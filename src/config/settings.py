import json
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# ======= ENV ========
ENV = os.getenv("ENV")

# =============== Development Telegram Configurations ====================
TELEGRAM_DEV_BOT_TOKEN= os.getenv('TELEGRAM_DEV_BOT_TOKEN')
DEV_BOT_USERNAME= os.getenv('DEV_BOT_USERNAME')
DEV_BUSINESS_USERNAME= os.getenv('DEV_BUSINESS_USERNAME')
DEV_COMPANY_NAME = os.getenv('DEV_COMPANY_NAME')

# =============== Production Telegram Bot Configurations ====================
TELEGRAM_PROD_BOT_TOKEN=os.getenv('TELEGRAM_PROD_BOT_TOKEN')
PROD_BOT_USERNAME= os.getenv('PROD_BOT_USERNAME')
BUSINESS_USERNAME=os.getenv('BUSINESS_USERNAME')
COMPANY_NAME = os.getenv('COMPANY_NAME')

TELEGRAM_BOT_TOKEN = TELEGRAM_DEV_BOT_TOKEN if ENV == 'development' else TELEGRAM_PROD_BOT_TOKEN
TELEGRAM_BOT_USERNAME = DEV_BOT_USERNAME if ENV == 'development' else PROD_BOT_USERNAME
BUSINESS_USERNAME = DEV_BUSINESS_USERNAME if ENV == 'development' else BUSINESS_USERNAME
COMPANY_NAME = DEV_COMPANY_NAME if ENV == 'development' else COMPANY_NAME


def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

questions = load_json('config/questions.json')
regions = load_json('config/locations/regions.json')
districts = load_json('config/locations/districts.json')

def get_districts_for_region(region_id):
    """Get districts that match the given region_id."""
    return [d for d in districts if d['region_id'] == region_id]


