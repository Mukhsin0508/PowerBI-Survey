# apps/telegram/bot.py

import logging
import random

from config import settings
from apps.telegram.helpers import store_response, get_selected_option
from config.settings import get_districts_for_region, questions, regions
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ======== Logging configuration ========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== Telegram bot token ========
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
COMPANY_NAME = settings.COMPANY_NAME
BUSINESS_USERNAME = settings.BUSINESS_USERNAME

# ======== Define States ========
(
    LANGUAGE,
    AGE,
    GENDER,
    REGION,
    DISTRICT,
    JOB,
    JOB_DETAIL,
    INCOME,
    MARITAL_STATUS,
    SPICY_FOOD,
    NOODLES,
    QUESTION_11,
    QUESTION_12,
    QUESTION_13,
    QUESTION_14,
    QUESTION_15,
    QUESTION_16,
    QUESTION_17,
    QUESTION_18,
    QUESTION_19,
    QUESTION_20,
    QUESTION_21,
    QUESTION_22,
    QUESTION_23,
    QUESTION_24,
    QUESTION_25,
    QUESTION_26,
    QUESTION_27,
    QUESTION_28,
    QUESTION_29,
    QUESTION_30,
    QUESTION_31,
    QUESTION_32,
    QUESTION_33,
    QUESTION_34,
    QUESTION_35,
    QUESTION_36,
) = range(1, 38)

# ======== Mapping of question IDs to state constants ========
QUESTION_STATE_MAP = {
    1: LANGUAGE,
    2: AGE,
    3: GENDER,
    4: REGION,
    5: DISTRICT,
    6: JOB,
    7: JOB_DETAIL,
    8: INCOME,
    9: MARITAL_STATUS,
    10: SPICY_FOOD,
    11: NOODLES,
    12: QUESTION_11,
    13: QUESTION_12,
    14: QUESTION_13,
    15: QUESTION_14,
    16: QUESTION_15,
    17: QUESTION_16,
    18: QUESTION_17,
    19: QUESTION_18,
    20: QUESTION_19,
    21: QUESTION_20,
    22: QUESTION_21,
    23: QUESTION_22,
    24: QUESTION_23,
    25: QUESTION_24,
    26: QUESTION_25,
    27: QUESTION_26,
    28: QUESTION_27,
    29: QUESTION_28,
    30: QUESTION_29,
    31: QUESTION_30,
    32: QUESTION_31,
    33: QUESTION_32,
    34: QUESTION_33,
    35: QUESTION_34,
    36: QUESTION_35,
    37: QUESTION_36,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and send the first question."""
    user_language = context.user_data.get('language', "ru")  # default to Russian
    question_text = questions[0]["text"][user_language]

    options = questions[0]['options']
    option_texts = [[opt["text"]] for opt in options]

    await update.message.reply_text(
        question_text,
        reply_markup=ReplyKeyboardMarkup(option_texts, one_time_keyboard=True),
    )
    return LANGUAGE

async def handle_responses(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    question_id: int,
) -> int:
    """Generic handler for each response."""
    global options
    user_response = update.message.text
    username = update.message.from_user.username

    # ======== Language code is the same as user_language ========
    user_language = context.user_data.get("language", "ru")
    language_code = user_language

    # ========= Load the current question ========
    current_question = next(
        (q for q in questions if q["id"] == question_id),
        None,
    )

    if not current_question:
        await update.message.reply_text("Вопрос не найден.")
        return ConversationHandler.END

    # ======== if awaiting custom user input ========
    if context.user_data.get('awaiting_custom_input'):
        # ======== Store the custom input ========
        custom_input = user_response
        question_id = context.user_data.get('custom_question_id')
        context.user_data['awaiting_custom_input'] = False

        # ========= Store the response ========
        store_response(username, question_id, custom_input)

        # ========== Proceed to the next question =========
        next_question_id = context.user_data.get('next_question_id', question_id + 1)
        next_state = get_next_state(next_question_id)
        return await handle_responses(
            update,
            context,
            next_question_id,
        )

    # ======== Special handling for language selection ========
    if question_id == 1:  # Language selection
        selected_option = next(
            (opt for opt in current_question['options']
                if opt['text'] == user_response),
            None,
        )
        if selected_option is None:
            await update.message.reply_text("Язык не найден. Попробуйте снова.")
            return LANGUAGE

        language_code = selected_option['id']
        context.user_data["language"] = language_code
        user_language = language_code

    # ======== Store region selection and dynamically load districts ========
    elif question_id == 4:  # Region selection
        selected_region = next(
            (
                region
                for region in regions
                if region['name'][language_code] == user_response
            ),
            None,
        )
        if selected_region is None:
            await update.message.reply_text("Регион не найден. Попробуйте снова.")
            return REGION

        context.user_data['region_id'] = selected_region['id']

        # Now prompt for the districts in this region
        districts_options = get_districts_for_region(selected_region['id'])
        district_names = [[district['name'][language_code]] for district in districts_options]

        question_text = questions[4]["text"][language_code]
        await update.message.reply_text(
            question_text,
            reply_markup=ReplyKeyboardMarkup(district_names, one_time_keyboard=True)
        )
        return DISTRICT

    # ======== District selection ========
    elif question_id == 5:
        region_id = context.user_data.get('region_id')
        if not region_id:
            await update.message.reply_text(
                "Регион не выбран. Пожалуйста, начните сначала."
            )
            return ConversationHandler.END
        districts_options = get_districts_for_region(region_id)
        selected_district = next(
            (
                district for
                district in districts_options
                if district['name'][language_code] == user_response),
            None,
        )
        if selected_district is None:
            await update.message.reply_text("Район не найден. Попробуйте снова.")
            return DISTRICT  # Prompt for district selection again
        context.user_data['district_id'] = selected_district['id']  # Proceed to next question

    # ======== Store the user's response ========
    else:
        store_response(username, question_id, user_response)

    # ========= Determine the next question ID ========
    next_question_id = None

    # ======== Handle branching logic ========
    if 'next_question' in current_question:
        next_question_id = current_question['next_question']
    else:
        selected_option = get_selected_option(
            current_question,
            user_response,
            user_language,
        )
        if selected_option and 'next_question' in selected_option:
            next_question_id = selected_option['next_question']
        else:
            next_question_id = question_id + 1  # Default to the next question

    # ========= Handle the end of survey =========
    if next_question_id == 'end' or next_question_id is None:
        await update.message.reply_text("Спасибо за участие в опросе!")
        return ConversationHandler.END

    next_question = next(
        (q for q in questions if q['id'] == int(next_question_id)),
        None,
    )

    if not next_question:
        await update.message.reply_text("Следующий вопрос не найден.")
        return ConversationHandler.END

    next_state = get_next_state(int(next_question_id))

    # ======== Prepare the question text and options =========
    question_text = next_question['text'].get(user_language, next_question['text']['ru'])

    # Handle options based on question ID
    if next_question['id'] == 4:
        # Region selection
        option_texts = [[region['name'][language_code]] for region in regions]
    elif next_question['id'] == 5:
        # District selection
        region_id = context.user_data.get('region_id')
        if not region_id:
            await update.message.reply_text("Регион не выбран. Пожалуйста, начните сначала.")
            return ConversationHandler.END
        districts_options = get_districts_for_region(region_id)
        option_texts = [[district['name'][language_code]] for district in districts_options]
    else:
        # For other questions, fetch options from the question data
        options = next_question.get('options', [])

        # ======== Randomize options if required =========
        if next_question.get('randomize_options', False):
            random.shuffle(options)

        # Build option_texts
        option_texts = []
        for opt in options:
            text_key = 'text'
            if f"text_{user_language}" in opt:
                text_key = f"text_{user_language}"
            option_text = opt.get(text_key, opt['text'])

            # Handle options that require input
            if opt.get('requires_input'):
                option_text += " (Введите свой вариант)"
                context.user_data['awaiting_custom_input'] = True
                context.user_data['custom_question_id'] = next_question['id']
                context.user_data['next_question_id'] = next_question_id + 1

            option_texts.append([option_text])

    # Handle different question types
    question_type = next_question.get("type", "single_choice")

    if question_type == 'open_ended':
        await update.message.reply_text(question_text)
        return next_state

    elif question_type == 'single_choice':
        await update.message.reply_text(
            question_text,
            reply_markup=ReplyKeyboardMarkup(
                option_texts,
                one_time_keyboard=True,
            ),
        )
        return next_state

    elif question_type == 'multiple_choice':
        # Send options as numbered list
        option_list = []
        for index, opt in enumerate(options):
            text_key = 'text'
            if f"text_{user_language}" in opt:
                text_key = f"text_{user_language}"
            option_text = opt.get(text_key, opt['text'])
            option_list.append(f"{index+1}. {option_text}")
        option_text_str = "\n".join(option_list)
        instruction = "Выберите один или несколько вариантов, указывая номера через запятую:"
        await update.message.reply_text(
            f"{question_text}\n{instruction}\n{option_text_str}",
        )
        return next_state

    elif question_type == 'rating':
        scale_min, scale_max = next_question.get('scale', [1, 10])
        rating_buttons = [[str(i)] for i in range(scale_min, scale_max + 1)]
        await update.message.reply_text(
            question_text,
            reply_markup=ReplyKeyboardMarkup(
                rating_buttons,
                one_time_keyboard=True,
            ),
        )
        return next_state

    else:
        # Default handling
        await update.message.reply_text(question_text)
        return next_state

# ======== Helper function to get the next state based on question ID ========
def get_next_state(question_id):
    return QUESTION_STATE_MAP.get(question_id)

# ======== Async handler functions ========
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=1)

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=2)

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=3)

async def region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=4)

async def district(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=5)

async def job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=6)

async def job_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=7)

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=8)

async def marital_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=9)

async def spicy_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=10)

async def noodles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=11)

# ========= Continue defining handler functions for the remaining questions =========
async def question_11(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=12)

async def question_12(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=13)

async def question_13(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=14)

async def question_14(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=15)

async def question_15(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=16)

async def question_16(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=17)

async def question_17(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=18)

async def question_18(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=19)

async def question_19(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=20)

async def question_20(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=21)

async def question_21(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=22)

async def question_22(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=23)

async def question_23(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=24)

async def question_24(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=25)

async def question_25(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=26)

async def question_26(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=27)

async def question_27(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=28)

async def question_28(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=29)

async def question_29(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=30)

async def question_30(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=31)

async def question_31(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=32)

async def question_32(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=33)

async def question_33(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=34)

# Handlers for non-consumer path
async def question_34(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=35)

async def question_35(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_responses(update, context, question_id=36)

async def question_36(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ======== End of non-consumer path ========
    await update.message.reply_text("Спасибо за участие в опросе!")
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

