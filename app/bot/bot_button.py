import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext

from app import services, models
from app.bot import bot_utils
from app.core.logger import logger
from app.core.di import di


# 搜索分页翻页
async def search_page_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    reply_to_message_text: str | None = query.message.to_dict()["reply_to_message"]["text"]
    if reply_to_message_text is False:
        await context.bot.answer_callback_query(query.id, "获取查询参数发生错误")
        await query.answer()
        return
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return
    
    # 搜索
    search_paging = bot_utils.query_data_get_search_paging(query.data)
    next_page = search_paging.page
    index_svc = di.get(services.IndexService)
    try:
        search_res = index_svc.search_index(reply_to_message_text, _type=search_paging.type, page=next_page)
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    if len(search_res.list) <= 0:
        await context.bot.answer_callback_query(query.id, "没有下一页了")
        current_page = next_page - 1 if next_page > 2 else 1
        await update.callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                bot_utils.search_type_button_line(current_page, search_paging.type),
                bot_utils.search_paging_button_line(current_page, False, search_paging.type)
            ]),
        )
        return
    
    # 发送结果
    await update.callback_query.edit_message_text(
        text=bot_utils.search_index_list_to_text(search_res, page=search_res.page),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            bot_utils.search_type_button_line(next_page, search_paging.type),
            bot_utils.search_paging_button_line(search_res.page, search_res.next, search_paging.type)
        ]),
        disable_web_page_preview=True,
    )


# 搜索类型切换
async def search_type_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    reply_to_message_text: str | None = query.message.to_dict()["reply_to_message"]["text"]
    if reply_to_message_text is None:
        await context.bot.answer_callback_query(query.id, "获取查询参数发生错误")
        await query.answer()
        return
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return
    
    # 搜索类型检查
    index_svc = di.get(services.IndexService)
    search_type = bot_utils.query_data_get_search_type(query.data)
    if search_type.page == 1 and search_type.current is True:
        await context.bot.answer_callback_query(query.id, "当前已是此类型")
        await query.answer()
        return
    
    # 搜索
    try:
        search_res = index_svc.search_index(reply_to_message_text, _type=search_type.type)
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    if len(search_res.list) <= 0:
        logger.warning(" ".join([
            f"用户 [{update.effective_chat.id}] 搜索词 [{reply_to_message_text}]",
            f"类型 [{'all' if search_type.type is None else search_type.type.value}] 结果为空"
        ]))
        await context.bot.answer_callback_query(query.id, "此类型搜索结果为空")
        await query.answer()
        return
    
    # 发送结果
    await update.callback_query.edit_message_text(
        text=bot_utils.search_index_list_to_text(search_res),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            bot_utils.search_type_button_line(1, search_type.type),
            bot_utils.search_paging_button_line(search_res.page, search_res.next, search_type.type)
        ]),
        disable_web_page_preview=True,
    )


# 查询索引信息
async def query_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data_svc = di.get(services.QueryDataService)
    try:
        query_data = query_data_svc.get_query_parameter(bot_utils.query_data_get_uuid(query.data))
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return
    
    # 获取index信息
    index_svc = di.get(services.IndexService)
    try:
        index = index_svc.query_index_by_id(query_data.parameter["index_id"])
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    if index is None:
        await context.bot.answer_callback_query(query.id, "查询的索引未被收录")
        await query.answer()
        return
    
    await update.callback_query.edit_message_text(
        text="\r\n".join([
            f"<strong>标题:</strong> {index.nickname}",
            f"<strong>链接:</strong> https://t.me/{index.username}",
            f"<strong>人数:</strong> {index.count_members}",
            f"<strong>描述:</strong> {index.desc if index.desc else '没有描述'}",
            f"<strong>收录时间:</strong> {index.create_at}",
            f"<strong>更新时间:</strong> {index.last_gather_at}",
            "",
            bot_utils.CONTACT_ADMIN_MESSAGE
        ]),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("更新", callback_data=f"index_update:{query_data.id}"),
                InlineKeyboardButton("删除", callback_data=f"index_delete:{query_data.id}"),
            ],
            [InlineKeyboardButton("<< 返回", callback_data=f"query_page:{query_data.id}")],
        ]),
        disable_web_page_preview=True,
    )


# 查收索引列表分页翻页
async def query_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data_svc = di.get(services.QueryDataService)
    try:
        query_data = query_data_svc.get_query_parameter(bot_utils.query_data_get_uuid(query.data))
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return
    
    index_svc = di.get(services.IndexService)
    try:
        index_list = index_svc.index_by_user_add(
            update.callback_query.message.chat.id,
            page=query_data.parameter["page"]
        )
    except Exception as e:
        # 查询失败通知
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    # 按钮组
    try:
        reply_markup = bot_utils.index_to_button_list(index_list)
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{e}",
            parse_mode=ParseMode.HTML,
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True,
        )
        return
    
    if len(index_list.list) == 0 and query_data.parameter["page"] == 1:
        await update.callback_query.edit_message_text(
            text="\r\n".join([
                "没有找到您收录的索引，请先收录索引后再查询！",
                "",
                bot_utils.CONTACT_ADMIN_MESSAGE
            ]),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return
    elif len(index_list.list) == 0:
        await update.callback_query.edit_message_text(
            text="当前页面数据为空，请继续返回上一页！",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(reply_markup),
            disable_web_page_preview=True,
        )
        return
    
    await update.callback_query.edit_message_text(
        text="您收录的索引如下:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(reply_markup),
        disable_web_page_preview=True,
    )


# 索引更新
async def index_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data_svc = di.get(services.QueryDataService)
    try:
        query_data = query_data_svc.get_query_parameter(bot_utils.query_data_get_uuid(query.data))
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return
    
    # 更新索引
    index_svc = di.get(services.IndexService)
    try:
        index = index_svc.update_index_by_id(query_data.parameter["index_id"])
    except Exception as e:
        # 查询失败通知
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return
    
    if index is None:
        await context.bot.answer_callback_query(query.id, "更新的索引未被收录")
        await query.answer()
        return
    
    await update.callback_query.edit_message_text(
        text="\r\n".join([
            f"<strong>标题:</strong> {index.nickname}",
            f"<strong>链接:</strong> https://t.me/{index.username}",
            f"<strong>人数:</strong> {index.count_members}",
            f"<strong>描述:</strong> {index.desc if index.desc else '没有描述'}",
            f"<strong>收录时间:</strong> {index.create_at}",
            f"<strong>更新时间:</strong> {index.last_gather_at}",
            "",
            bot_utils.CONTACT_ADMIN_MESSAGE
        ]),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("更新", callback_data=f"index_update:{query_data.id}"),
                InlineKeyboardButton("删除", callback_data=f"index_delete:{query_data.id}"),
            ],
            [InlineKeyboardButton("<< 返回", callback_data=f"query_page:{query_data.id}")],
        ]),
        disable_web_page_preview=True,
    )
    
    await context.bot.answer_callback_query(query.id, "更新索引信息成功")


# 索引删除
async def index_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    query_data_svc = di.get(services.QueryDataService)
    try:
        query_data = query_data_svc.get_query_parameter(bot_utils.query_data_get_uuid(query.data))
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return False
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE)
        await query.answer()
        return False
    
    # 获取index信息
    index_svc = di.get(services.IndexService)
    try:
        index = index_svc.query_index_by_id(query_data.parameter["index_id"])
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}")
        await query.answer()
        return False
    
    if index is None:
        await context.bot.answer_callback_query(query.id, "删除的索引未被收录")
        await query.answer()
        return False
    
    # 编辑消息
    await update.callback_query.edit_message_text(
        text="\r\n".join([
            f"<strong>标题:</strong> {index.nickname}",
            f"<strong>链接:</strong> https://t.me/{index.username}",
            f"<strong>人数:</strong> {index.count_members}",
            f"<strong>描述:</strong> {index.desc if index.desc else '没有描述'}",
            f"<strong>收录时间:</strong> {index.create_at}",
            f"<strong>更新时间:</strong> {index.last_gather_at}",
            "",
            "删除索引并不会把索引从引擎中删除，仅仅从你的查询列表中进行删除。",
            "如果你想索引不被引擎收录理应把群组设置为私密群。",
        ]),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("确认删除", callback_data=f"index_delete_confirm:{query_data.id}")],
            [InlineKeyboardButton("<< 返回", callback_data=f"query_index:{query_data.id}")],
        ]),
        disable_web_page_preview=True,
    )
    
    return True


# 索引删除确认
async def index_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    query_data_svc = di.get(services.QueryDataService)
    query_id = bot_utils.query_data_get_uuid(query.data)
    try:
        query_data = query_data_svc.get_query_parameter(query_id)
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}", show_alert=True)
        await query.answer()
        return False
    
    # 不是本人点击按钮
    if query.from_user.id != query.message.to_dict()["reply_to_message"]["from"]["id"]:
        await context.bot.answer_callback_query(query.id, bot_utils.CLICK_OWN_SEARCH_MESSAGE, show_alert=True)
        await query.answer()
        return False
    
    # 删除用户添加的索引
    index_svc = di.get(services.IndexService)
    try:
        index_svc.del_index_in_username_by_user(query_data.parameter["index_username"], query.from_user.id)
    except Exception as e:
        await context.bot.answer_callback_query(query.id, f"{e}", show_alert=True)
        await query.answer()
        return False
    
    await query_page(update, context)
    
    return True
