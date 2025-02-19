import re
from dataclasses import dataclass
from typing import Optional, Match

from telegram import InlineKeyboardButton, Update

from app import schemas, models


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
        message = [f"{start_index}."]
        if index.type == models.TmeIndexType.GROUP:
            message.append("👥")
        elif index.type == models.TmeIndexType.CHANNEL:
            message.append("📢")
        elif index.type == models.TmeIndexType.BOT:
            message.append("🤖")
        else:
            continue
        
        count_members = ""
        if index.count_members > 0:
            count_members = f" {_format_number(index.count_members)}"
        
        title = index.nickname[:12] if len(index.nickname) > 12 else index.nickname
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
        return QuerySearchType(type=None, page=1, current=len(query_type) == 3)


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


# 获取消息中的回复消息文字内容
def get_reply_to_message_text(update: Update) -> str | None:
    try:
        return update.callback_query.message.to_dict()["reply_to_message"]["text"]
    except:
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
