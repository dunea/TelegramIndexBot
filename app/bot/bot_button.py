import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext

from app import services
from app.bot import bot_utils
from app.core.logger import logger
from app.core.di import di


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()


# 搜索分页翻页
async def search_page_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    reply_to_message_text = bot_utils.get_reply_to_message_text(update)
    if reply_to_message_text is None:
        await query.answer()
        return
    
    search_paging = bot_utils.query_data_get_search_paging(query.data)
    next_page = search_paging.page
    index_svc = di.get(services.IndexService)
    search_res = index_svc.search_index(reply_to_message_text, _type=search_paging.type, page=next_page)
    if len(search_res.list) <= 0:
        await context.bot.answer_callback_query(query.id, "没有下一页了~")
        await query.answer()
        return
    
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
    reply_to_message_text = bot_utils.get_reply_to_message_text(update)
    if reply_to_message_text is None:
        await query.answer()
        return
    
    index_svc = di.get(services.IndexService)
    search_type = bot_utils.query_data_get_search_type(query.data)
    if search_type.page == 1 and search_type.current is True:
        await context.bot.answer_callback_query(query.id, "当前已是此类型")
        await query.answer()
        return
    
    search_res = index_svc.search_index(reply_to_message_text, _type=search_type.type)
    if len(search_res.list) <= 0:
        logger.warning(" ".join([
            f"用户 [{update.effective_chat.id}] 搜索词 [{reply_to_message_text}]",
            f"类型 [{'all' if search_type.type is None else search_type.type.value}] 结果为空"
        ]))
        await context.bot.answer_callback_query(query.id, "此类型搜索结果为空")
        await query.answer()
        return
    
    await update.callback_query.edit_message_text(
        text=bot_utils.search_index_list_to_text(search_res),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            bot_utils.search_type_button_line(1, search_type.type),
            bot_utils.search_paging_button_line(search_res.page, search_res.next, search_type.type)
        ]),
        disable_web_page_preview=True,
    )
