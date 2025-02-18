import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.bot import bot_command, bot_message

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Bot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.add_command_group()
        self.add_message_group()
    
    def run_polling(self):
        self.application.run_polling()
    
    def add_command_group(self):
        start_handler = CommandHandler('start', bot_command.start)
        self.application.add_handler(start_handler)
    
    def add_message_group(self):
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), bot_message.echo)
        self.application.add_handler(echo_handler)
