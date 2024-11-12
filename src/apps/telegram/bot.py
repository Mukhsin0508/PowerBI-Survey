import  logging
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import settings
from config.settings import get_districts_for_region, questions, regions
from apps.MongoDB.connect import conversation_collection


# ======== Logging configuration ========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# ======== Set higher level for httpx to only log if it is user-side request ========
logging.getLogger(__name__).addHandler(logging.StreamHandler())

logger = logging.getLogger(__name__)

# ======== Telegram bot token ========
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
COMPANY_NAME = settings.COMPANY_NAME
BUSINESS_USERNAME = settings.BUSINESS_USERNAME

# ======== Define States ========
(LANGUAGE, AGE, GENDER, REGION, DISTRICT, JOB, JOB_DETAIL, INCOME, MARITAL_STATUS, SPICY_FOOD, NOODLES) = range(11)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and send the first question."""
    user_language = context.user_data.get('language', "ru") # default to russian language
    question_text = questions[0]["text"][user_language]
    options = questions[0]['options']

    await update.message.reply_text(
        question_text,
        reply_markup=ReplyKeyboardMarkup([[opt["text"]] for opt in options], one_time_keyboard=True),
    )
    return LANGUAGE

async def handle_responses(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           question_id: int, next_state: int) -> int:
    """Generic Handler for each response."""
    user_response = update.message.text
    username = update.message.from_user.username

    user_language = context.user_data.get("language", "ru")  # Default to Russian
    language_code = user_language  # Language code is the same as user_language


    # ======== Store language selection if the first question =========
    if question_id == 0: # Language selection
        # ========= Find the language code corresponding to the selected language text ========
        selected_option = next(
            (opt for opt in questions[0]['options'] if opt['text'] == user_response),
            None
        )
        if selected_option is None:
            await update.message.reply_text(
                "Язык не найден. Попробуйте снова."
            )
            return LANGUAGE
        language_code = selected_option['id']
        context.user_data["language"] = language_code

    # ======== Store region selection and dynamically load districts =========
    elif question_id == 3: # Region selection
        selected_region = next(
            (region for region in regions if region['name'][language_code] == user_response), None
        )
        if selected_region is None:
            await update.message.reply_text("Регион не найден. Попробуйте снова.")
            return REGION
        context.user_data['region_id'] = selected_region['id']
        districts_options = get_districts_for_region(selected_region['id'])
        await update.message.reply_text(
            questions[3]["text"][language_code],
            reply_markup=ReplyKeyboardMarkup(
                [[district['name'][language_code]] for district in districts_options],
                one_time_keyboard=True
            )
        )
        return DISTRICT

    # ======== District selection ========
    elif question_id == 4:
        region_id = context.user_data.get('region_id')
        if not region_id:
            await update.message.reply_text("Регион не выбран. Пожалуйста, начните сначала.")
            return ConversationHandler.END
        districts_options = get_districts_for_region(region_id)
        selected_district = next(
            (district for district in districts_options if district['name'][language_code] == user_response), None
        )
        if selected_district is None:
            await update.message.reply_text("Район не найден. Попробуйте снова.")
            return DISTRICT  # Prompt for district selection again
        context.user_data['district_id'] = selected_district['id']  # Proceed to next question

    # ======== Store response in MongoDB ========
    conversation_collection.update_one(
        {"username": username},
        {"$set": {f"question_{question_id}": user_response}},
        upsert=True
    )

    # ======== Send the next question ========
    if question_id < len(questions) - 1:
        next_question = questions[question_id + 1]
        question_text = next_question["text"][user_language]
        options = next_question["options"]

        # ======== Handle option texts based on language and data source ========
        if isinstance(options, list):
            option_texts = []
            for opt in options:
                text_key = 'text'
                if f"text_{language_code}" in opt:
                    text_key = f"text_{language_code}"
                option_texts.append([opt.get(text_key, opt['text'])])
        elif next_question['id'] == 4:
            # ========= Next question is region selection ========
            option_texts = [[region['name'][language_code]] for region in regions]
        elif next_question['id'] == 5:
            # ========= Next question is district selection ========
            region_id = context.user_data.get("region_id")
            if region_id:
                districts_options = get_districts_for_region(region_id)
                option_texts = [[district['name'][language_code]] for district in districts_options]
            else:
                await update.message.reply_text("Регион не выбран. Пожалуйста, начните сначала.")
                return ConversationHandler.END
        else:
            # ======== Handle any other special cases or default behavior ========
            option_texts = []

        await update.message.reply_text(
            question_text,
            reply_markup=ReplyKeyboardMarkup(option_texts, one_time_keyboard=True),
        )
        return next_state
    else:
        # ======== End of questions ========
        await update.message.reply_text("Спасибо за участие в опросе!")
        return ConversationHandler.END


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=0, next_state=AGE)

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=1, next_state=GENDER)

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=2, next_state=REGION)

async def region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=3, next_state=DISTRICT)

async def district(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=4, next_state=JOB)

async def job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=5, next_state=JOB_DETAIL)

async def job_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=6, next_state=INCOME)

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=7, next_state=MARITAL_STATUS)

async def marital_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=8, next_state=SPICY_FOOD)

async def spicy_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=9, next_state=NOODLES)

async def noodles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=10, next_state=REGION)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(update, context, exc_info=context.error)