import os
import sys

from telegram.ext import (Application, CommandHandler, ConversationHandler, MessageHandler, filters)

# ======== Add the project root directory to the Python path ========
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import (start, language, age, gender, region, district, job, job_detail, income, marital_status,
                      spicy_food, noodles, question_11, question_12, question_13, question_14, question_15, question_16,
                      question_17, question_18, question_19, question_20, question_21, question_22, question_23,
                      question_24, question_25, question_26, question_27, question_28, question_29, question_30,
                      question_31, question_32, question_33, question_34, question_35, question_36, error_handler, )

from conversation_states import (LANGUAGE, AGE, GENDER, REGION, DISTRICT, JOB, JOB_DETAIL, INCOME, MARITAL_STATUS,
                                 SPICY_FOOD, NOODLES, QUESTION_11, QUESTION_12, QUESTION_13, QUESTION_14, QUESTION_15,
                                 QUESTION_16, QUESTION_17, QUESTION_18, QUESTION_19, QUESTION_20, QUESTION_21,
                                 QUESTION_22, QUESTION_23, QUESTION_24, QUESTION_25, QUESTION_26, QUESTION_27,
                                 QUESTION_28, QUESTION_29, QUESTION_30, QUESTION_31, QUESTION_32, QUESTION_33,
                                 QUESTION_34, QUESTION_35, QUESTION_36, )

ENV = os.getenv("ENV")
TELEGRAM_DEV_BOT_TOKEN = os.getenv("TELEGRAM_DEV_BOT_TOKEN")
TELEGRAM_AIURU_BOT_TOKEN = os.getenv("TELEGRAM_AIURU_BOT_TOKEN")

TELEGRAM_BOT_TOKEN = TELEGRAM_DEV_BOT_TOKEN if ENV == "development" else TELEGRAM_AIURU_BOT_TOKEN


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ======== Conversation Handlers ========
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={LANGUAGE:[MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            AGE:[MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            GENDER:[MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            REGION:[MessageHandler(filters.TEXT & ~filters.COMMAND, region)],
            DISTRICT:[MessageHandler(filters.TEXT & ~filters.COMMAND, district)],
            JOB:[MessageHandler(filters.TEXT & ~filters.COMMAND, job)],
            JOB_DETAIL:[MessageHandler(filters.TEXT & ~filters.COMMAND, job_detail)],
            INCOME:[MessageHandler(filters.TEXT & ~filters.COMMAND, income)],
            MARITAL_STATUS:[MessageHandler(filters.TEXT & ~filters.COMMAND, marital_status)],
            SPICY_FOOD:[MessageHandler(filters.TEXT & ~filters.COMMAND, spicy_food)],
            NOODLES:[MessageHandler(filters.TEXT & ~filters.COMMAND, noodles)],
            QUESTION_11:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_11)],
            QUESTION_12:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_12)],
            QUESTION_13:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_13)],
            QUESTION_14:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_14)],
            QUESTION_15:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_15)],
            QUESTION_16:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_16)],
            QUESTION_17:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_17)],
            QUESTION_18:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_18)],
            QUESTION_19:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_19)],
            QUESTION_20:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_20)],
            QUESTION_21:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_21)],
            QUESTION_22:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_22)],
            QUESTION_23:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_23)],
            QUESTION_24:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_24)],
            QUESTION_25:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_25)],
            QUESTION_26:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_26)],
            QUESTION_27:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_27)],
            QUESTION_28:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_28)],
            QUESTION_29:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_29)],
            QUESTION_30:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_30)],
            QUESTION_31:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_31)],
            QUESTION_32:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_32)],
            QUESTION_33:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_33)],
            QUESTION_34:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_34)],
            QUESTION_35:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_35)],
            QUESTION_36:[MessageHandler(filters.TEXT & ~filters.COMMAND, question_36)], },
        fallbacks=[CommandHandler("start", start)], )

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