import re
from dataclasses import dataclass
from typing import Optional, Match

import emoji
from telegram import InlineKeyboardButton, Update

from app import schemas, models, services
from app.core.di import di

CONTACT_ADMIN_MESSAGE = "如您有任何问题或建议，请联系管理员！ @nuoyea"
CLICK_OWN_SEARCH_MESSAGE = "您仅能点击自己的搜索"


# 根据字节数截取字符串，确保不截断多字节字符
def truncate_string_by_bytes(s, max_bytes):
    """
    根据字节数截取字符串，确保不截断多字节字符
    :param s: 输入的字符串
    :param max_bytes: 最大允许的字节数
    :return: 截取后的字符串
    """
    # 将字符串编码为字节对象
    encoded = s.encode('utf-8')
    # 按照指定字节数截取字节对象
    truncated = encoded[:max_bytes]
    try:
        # 尝试解码截取后的字节对象
        return truncated.decode('utf-8')
    except UnicodeDecodeError:
        # 如果解码失败，逐步减少字节数直到能正确解码
        while truncated:
            truncated = truncated[:-1]
            try:
                return truncated.decode('utf-8')
            except UnicodeDecodeError:
                continue
    return ''


# 简化字符串
def simplify_string(value: str) -> str:
    # 欧美福利丨口交丨后入丨内射丨大.. 1k (https://t.me/oumeifuli8)
    # 熟女/乱伦/3P/口交/换妻/.. 7k (https://t.me/shenye_fuli)
    #  【后入口交】口交/口爆/吞精/.. 1k (https://t.me/hourukoujiaoo)
    # 深喉~口交~吞精  6k (https://t.me/shenhoukoujia)
    # ●高中生口交●人兽内射 0.6k (https://t.me/jingping2025)
    # 蓝精灵（鉴赏视频）口交 5k (https://t.me/eyxjsjsn)
    # SM-吞精〓口交 颜射 13k
    # 人兽国产资源█露脸口交 6k (https://t.me/avhssp)
    #   ｜自拍｜欧美｜日本｜大.. 2k (https://t.me/ggaoqianj)
    # 口爆|肛交|贱狗|骚屄|绿茶 1k (https://t.me/caolvchabiaob)
    # 口袋收益、易富收益跑分 1k (https://t.me/koudaishouyi)
    # 球球：重口味專區 0.2k (https://t.me/kiss520u)
    # 〖莱克搭建〗海外各类盘口 22k (https://t.me/laike999999)
    # 『华乐』鉴黄偷拍自拍乱伦.. 21k (https://t.me/fhxy888)
    # 猎奇│人兽│吃屎│变态│.. 2k (https://t.me/renshou321)
    # 明星综合社区：明星生图AI.. 16k (https://t.me/mingxingst)
    # 爱奇艺?干嫩逼|口爆|互舔|.. 0.4k (https://t.me/owmomKKKK)
    # YY担保·灰产项目交流群[盘.. 35k (https://t.me/yyyy0)
    # 出海项目「总部」海外盘口.. 0.3k (https://t.me/CHLM9527)
    # 空降炮台3.0️盘口交流群 15k (https://t.me/xwmwx)
    
    replace_kv = [
        ("丨", "|"), ("【", "["), ("】", "]"), ("~", " "), ("●", " "), ("（", "("),
        ("）", ")"), ("〓", " "), ("█", " "), ("、", ","), ("，", ","), ("。", "."),
        ("？", "?"), ("！", "!"), ("！", "!"), ("｜", "|"), (" ", " "), ("：", ":"),
        ("；", ";"), ("#", ","), ("《", "("), ("》", ")"), ("——", "-"), ("[]", " "),
        ("()", " "), ("<>", " "), ("{}", " "), ("〖", "["), ("〗", "]"), ("『", "["),
        ("』", "]"), ("│", "|"), ("<", "("), (">", ")"), ("·", ","), ("「", "["),
        ("」", "]"), ("0️", "0")
    ]
    
    for _ in range(2):
        for kv in replace_kv:
            if value.find(kv[0]) != -1:
                value = value.replace(kv[0], kv[1])
    
    # 先删除字符串首尾的空格
    value = value.strip()
    
    # 把连续的空格替换成 1 个空格
    value = re.sub(r' +', ' ', value)
    
    # 把连续的符号替换成 1 个符号，这里符号定义为非字母数字和非空格的字符
    value = re.sub(r'([^\w\s])\1+', r'\1', value)
    
    # 匹配所有不可见字符（空白字符和控制字符）
    pattern = re.compile(r'[\s\x00-\x1F\x7F]')
    
    # 将匹配到的不可见字符替换为空字符串
    value = pattern.sub('', value)
    
    return value.lower()


# 简化昵称
def simplify_nickname(nickname: str, max_len=43) -> str:
    # 删除emoji
    nickname_ = _remove_emoji(nickname)
    
    # 简化字符串
    nickname_ = simplify_string(nickname_)
    
    if len(nickname_) <= 0:
        return nickname
    
    nickname = nickname_
    
    if len(nickname.encode('utf-8')) <= max_len:
        return nickname
    
    max_len = max_len - len("..".encode('utf-8'))
    
    if len(nickname.encode('utf-8')) > max_len:
        truncate_nickname = truncate_string_by_bytes(nickname, max_len)
        if len(truncate_nickname) <= 0:
            return nickname
        return f"{truncate_nickname}.."
    
    return nickname


# 搜索结果列表转文字
def search_index_list_to_text(index_list: schemas.TmeIndexBaseList, page=1, limit=20) -> Optional[str]:
    """
    schemas.TmeIndexBaseList 转机器人响应的字符串消息
    类型图标 📢👥📝👤🤖
    """
    reply_messages: list[str] = []
    start_index = (page - 1) * limit
    
    # 数字对其
    index_numbers = [(page - 1) * limit + i + 1 for i in range(len(index_list.list))]
    # 找出最长数字的长度
    max_length = max(len(str(num)) for num in index_numbers)
    
    start_index = 0
    
    # 构造列表
    for index in index_list.list:
        start_index += 1
        # 使用空格补齐左边长度
        # padded_num = str(start_index).zfill(max_length)
        padded_num = str(start_index)
        
        # 行内消息
        message = []
        if index.type == models.TmeIndexType.GROUP:
            # message.append(f"<i>{padded_num}.</i>👥")
            message.append(f"👥")
        elif index.type == models.TmeIndexType.CHANNEL:
            # message.append(f"<i>{padded_num}.</i>📢")
            message.append(f"📢")
        elif index.type == models.TmeIndexType.BOT:
            # message.append(f"<i>{padded_num}.</i>🤖")
            message.append(f"🤖")
        else:
            continue
        
        # 群组、频道人数
        count_members = ""
        if index.count_members > 0:
            count_members = f" {_format_number(index.count_members)}"
        
        # 跳转链接
        title = simplify_nickname(index.nickname)
        message.append(f"<a href='https://t.me/{index.username}'>{title}{count_members}</a>")
        reply_messages.append(" ".join(message))
    
    # 页码
    reply_messages.append(f"<i>[第 {page} 页 / {len(index_list.list)} 条]</i>")
    
    return "\r\n".join(reply_messages) if len(reply_messages) > 0 else None


# 获取搜索分页按钮行
def search_paging_button_line(page: int, _next: bool, _type: models.TmeIndexType = None) -> list[InlineKeyboardButton]:
    button_list: list[InlineKeyboardButton] = []
    button_type = "all" if _type is None else _type.value
    
    if page <= 1:
        item = InlineKeyboardButton("购买广告", url="https://t.me/nuoyea")
        button_list.append(item)
    else:
        item = InlineKeyboardButton("上一页", callback_data=f"search_paging:{button_type}:{page - 1}")
        button_list.append(item)
    if _next is True:
        item = InlineKeyboardButton("下一页", callback_data=f"search_paging:{button_type}:{page + 1}")
        button_list.append(item)
    
    return button_list


# 获取搜索类型按钮行
def search_type_button_line(page: int, _type: models.TmeIndexType = None) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            "全部",
            callback_data=f"search_type:all:{page}{':current' if _type is None else ''}"
        ),
        InlineKeyboardButton(
            "📢",
            callback_data=f"search_type:{models.TmeIndexType.CHANNEL.value}:{page}{':current' if _type == models.TmeIndexType.CHANNEL else ''}"
        ),
        InlineKeyboardButton(
            "👥",
            callback_data=f"search_type:{models.TmeIndexType.GROUP.value}:{page}{':current' if _type == models.TmeIndexType.GROUP else ''}"
        ),
        InlineKeyboardButton(
            "🤖",
            callback_data=f"search_type:{models.TmeIndexType.BOT.value}:{page}{':current' if _type == models.TmeIndexType.BOT else ''}"
        ),
    ]


@dataclass
class QuerySearchType:
    type: models.TmeIndexType | None
    page: int
    current: bool


# 获取查询数据搜索类型
def query_data_get_search_type(query: str | None) -> QuerySearchType:
    if query is None:
        return QuerySearchType(type=None, page=1, current=False)
    
    query_type = []
    pattern = r'search_type:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)(?::([a-zA-Z0-9]+))?'
    match = re.search(pattern, query)
    if match:
        query_type.append(match.group(1))
        query_type.append(match.group(2))
        if match.group(3):
            query_type.append(match.group(3))
    
    if query_type[0] == models.TmeIndexType.CHANNEL.value:
        return QuerySearchType(type=models.TmeIndexType.CHANNEL, page=int(query_type[1]), current=len(query_type) == 3)
    elif query_type[0] == models.TmeIndexType.GROUP.value:
        return QuerySearchType(type=models.TmeIndexType.GROUP, page=int(query_type[1]), current=len(query_type) == 3)
    elif query_type[0] == models.TmeIndexType.BOT.value:
        return QuerySearchType(type=models.TmeIndexType.BOT, page=int(query_type[1]), current=len(query_type) == 3)
    else:
        return QuerySearchType(type=None, page=int(query_type[1]), current=len(query_type) == 3)


@dataclass
class QuerySearchPaging:
    type: models.TmeIndexType | None
    page: int


# 获取查询数据搜索分页
def query_data_get_search_paging(query: str | None) -> QuerySearchPaging:
    if query is None:
        return QuerySearchPaging(type=None, page=1)
    
    query_type = []
    pattern = r'search_paging:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)'
    match = re.search(pattern, query)
    if match:
        query_type.append(match.group(1))
        query_type.append(match.group(2))
    
    if query_type[0] == models.TmeIndexType.CHANNEL.value:
        return QuerySearchPaging(type=models.TmeIndexType.CHANNEL, page=int(query_type[1]))
    elif query_type[0] == models.TmeIndexType.GROUP.value:
        return QuerySearchPaging(type=models.TmeIndexType.GROUP, page=int(query_type[1]))
    elif query_type[0] == models.TmeIndexType.BOT.value:
        return QuerySearchPaging(type=models.TmeIndexType.BOT, page=int(query_type[1]))
    else:
        return QuerySearchPaging(type=None, page=int(query_type[1]))


# 索引转索引按钮列表
def index_to_button_list(index_list: schemas.TmeIndexBaseList):
    reply_markup = []
    query_data_svc = di.get(services.QueryDataService)
    try:
        i = (index_list.page - 1) * index_list.limit
        for index in index_list.list:
            i += 1
            query_data = query_data_svc.set_query_parameter(
                {"index_id": index.id, "index_username": index.username, "page": index_list.page})
            reply_markup.append([InlineKeyboardButton(
                f"{index.nickname}",
                callback_data=f"query_index:{query_data.id}"
            )])
        
        # 分页按钮
        if index_list.next is True or index_list.page > 1:
            paging_button_line = []
            if index_list.page > 1:
                query_data = query_data_svc.set_query_parameter({"page": index_list.page - 1})
                paging_button_line.append(
                    InlineKeyboardButton(f"上一页", callback_data=f"query_page:{query_data.id}")
                )
            if index_list.next is True:
                query_data = query_data_svc.set_query_parameter({"page": index_list.page + 1})
                paging_button_line.append(
                    InlineKeyboardButton(f"下一页", callback_data=f"query_page:{query_data.id}")
                )
            reply_markup.append(paging_button_line)
    except Exception as e:
        raise e
    
    return reply_markup


# 按钮query_data获取uuid
def query_data_get_uuid(query_data: str) -> str:
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    try:
        match = re.search(uuid_pattern, query_data)
        if match:
            return match.group()
        raise Exception("未找到有效按钮ID")
    except:
        raise Exception("获取按钮ID发生错误")


# 格式化数字
def _format_number(number: int) -> str:
    """
    格式化数字
    :param number:
    :return:
    """
    if number <= 100:
        return "0k"
    elif number < 1000:
        k_value: float = number / 1000
        return f"{round(k_value, 1)}k"
    else:
        k_value: int = number // 1000
        return f"{k_value}k"


# 删除字符串中的emoji标签
def _remove_emoji(text: str) -> str:
    result = ""
    for char in text:
        if not emoji.is_emoji(char):
            result += char
        else:
            result += " "
    return result
