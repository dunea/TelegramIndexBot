import re
from dataclasses import dataclass
from typing import Optional, Match

import emoji
from telegram import InlineKeyboardButton, Update

from app import schemas, models, services
from app.core.di import di

CONTACT_ADMIN_MESSAGE = "如您有任何问题或建议，请联系管理员！ @nuoyea"
CLICK_OWN_SEARCH_MESSAGE = "您仅能点击自己的搜索"


# 搜索结果列表转文字
def search_index_list_to_text(index_list: schemas.TmeIndexBaseList, page=1, limit=20) -> Optional[str]:
    """
    schemas.TmeIndexBaseList 转机器人响应的字符串消息
    类型图标 📢👥📝👤🤖
    """
    reply_messages: list[str] = []
    start_index = (page - 1) * limit
    
    for index in index_list.list:
        start_index += 1
        message = []
        if index.type == models.TmeIndexType.GROUP:
            message.append(f"{start_index}.👥")
        elif index.type == models.TmeIndexType.CHANNEL:
            message.append(f"{start_index}.📢")
        elif index.type == models.TmeIndexType.BOT:
            message.append(f"{start_index}.🤖")
        else:
            continue
        
        count_members = ""
        if index.count_members > 0:
            count_members = f" {_format_number(index.count_members)}"
        
        title = f"{_remove_emoji(index.nickname)[:10]}.." if len(_remove_emoji(index.nickname)) > 10 else _remove_emoji(
            index.nickname)
        message.append(f"<a href='https://t.me/{index.username}'>{title}{count_members}</a>")
        reply_messages.append(" ".join(message))
    
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
            query_data = query_data_svc.set_query_parameter({"index_id": index.id, "page": index_list.page})
            reply_markup.append([InlineKeyboardButton(
                f"{i}. {index.nickname}",
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


@dataclass
class QueryIndexParameter:
    index_id: str
    page: int


# query_index按钮获取索引参数
def query_index_button_get_parameter(query_data: str) -> QueryIndexParameter | None:
    # 正则表达式匹配UUID
    uuid_pattern = r'^query_index:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}):(100|[1-9][0-9]?)$'
    
    try:
        match = re.search(uuid_pattern, query_data)
        if match:
            return QueryIndexParameter(
                index_id=match.group(1),
                page=int(match.group(2)),
            )
    except:
        pass
    
    return None


# query_page按钮获取页码
def query_page_button_get_page(query_data: str) -> int | None:
    # 正则表达式匹配UUID
    uuid_pattern = r'^query_page:(100|[1-9][0-9]?)$'
    
    try:
        match = re.search(uuid_pattern, query_data)
        if match:
            return int(match.group(1))
    except:
        pass
    
    return None


# index_update按钮获取参数
def index_update_button_get_parameter(query_data: str) -> QueryIndexParameter | None:
    # 正则表达式匹配UUID
    uuid_pattern = r'^index_update:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}):(100|[1-9][0-9]?)$'
    
    try:
        match = re.search(uuid_pattern, query_data)
        if match:
            return QueryIndexParameter(
                index_id=match.group(1),
                page=int(match.group(2)),
            )
    except:
        pass
    
    return None


# index_delete按钮获取参数
def index_delete_button_get_parameter(query_data: str) -> QueryIndexParameter | None:
    # 正则表达式匹配UUID
    uuid_pattern = r'^index_delete:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}):(100|[1-9][0-9]?)$'
    
    try:
        match = re.search(uuid_pattern, query_data)
        if match:
            return QueryIndexParameter(
                index_id=match.group(1),
                page=int(match.group(2)),
            )
    except:
        pass
    
    return None


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


def _remove_emoji(text: str) -> str:
    result = ""
    for char in text:
        if not emoji.is_emoji(char):
            result += char
        else:
            result += " "
    return result
