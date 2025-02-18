from app.bot import Bot
from app.core.settings import settings

if __name__ == '__main__':
    Bot(settings.BOT_TOKEN).run_polling()
    pass
