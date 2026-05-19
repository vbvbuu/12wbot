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
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_IDS = int(os.getenv("ADMIN_ID"))

WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://one2wbot.onrender.com"

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
                caption="Selamat datang 12WIN💋🔥"
            )
    except:
        await update.message.reply_text("Selamat datang 12WIN💋🔥")

    keyboard = [
        [InlineKeyboardButton("📩 Register", url="https://www.12win.online/refer/tlgbot")],
        [InlineKeyboardButton("🕹️ Play Now", url="https://www.12win.online")],
        [InlineKeyboardButton("🛎️ Channel", url="https://t.me/onetwowiin")],
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
            "💬 Contact CS:\nhttps://direct.lc.chat/19594218/"
        )


async def keyword_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "hi boss" in text or "daftar" in text:
        await update.message.reply_text(
            "💎 Register link:\nhttps://www.12win.online/refer/tlgbot\n"
            "📩 CS: https://direct.lc.chat/19594218/"
        )
    elif "livechat" in text:
        await update.message.reply_text("📩 CS: https://direct.lc.chat/19594218/")
    else:
        await update.message.reply_text("💎 https://www.12win.online")


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Welcome {member.full_name} 🎉"
        )


async def handle_media_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MEDIA HANDLER TRIGGERED")
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 No permission.")
        return

    caption = update.message.caption or "🧧 12WIN Latest Promo"

    keyboard = [
        [
            InlineKeyboardButton("🕹️ Register", url="https://www.12win.online/refer/tlgbot"),
            InlineKeyboardButton("💫 Spin", url="https://www.12win.online")
        ],
        [
            InlineKeyboardButton("💬 Contact", url="https://direct.lc.chat/19594218/")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = update.message

    try:
        # PHOTO
        if msg.photo:
            file_id = msg.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )

        # VIDEO
        elif msg.video:
            file_id = msg.video.file_id
            await context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=file_id,
                caption=caption,
                reply_markup=reply_markup
            )

        # GIF / ANIMATION ⭐ 关键修复
        elif msg.animation:
            file_id = msg.animation.file_id
            await context.bot.send_animation(
                chat_id=CHANNEL_ID,
                animation=file_id,
                caption=caption,
                reply_markup=reply_markup
            )

        # DOCUMENT video fallback ⭐ 很重要
        elif msg.document:
            file_id = msg.document.file_id
            await context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=file_id,
                caption=caption,
                reply_markup=reply_markup
            )

        else:
            await update.message.reply_text("❗ Unsupported media type")

        await update.message.reply_text("✅ Posted to channel!")

    except Exception as e:
        print("SEND ERROR:", e)
        await update.message.reply_text(f"❌ Failed: {e}")

async def scheduled_message(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = list(set(line.strip() for line in f if line.strip()))

        for user_id in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text="📢 Notis Harian: Top up sekarang & MENANG BESAR!"
                )
            except Exception as e:
                print(f"Failed {user_id}: {e}")

    except FileNotFoundError:
        print("user_ids.txt not found")


# ================= MAIN =================

def main():
    malaysia = timezone(timedelta(hours=8))

    app = ApplicationBuilder().token(TOKEN).build()
       
    print("BOT STARTED")

    # start command
    app.add_handler(CommandHandler("start", start))

    # button callback
    app.add_handler(CallbackQueryHandler(button_callback))

    print("REGISTER MEDIA HANDLER")
    
    # media handler
    app.add_handler(
        MessageHandler(
            filters.PHOTO
            | filters.VIDEO
            | filters.ANIMATION
            | filters.Document.VIDEO,
            handle_media_post
        )
    )

    # welcome new member
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_new_member
        )
    )

    # text handler
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            keyword_reply
        )
    )

    # scheduled message
    app.job_queue.run_daily(
        scheduled_message,
        time=time(17, 0, tzinfo=malaysia)
    )

    # webhook
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
