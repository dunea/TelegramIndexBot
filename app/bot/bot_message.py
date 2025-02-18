from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app import services, models
from app.bot import bot_utils
from app.core.di import di


async def search_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index_svc = di.get(services.IndexService)
    tme_index_list = index_svc.search_index(update.message.text, models.TmeIndexType)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=bot_utils.tem_index_base_list_to_text(tme_index_list),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.reply_to_message.message_id,
    )
