import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode
from datetime import time, timedelta, timezone

# ================= CONFIG =================
TOKEN = "8456080157:AAEDzw_1drRIx_nxvgTAalBS1Fz1OVJ-aT4"
CHANNEL_ID = -1003962354146
ADMIN_IDS = [7060111888]

WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://telegram-bot-z8zl.onrender.com"

logging.basicConfig(level=logging.INFO)

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # save user id
    with open("user_ids.txt", "a") as f:
        f.write(f"{chat_id}\n")

    # welcome image
    try:
        with open("welcome.png", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption="Welcome to VictorBet💎👇"
            )
    except:
        await update.message.reply_text("Welcome to VictorBet💎👇")

    keyboard = [
        [InlineKeyboardButton("📝 Register", url="https://www.victorbet.me/download/url?referral=3FLEBW")],
        [InlineKeyboardButton("🎮 Play Now", url="https://www.victorbet.me")],
        [InlineKeyboardButton("🚀 Channel", url="https://t.me/VTB33_Channel")],
        [InlineKeyboardButton("📲 Contact us", callback_data="contact_us")]
    ]

    await update.message.reply_text(
        "Select option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "contact_us":
        await query.message.reply_text(
            "💬 Contact CS:\nhttps://direct.lc.chat/14684676/"
        )


async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "hi boss" in text or "daftar" in text:
        await update.message.reply_text(
            "👇 Register link:\nhttps://www.victorbet.me/download/url?referral=3FLEBW\n"
            "💬 CS: https://direct.lc.chat/14684676/"
        )
    elif "livechat" in text:
        await update.message.reply_text("💬 CS: https://direct.lc.chat/14684676/")
    else:
        await update.message.reply_text("👇 https://www.victorbet.me")


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Welcome {member.full_name} 🎉"
        )


async def scheduled_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))

        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text="📢 Daily Bonus Alert: Topup now & WIN BIG!"
                )
            except Exception as e:
                logging.warning(f"Failed {user_id}: {e}")

    except FileNotFoundError:
        logging.warning("user_ids.txt not found")


async def handle_media_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 No permission.")
        return

    caption = update.message.caption or "🎬 Latest Promo"

    keyboard = [
        [
            InlineKeyboardButton("📝 Register", url="https://www.victorbet.me/download/url?referral=3FLEBW"),
            InlineKeyboardButton("🎮 Play", url="https://www.victorbet.me")
        ],
        [
            InlineKeyboardButton("💬 Contact", url="https://direct.lc.chat/14684676/")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await context.bot.send_photo(CHANNEL_ID, file_id, caption=caption, reply_markup=reply_markup)

    elif update.message.video:
        file_id = update.message.video.file_id
        await context.bot.send_video(CHANNEL_ID, file_id, caption=caption, reply_markup=reply_markup)

    await update.message.reply_text("✅ Posted to channel!")


# ================= MAIN =================

def main():
    malaysia = timezone(timedelta(hours=8))

    app = ApplicationBuilder().token(TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media_post))

    # job queue (IMPORTANT FIX)
    app.job_queue.run_daily(
        scheduled_message,
        time=time(17, 0, tzinfo=malaysia)
    )

    # webhook (Render only)
    webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
    print(f"🚀 Webhook running: {webhook_url}")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    main()
