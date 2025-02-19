from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app import services, models
from app.bot import bot_utils
from app.core.logger import logger
from app.core.di import di


# 搜索索引
async def search_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot:
        return
    if len(update.message.text) > 10:
        await _send_search_keyword_range_error(update, context)
        return
    
    index_svc = di.get(services.IndexService)
    search_res = index_svc.search_index(update.message.text)
    if len(search_res.list) <= 0:
        logger.warning(f"用户 [{update.effective_chat.id}] 搜索词 [{update.message.text}] 结果为空")
        await _send_search_no_result(update, context)
        return
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=bot_utils.search_index_list_to_text(search_res),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            bot_utils.search_type_button_line(1),
            bot_utils.search_paging_button_line(search_res.page, search_res.next)
        ]),
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )


# 搜索没有找到相关结果
async def _send_search_no_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="没有找到相关结果",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )


# 搜索词2-10字之间
async def _send_search_keyword_range_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="搜索词请在2-10字之间",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )


# 搜索词无效
async def _send_search_word_invalid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="搜索词无效",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )
