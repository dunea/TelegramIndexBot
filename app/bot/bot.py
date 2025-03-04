import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler

from app.bot import bot_command, bot_message, bot_button

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# 为httpx设置更高的日志级别，以避免记录所有GET和POST请求
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Stages
# START_ROUTES, END_ROUTES = range(0)
# Callback data
# ONE, TWO, THREE, FOUR = range(0)


class Bot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.application.add_handlers(
            handlers={
                # 命令
                -1: [
                    CommandHandler('start', bot_command.start, block=False),
                    CommandHandler('add', bot_command.add, block=False),
                    CommandHandler('query', bot_command.query, block=False)
                ],
                # 按钮
                1: [
                    CallbackQueryHandler(
                        bot_button.search_page_switch, block=False,
                        pattern='^search_paging:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)$',
                    ),
                    CallbackQueryHandler(
                        bot_button.search_type_switch, block=False,
                        pattern=r'^search_type:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)(?::[a-zA-Z0-9]+)?$',
                    ),
                    CallbackQueryHandler(
                        bot_button.query_index, block=False,
                        pattern=r'^query_index:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
                    ),
                    CallbackQueryHandler(
                        bot_button.query_page, block=False,
                        pattern=r'^query_page:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
                    ),
                    CallbackQueryHandler(
                        bot_button.index_update, block=False,
                        pattern=r'^index_update:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
                    ),
                    CallbackQueryHandler(
                        bot_button.index_delete, block=False,
                        pattern=r'^index_delete:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
                    ),
                    CallbackQueryHandler(
                        bot_button.index_delete_confirm, block=False,
                        pattern=r'^index_delete_confirm:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
                    )
                ],
                # 消息
                2: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND & ~filters.Document.ALL & ~filters.Regex(
                            r'http[s]?://') & ~filters.REPLY,
                        bot_message.search_index
                    )
                ]
            }
        )
