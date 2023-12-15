import os
import json

def is_valid_currency(currency, currencies_data):
    return currency.upper() in currencies_data.get('currencies', {})

def load_rate_data_from_cache(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_rate_data_to_cache(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)
