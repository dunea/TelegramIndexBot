import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.bot import bot_commands
from app.core import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


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
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
        self.application.add_handler(echo_handler)
