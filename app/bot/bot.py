import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.bot import bot_commands, bot_messages
from app.core import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Bot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.commands()
        self.messages()
    
    def run_polling(self):
        self.application.run_polling()
    
    def commands(self):
        start_handler = CommandHandler('start', bot_commands.start)
        self.application.add_handler(start_handler)
    
    def messages(self):
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), bot_messages.echo)
        self.application.add_handler(echo_handler)
