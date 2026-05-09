import asyncio
import logging
import os
import sys

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 986046035
QR_IMAGE = "upi_qr.png"
# ==========================================

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
logging.basicConfig(level=logging.INFO)

request = HTTPXRequest(connect_timeout=20, read_timeout=20)

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Daily Desi (₹300)", callback_data="daily")],
        [InlineKeyboardButton("💎 Awesome Candids (₹600)", callback_data="premium")],
    ]

    await update.message.reply_text(
        "👋 Choose a plan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= PLAN SELECTION =================

async def handle_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = query.data
    context.user_data["plan"] = plan

    # ================= DAILY PLAN =================
    if plan == "daily":
        demo_link1 = "https://telegra.ph/daily-desi-05-09"

        # 🔘 Button for better UI
        keyboard = [
            [InlineKeyboardButton("👀 View Demo", url=demo_link1)]
        ]
        
        await query.message.reply_text(
            "💰 <b>Daily Desi</b>\n\n"
            "💳 Pay ₹300 using QR below\n\n"
            "Then send screenshot here.",
            parse_mode="HTML"
        )

        try:
            with open(QR_IMAGE, "rb") as qr:
                await query.message.reply_photo(qr)
        except:
            await query.message.reply_text("⚠️ QR not found")

    # ================= PREMIUM PLAN =================
    elif plan == "premium":
        demo_link = "https://telegra.ph/AWESOME-CANDIDS-DEMO-04-06-2"

        # 🔘 Button for better UI
        keyboard = [
            [InlineKeyboardButton("👀 View Demo", url=demo_link)]
        ]

        await query.message.reply_text(
            "💎 <b>Awesome Candids</b>\n\n"
            "🔥 Click below to view demo content\n\n"
            "💳 After viewing, pay ₹600 using QR",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        try:
            with open(QR_IMAGE, "rb") as qr:
                await query.message.reply_photo(qr)
        except:
            await query.message.reply_text("⚠️ QR not found")

# ================= HANDLE SCREENSHOT =================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    plan = context.user_data.get("plan", "Not selected")

    user_link = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    await update.message.reply_text("Screenshot received ✅\nPlease wait for admin approval.")

    caption = f"""
📥 <b>New Payment Request</b>

👤 User: {user_link}
🆔 ID: <code>{user.id}</code>
📛 Username: @{user.username if user.username else "None"}
📦 Plan: <b>{plan}</b>
"""

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML"
    )

# ================= MAIN =================

def main():
    print("🚀 Bot running...")

    app = ApplicationBuilder().token(TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_plan))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()
