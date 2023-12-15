"""
Module containing configuration constants.
"""

from decouple import config

TELEGRAM_BOT_TOKEN = config("API_KEY_BOT")
API_LAYER_KEY = config("API_KEY_LAYER")

CACHE_FILE_PATH = 'data/rate_data_cache.json'
CURRENCIES_FILE_PATH = 'data/valid_currencies.json'

SELECTING, CHOOSING_CURRENCY, CHOOSING_INTERVAL, SETTING_MIN_THRESHOLDS, SETTING_MAX_THRESHOLDS, MONITORING = range(6)
