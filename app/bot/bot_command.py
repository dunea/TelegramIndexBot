from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app import services
from app.core.di import di


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


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or context.args[0].startswith("https://t.me/") is False:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="\r\n".join([
                "请输入群组、频道或机器人的链接，不支持外部链接，命令示例如下。",
                "",
                "/add 要收录的公开链接 (必须为https://t.me/开头，可以从群组信息里获取公开链接)",
                "/add https://t.me/mes_index_bot",
                "",
                "如您有任何问题或建议，请联系管理员！ @nuoyea"
            ])
        )
        return
    
    # 提交链接
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="收录中 ≈ 10秒，收录成功后会给您发送通知！",
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )
    
    index_svc = di.get(services.IndexService)
    try:
        tme_index = index_svc.add_index_tme_link_by_user(update.message.text, update.message.from_user.id)
    except Exception as e:
        # 收录失败通知
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"收录失败: {e}",
            parse_mode=ParseMode.HTML,
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True,
        )
        return
    
    # 收录成功通知
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\r\n".join([
            "恭喜，您的链接已经收录成功啦！",
            "",
            f"<strong>标题:</strong> {tme_index.nickname}",
            f"<strong>链接:</strong> https://t.me/{tme_index.username}",
            f"<strong>描述:</strong> {tme_index.desc if tme_index.desc else '没有描述'}",
            f"<strong>收录时间:</strong> {tme_index.create_at}",
            "",
            "如您有任何问题或建议，请联系志愿者！ @nuoyea"
        ]),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        disable_web_page_preview=True,
    )
