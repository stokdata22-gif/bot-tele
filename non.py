import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN belum diatur. Isi nilainya di file .env.")

PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
if not WEBHOOK_BASE_URL:
    raise RuntimeError("WEBHOOK_URL belum diatur. Isi URL HTTPS server di environment.")

SERVER_STATUS = "AKTIF"
ACTIVATION_TIME = "2026-06-06 10:00:00"
HOURS_LEFT = 24
TOKENS_USED = 1250
CURRENT_MODE = "Gambar"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🟢 Server Aktif", callback_data="server_aktif"),
            InlineKeyboardButton("🔴 Server Mati", callback_data="server_mati"),
        ],
        [InlineKeyboardButton("📊 Status Server", callback_data="server_status")],
        [
            InlineKeyboardButton("🖼️ Mode Gambar", callback_data="mode_gambar"),
            InlineKeyboardButton("🎬 Mode Video", callback_data="mode_video"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🤖 **Panel Kontrol Bot AI**\n\n"
        "Pilih menu:"
    )

    if update.message:
        await update.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    global SERVER_STATUS, CURRENT_MODE

    data = query.data

    if data == "server_aktif":
        SERVER_STATUS = "AKTIF"
        await query.message.reply_text("✅ Server aktif!")
        await start(update, context)

    elif data == "server_mati":
        SERVER_STATUS = "MATI"
        await query.message.reply_text("❌ Server dimatikan.")
        await start(update, context)

    elif data == "server_status":
        status_text = (
            f"📊 **Status Server:**\n\n"
            f"• Status: {SERVER_STATUS}\n"
            f"• Sisa Waktu: {HOURS_LEFT} jam\n"
            f"• Token: {TOKENS_USED}"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(status_text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "mode_gambar":
        CURRENT_MODE = "Gambar"
        await query.message.reply_text("🖼️ Mode Gambar ON")

    elif data == "mode_video":
        CURRENT_MODE = "Video"
        await query.message.reply_text("🎬 Mode Video ON")

    elif data == "back_to_menu":
        await start(update, context)


def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    webhook_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/telegram"
    print("Bot webhook running...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=webhook_url,
        secret_token=WEBHOOK_SECRET or None,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()