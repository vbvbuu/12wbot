import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler
)
from telegram.constants import ParseMode
from datetime import time, timedelta, timezone
import logging

TOKEN = "8456080157:AAEDzw_1drRIx_nxvgTAalBS1Fz1OVJ-aT4"
CHANNEL_ID = -1003962354146  # 你的频道 ID
ADMIN_IDS = [7060111888]  # 允许发 rich post 的用户 Telegram ID

WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 5000))
BASE_URL = "https://telegram-bot-z8zl.onrender.com"  # 你的域名

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")

    with open("welcome.png", "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption="Welcome to VictorBet💎👇")

    keyboard = [
        [InlineKeyboardButton("📝 Register", url="https://www.victorbet.me/download/url?referral=3FLEBW")],
        [InlineKeyboardButton("🎮 play now", url="https://www.victorbet.me")],
        [InlineKeyboardButton("🚀 New Telegram Channel", url="https://t.me/VTB33_Channel")],
        [InlineKeyboardButton("📲 Contact us", callback_data="contact_us")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select option at below：", reply_markup=reply_markup)

async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "contact_us":
        await query.message.reply_text("💬 Tekan link utk chat CS: \nhttps://direct.lc.chat/14684676/")

async def keyword_reply(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()
    if "hi boss" in text or "daftar" in text:
        await update.message.reply_text("👇 Tekan link bawah utk register ya:\nhttps://www.victorbet.me/download/url?referral=3FLEBW\n💬 Chat CS: \nhttps://direct.lc.chat/14684676/")
    elif "livechat" in text:
        await update.message.reply_text("💬 Chat CS: \nhttps://direct.lc.chat/14684676/")
    else:
        await update.message.reply_text("👇 Register link:\nhttps://www.victorbet.me/download/url?referral=3FLEBW\n💬 Chat CS: \nhttps://direct.lc.chat/14684676/")

async def welcome_new_member(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.full_name} Join group！🎉")

async def scheduled_message(context: CallbackContext):
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text="📢 VictorBet Daily notification：Topup skrg n BIGWIN！")
            except Exception as e:
                print(f"发送给 {user_id} 失败：{e}")
    except FileNotFoundError:
        print("没有 user_ids.txt 文件")

# ✅ Rich post 支持图片或视频（来自管理员）
async def handle_media_post(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 你没有权限发布到频道。")
        return

    caption = update.message.caption or "🎬 VictorBet 最新优惠"

    keyboard = [
        [
            InlineKeyboardButton("📝 Register", url="https://www.victorbet.me/download/url?referral=3FLEBW"),
            InlineKeyboardButton("🎮 play now", url="https://www.victorbet.me")
        ],
        [
            InlineKeyboardButton("📢 VTBmy_bot", url="https://t.me/VTBmy_bot"),
            InlineKeyboardButton("💬 Contact us", url="https://direct.lc.chat/14684676/")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=caption, reply_markup=reply_markup)
    elif update.message.video:
        file_id = update.message.video.file_id
        await context.bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=caption, reply_markup=reply_markup)
    else:
        await update.message.reply_text("❗ 请发送图片或视频 + 文案")

    await update.message.reply_text("✅ 已发布到频道！")

def main():
    malaysia = timezone(timedelta(hours=8))
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media_post))

    job_queue = app.job_queue
    job_queue.run_daily(scheduled_message, time=time(17, 0, tzinfo=malaysia))
    job_queue.start()

    if os.environ.get("RENDER"):
        webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
        print(f"🚀 Starting webhook with URL: {webhook_url} on port {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=WEBHOOK_PATH,
            webhook_url=webhook_url,
        )
    else:
        print("🖥️ Running in polling mode")
        app.run_polling()

if __name__ == "__main__":
    main()