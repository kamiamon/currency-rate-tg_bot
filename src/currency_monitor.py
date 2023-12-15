"""
Module containing functions for monitoring currency rates.
"""

from datetime import datetime
import asyncio
import requests
from telegram import Update
from telegram.ext import CallbackContext
from src.utils import load_rate_data_from_cache, save_rate_data_to_cache
from src.constants import SELECTING, API_LAYER_KEY, CACHE_FILE_PATH
from src.graph_drawer import draw_graph

async def monitor(update: Update, context: CallbackContext):
    """
    Start monitoring the selected currency's rate at specified intervals.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.

    Returns:
        int: The next conversation state.
    """
    selected_currency = context.user_data.get('selected_currency')
    monitoring_interval = context.user_data.get('monitoring_interval')
    min_threshold = context.user_data.get('min_threshold')
    max_threshold = context.user_data.get('max_threshold')

    if selected_currency:
        base_currency = "USD"
        symbols = selected_currency
        url = f'https://api.apilayer.com/currency_data/live?base={base_currency}&symbols={symbols}'
        headers = {'apikey': API_LAYER_KEY}

        async def monitor_task():
            while True:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    data = response.json()
                    if 'error' in data:
                        print("error")
                        await update.message.reply_text(f"Error: {data['error']['info']}")
                    else:
                        rate = data['quotes'].get(f'USD{selected_currency}')
                        currency_cache_data = load_rate_data_from_cache(CACHE_FILE_PATH)
                        if selected_currency not in currency_cache_data:
                            currency_cache_data[selected_currency] = {'rates': [], 'times': []}
                        currency_cache_data[selected_currency]['rates'].append(rate)
                        currency_cache_data[selected_currency]['times'].append(str(datetime.now().strftime("%d-%m %H:%M")))
                        save_rate_data_to_cache(currency_cache_data, CACHE_FILE_PATH)

                        await draw_graph(update, context)

                        if min_threshold is not None and rate < min_threshold:
                            await update.message.reply_html(
                                f"\u26A0 <b>Внимание!</b>\n\n"
                                f"Курс {selected_currency} преодолел нижнюю границу: {rate}")

                        if max_threshold is not None and rate > max_threshold:
                            await update.message.reply_html(
                                f"\u26A0 <b>Внимание!</b>\n\n"
                                f"Курс {selected_currency} преодолел верхнюю границу: {rate}")

                except requests.Timeout:
                    print("Request timeout")
                except Exception as e:
                    print(f"Error: {e}")

                await asyncio.sleep(monitoring_interval * 60)

        task = asyncio.create_task(monitor_task())
        context.user_data['job'] = task
        await update.message.reply_html(
            f"\U0001F680 <b>Мониторинг курса {selected_currency} "
            f"начат с интервалом {monitoring_interval} минут.</b>\n\n"
            "Используйте команду /currency, чтобы узнать последнее значение курса.\n\n"
            "Используйте команду /cancel, чтобы отменить мониторинг."
        )
    else:
        await update.message.reply_text(
            "\U00002699 Настройте мониторинг, используя команду /settings."
        )
    return SELECTING

async def currency(update: Update, context: CallbackContext):
    """
    Display the last recorded rate and a graph for the selected currency.

    Args:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    selected_currency = context.user_data.get('selected_currency')

    if selected_currency:
        currency_cache_data = load_rate_data_from_cache(CACHE_FILE_PATH)
        if selected_currency in currency_cache_data:
            last_rate = currency_cache_data[selected_currency]['rates'][-1]

            with open(f"graphs/{selected_currency}.png", 'rb') as photo_file:
                caption_text = (
                    f"\U0001F3C1 Последнее значение курса"
                    f" {selected_currency}: {last_rate}"
                )
                await update.message.reply_photo(photo=photo_file, caption=caption_text)
        else:
            await update.message.reply_text(
                "\U0000274C <b>Нет данных о курсе.</b>\n\n"
                "Начните мониторинг с помощью /monitor."
            )
    else:
        await update.message.reply_html(
            "\U0000274C <b>Не выбрана валюта для мониторинга.</b>"
            "\n\nИспользуйте /settings."
        )
