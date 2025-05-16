from typing import Final
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

TOKEN: Final = "7437237126:AAFNsP1jHSOfZ4IqbtkdQd7L48cSvktGiCE"
BOT_USERNAME: Final = "@CQ1251_bot"

# Dictionary of personnel with initial statuses
personnel_status = {
    "Pauline": {"rank": "2WO", "status": "MC", "dates": "150525-160525"},
    "S S R SABHARISWARAN": {"rank": "3SG", "status": "P", "dates": ""},
    "ONG YAONENG": {"rank": "CPL", "status": "MC", "dates": "150525-160525"},
    "JOVAN LOH": {"rank": "CPL", "status": "OFF", "dates": ""},
    "KELVEN KOH JUN YANG": {"rank": "CPL", "status": "MC", "dates": "150525-160525"},
    "ALVERN LOW": {"rank": "PTE", "status": "P", "dates": ""},
    "TAN SHAO EN": {"rank": "LCP", "status": "P", "dates": ""},
    "LIM YU SHEN": {"rank": "PTE", "status": "P", "dates": ""},
    "TAN KHAY YAN": {"rank": "3SG", "status": "P", "dates": ""},
    "DEMIEN LOH": {"rank": "PTE", "status": "ABSENT", "dates": ""},
    "EVAN TAN": {"rank": "PTE", "status": "P", "dates": ""},
    "SIAO BOON WEI": {"rank": "PTE", "status": "P", "dates": ""},
    "GOH GUAN YI, JAVIER": {"rank": "PTE", "status": "P", "dates": ""},
    "YEOH RANDALL": {"rank": "PTE", "status": "P", "dates": ""},
}

# Define conversation states
STATUS, DATES, SET_DATES = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please enter your full name to continue:")
    return STATUS

async def status_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.text.strip().upper()
    for name in personnel_status:
        if user in name.upper():
            context.user_data["name"] = name
            reply_keyboard = [["P", "MC", "MA", "OL"]]
            await update.message.reply_text(
                f"Hello {name}, what is your new status?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            )
            return DATES
    await update.message.reply_text("Name not found. Try again.")
    return STATUS

async def date_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = update.message.text.strip()
    name = context.user_data["name"]
    context.user_data["status"] = status

    if status == "P":
        personnel_status[name]["status"] = "P"
        personnel_status[name]["dates"] = ""
        await update.message.reply_text(f"Status for {name} updated to Present.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Enter the date range (e.g., 160525-170525):")
        return SET_DATES

async def set_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_range = update.message.text.strip()
    name = context.user_data["name"]
    status = context.user_data["status"]
    personnel_status[name]["status"] = status
    personnel_status[name]["dates"] = date_range
    await update.message.reply_text(f"{name} updated to {status} ({date_range}).")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Update canceled.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, status_step)],
            DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_step)],
            SET_DATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_dates)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()