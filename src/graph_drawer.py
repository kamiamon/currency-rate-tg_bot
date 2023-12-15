"""
Module containing functions for drawing currency rate graphs.
"""

import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import CallbackContext
from src.utils import load_rate_data_from_cache
from src.constants import CACHE_FILE_PATH

async def draw_graph(update: Update, context: CallbackContext):
    """
    Draw and save a currency rate graph based on the user's selected currency.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    selected_currency = context.user_data.get('selected_currency')

    recent_values = 12
    height_image = 10
    width_image = 6

    if selected_currency:
        currency_cache_data = load_rate_data_from_cache(CACHE_FILE_PATH)
        if selected_currency in currency_cache_data:
            rates = currency_cache_data[selected_currency]['rates']
            times = currency_cache_data[selected_currency]['times']

            plt.figure(figsize=(height_image, width_image))
            plt.plot(times[-recent_values:], rates[-recent_values:], marker='o')
            plt.gcf().autofmt_xdate()
            plt.xlabel('Время')
            plt.ylabel('Значения')
            plt.title(f'График курса {selected_currency}')
            plt.legend([f'{selected_currency} к USD'], loc='upper right')
            plt.grid(True)

            plt.savefig(f"graphs/{selected_currency}.png")
