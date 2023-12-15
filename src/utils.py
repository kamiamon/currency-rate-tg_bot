"""
Module containing utility functions.
"""

import os
import json

def is_valid_currency(currency, currencies_data):
    """
    Check if the provided currency is valid.

    Args:
        currency (str): The currency code to check.
        currencies_data (dict): Dictionary containing valid currencies.

    Returns:
        bool: True if the currency is valid, False otherwise.
    """
    return currency.upper() in currencies_data.get('currencies', {})

def load_rate_data_from_cache(file_path):
    """
    Load rate data from a cache file.

    Args:
        file_path (str): The path to the cache file.

    Returns:
        dict: The loaded rate data.
    """
    if not os.path.exists("graphs"):
        os.makedirs("graphs")

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_rate_data_to_cache(data, file_path):
    """
    Save rate data to a cache file.

    Args:
        data (dict): The data to be saved.
        file_path (str): The path to the cache file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
