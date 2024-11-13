import os
import sys

from telegram.ext import (Application, CommandHandler, ConversationHandler,
                          MessageHandler, Updater, filters)

# ======== Add the project root directory to the Python path ========
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.telegram.bot import (AGE, DISTRICT, GENDER, INCOME, JOB, JOB_DETAIL,
                               LANGUAGE, MARITAL_STATUS, NOODLES, REGION,
                               SPICY_FOOD, age, district, error_handler,
                               gender, income, job, job_detail, language,
                               marital_status, noodles, region, spicy_food,
                               start)

ENV = os.getenv("ENV")
TELEGRAM_DEV_BOT_TOKEN = os.getenv("TELEGRAM_DEV_BOT_TOKEN")
TELEGRAM_AIURU_BOT_TOKEN = os.getenv("TELEGRAM_AIURU_BOT_TOKEN")

TELEGRAM_BOT_TOKEN = TELEGRAM_DEV_BOT_TOKEN if ENV == "development" else TELEGRAM_AIURU_BOT_TOKEN

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ======== Conversation Handlers ========
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            DISTRICT:[MessageHandler(filters.TEXT & ~filters.COMMAND, district)],
            JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, job)],
            JOB_DETAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, job_detail)],
            INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, income)],
            MARITAL_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, marital_status)],
            SPICY_FOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, spicy_food)],
            NOODLES: [MessageHandler(filters.TEXT & ~filters.COMMAND, noodles)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_error_handler(error_handler)
    application.add_handler(conversation_handler)

    # ======== Start/Stop the bot ========
    try:
        print("Starting Telegram bot polling...")
        application.run_polling()
    except KeyboardInterrupt:
        print("Bot stopped by user")

if __name__ == '__main__':
    main()
