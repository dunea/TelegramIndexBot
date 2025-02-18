from typing import Optional, Match

from app import schemas, models


def tem_index_base_list_to_text(index_list: schemas.TmeIndexBaseList) -> Optional[str]:
    """
    schemas.TmeIndexBaseList 转机器人响应的字符串消息
    类型图标 📢👥📝👤🤖
    :param index_list:
    :return:
    """
    reply_messages: list[str] = []
    start_index = 0
    
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
        if index.count_members > 100:
            count_members = f" {_format_number(index.count_members)}"
        
        message.extend(f"<a href='https://t.me/{index.username}'>{index.nickname[:12]}{count_members}</a>")
        reply_messages.append(" ".join(message))
    
    return "\r\n".join(reply_messages) if len(reply_messages) > 0 else None


def _format_number(number: int) -> str:
    """
    格式化数字
    :param number:
    :return:
    """
    if number < 100:
        return str(number)
    elif number < 1000:
        k_value: float = number // 1000.0
        return f"{round(k_value, 1)}k"
    else:
        k_value: int = number // 1000
        return f"{k_value}k"
