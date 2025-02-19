from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\r\n".join([
            "欢迎您使用Mesy免费智能索引机器人 @mes_index_bot，基于Telegram最专业且智能的免费索引机器人，发送关键词来查询您感兴趣的群组和频道。",
            "",
            "/start - 开始使用",
            "/add - 添加收录",
            "/query - 我的收录",
            "/ad - 广告联盟",
        ])
    )
