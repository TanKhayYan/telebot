from typing import Final
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import logging
from datetime import datetime  # Don't forget this

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

# ✅ Moved this ABOVE where it's used
def generate_report():
    today = datetime.now().strftime("%d/%m/%Y\n(%A)").upper()
    total = len(personnel_status)
    present = sum(1 for p in personnel_status.values() if p["status"] == "P")

    sorted_personnel = sorted(personnel_status.items(), key=lambda x: x[1]['rank'] + x[0])
    log_lines = []
    for idx, (name, info) in enumerate(sorted_personnel, start=1):
        status = info["status"]
        dates = f" ({info['dates']})" if info["dates"] else ""
        log_lines.append(f"{idx}) {info['rank']} {name} - {status}{dates}")

    duty_rotation = [
        "YaoNeng", "Kelven", "Alvern", "Shao En",
        "Yu Shen", "Evan", "Demien", "Randall"
    ]
    duty_section = "\n- " + "\n- ".join(duty_rotation)

    return f"""Date: {today}
Strength: {total}
Present: {present}

*==========*
*LOGS Branch {present}/{total}
  
{chr(10).join(log_lines)}
*==========*

Duty storeman for today 
==========
*DUTY STOREMAN ROTATION*{duty_section}

  
-You are to *Manage the key issue/registered book* in LOG BR office.

*Key registered book*
- Any cancellation must be in *RED* ink and sign in blue/black ink.

You are to open LOG BR office by *0800h*. 

*Non-compliance* 
- Will be given extra duty storeman 
==========
==========
*MC submission for ALL*
- You are to upload your MC into the OneNS immediately upon receiving it from the hospital/any private clinic.(less MC from camp)

- *Show it to 2WO Pauline once you report back to camp.*

- All MC hard copy are to be kept with you for minimum *(2 year)*.

*(Any MC not uploaded/submitted in OneNS will be considered as AWOL and you'll be charged)*
==========
==========
"""

# Command handlers
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
        await update.message.reply_text(generate_report())
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
    await update.message.reply_text(generate_report())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Update canceled.")
    return ConversationHandler.END

async def show_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report_text = generate_report()
    await update.message.reply_text(report_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Current functions: Parade state\n\n"
        "How to use the bot for parade state:\n"
        "1. /start (start the bot)\n"
        "2. Enter your name (doesn't have to be full)\n"
        "3. Enter your status. Status will remain constant unless changed. "
        "e.g., if you do not change it from P to MC the next day, it will remain as P. "
        "Whatever you input will be reflected after your name.\n"
        "e.g., inputting 'present' as 3SG TAN KHAY YAN will reflect: "
        "`3SG TAN KHAY YAN - present`, rather than `3SG TAN KHAY YAN - P`.\n"
        "Accepted formats are: P, MC, MA, OL, OFF, ABSENT.\n"
        "4. If you are on MC, input date range (e.g., 160525-170525).\n\n"
        "/report (produces parade state)"
    )
    await update.message.reply_text(help_text)

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

    app.add_handler(CommandHandler("report", show_report))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()