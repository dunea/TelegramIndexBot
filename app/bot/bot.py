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
        self.add_message_group()
        self.add_command_group()
        self.add_button_group()
        
        # 设置对话处理器，包含 FIRST 和 SECOND 状态
        # 使用 pattern 参数将具有特定数据模式的 CallbackQueries
        # 传递给相应的处理器。
        # ^ 表示 "行/字符串的开始"
        # $ 表示 "行/字符串的结束"
        # 所以 ^ABC$ 只会匹配 'ABC'
        # conv_handler = ConversationHandler(
        #     entry_points=[],
        #     states={
        #         START_ROUTES: [],
        #         END_ROUTES: [],
        #     },
        #     fallbacks=[CommandHandler("start", bot_command.start)],
        # )
        
        # 将ConversationHandler添加到用于处理更新的应用程序中
        # self.application.add_handler(conv_handler)
    
    def run_polling(self):
        self.application.run_polling(poll_interval=0.1, allowed_updates=Update.ALL_TYPES)
    
    def add_command_group(self):
        self.application.add_handler(CommandHandler('start', bot_command.start))
    
    def add_message_group(self):
        self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), bot_message.search_index))
    
    def add_button_group(self):
        self.application.add_handler(
            CallbackQueryHandler(
                bot_button.search_page_switch,
                pattern=r'^search_paging:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)$',
                block=True
            )
        )
        self.application.add_handler(
            CallbackQueryHandler(
                bot_button.search_type_switch,
                pattern=r'^search_type:([a-zA-Z0-9]{1,20}):(100|[1-9][0-9]?)(?::[a-zA-Z0-9]+)?$',
                block=True
            )
        )
        self.application.add_handler(CallbackQueryHandler(bot_button.button, block=True))
