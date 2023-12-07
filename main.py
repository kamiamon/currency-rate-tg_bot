import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
from decouple import config
from datetime import datetime
import matplotlib.pyplot as plt
import asyncio
import json
import os

TOKEN = config("API_KEY_BOT")
API_KEY = config("API_KEY_LAYER")

SELECTING, CHOOSING_CURRENCY, CHOOSING_INTERVAL, SETTING_MIN_THRESHOLDS, SETTING_MAX_THRESHOLDS, MONITORING = range(6)

CACHE_FILE_PATH = 'rate_data_cache.json'

currencies_file_path = 'valid_currencies.json'

with open(currencies_file_path, 'r', encoding='utf-8') as file:
    currencies_data = json.load(file)

def load_rate_data_from_cache():
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_rate_data_to_cache(data):
    with open(CACHE_FILE_PATH, 'w') as file:
        json.dump(data, file)

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"\U0001F44B Привет, {user.mention_html()}!\n\n"
        "Этот бот предназначен для мониторинга курсов валют.\n\n"
        "Используйте /settings, чтобы настроить мониторинг."
    )
    return SELECTING

async def cancel(update: Update, context: CallbackContext):
    job = context.user_data.get('job')
    if job:
        job.cancel()
    context.user_data.clear()

    await update.message.reply_text("\U000026D4 Мониторинг отменен. Все настройки сброшены.\n\n"
                                    "Используйте /settings, чтобы настроить мониторинг.")
    return ConversationHandler.END

def is_valid_currency(currency):
    return currency.upper() in currencies_data.get('currencies', {})

async def settings(update: Update, context: CallbackContext):
    await update.message.reply_text("\U0001F4B5 Выберите валюту, курс которой вы хотите мониторить (например, EUR, RUB, JPY):")
    return CHOOSING_CURRENCY

async def set_currency(update: Update, context: CallbackContext):
    entered_currency = update.message.text.upper()

    if is_valid_currency(entered_currency):
        context.user_data['selected_currency'] = entered_currency
        await update.message.reply_text(
            f"\U00002705 Выбрана валюта: {context.user_data['selected_currency']}.\n\n"
            "Теперь выберите интервал мониторинга в минутах (например, 15):"
        )
        return CHOOSING_INTERVAL
    else:
        await update.message.reply_text("\U0000274C Пожалуйста, выберите корректную валюту.")
        return CHOOSING_CURRENCY

async def set_interval(update: Update, context: CallbackContext):
    try:
        context.user_data['monitoring_interval'] = int(update.message.text)
        if context.user_data['monitoring_interval'] <= 0:
            raise ValueError("\U0000274C Интервал мониторинга должен быть положительным числом.")
        await update.message.reply_text(
            f"\U000023F1 Выбран интервал мониторинга: {context.user_data['monitoring_interval']} минут.\n\n"
            "Введите нижнее значение курса, при достижении которого бот будет Вас уведомлять:"
        )
        return SETTING_MIN_THRESHOLDS
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное положительное число для интервала мониторинга.")
        return CHOOSING_INTERVAL

async def set_min_threshold(update: Update, context: CallbackContext):
    try:
        context.user_data['min_threshold'] = float((update.message.text).replace(',', '.'))
        await update.message.reply_text(f"\U0001F4C9 Нижняя граница установлена: {context.user_data['min_threshold']}\n\n"
                                        "Введите вверхнее значение курса, при достижении которого бот будет Вас уведомлять:")
        return SETTING_MAX_THRESHOLDS
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное числовое значение для нижней границы.")
        return SETTING_MIN_THRESHOLDS

async def set_max_threshold(update: Update, context: CallbackContext):
    try:
        context.user_data['max_threshold'] = float((update.message.text).replace(',', '.'))
        await update.message.reply_text(f"\U0001F4C8 Верхняя граница установлена: {context.user_data['max_threshold']}\n\n"
                                        "Используйте /monitor, чтобы начать мониторинг.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное числовое значение для верхней границы.")
        return SETTING_MAX_THRESHOLDS

async def monitor(update: Update, context: CallbackContext):
    selected_currency = context.user_data.get('selected_currency')
    monitoring_interval = context.user_data.get('monitoring_interval')
    min_threshold = context.user_data.get('min_threshold')
    max_threshold = context.user_data.get('max_threshold')

    if selected_currency:
        base_currency = "USD"
        symbols = selected_currency
        url = f'https://api.apilayer.com/currency_data/live?base={base_currency}&symbols={symbols}'
        headers = {'apikey': API_KEY}

        async def monitor_task():
            while True:
                try:
                    response = requests.get(url, headers=headers)
                    data = response.json()
                    if 'error' in data:
                        print("error")
                        await update.message.reply_text(f"Error: {data['error']['info']}")
                    else:
                        rate = data['quotes'].get(f'USD{selected_currency}')
                        currency_cache_data = load_rate_data_from_cache()
                        if selected_currency not in currency_cache_data:
                            currency_cache_data[selected_currency] = {'rates': [], 'times': []}
                        currency_cache_data[selected_currency]['rates'].append(rate)
                        currency_cache_data[selected_currency]['times'].append(str(datetime.now().strftime("%d-%m %H:%M")))
                        save_rate_data_to_cache(currency_cache_data)

                        await draw_graph(update, context)

                        if min_threshold is not None and rate < min_threshold:
                            await update.message.reply_text(
                                f"\u26A0 Внимание!\n\nКурс {selected_currency} преодолел нижнюю границу: {rate}")

                        if max_threshold is not None and rate > max_threshold:
                            await update.message.reply_text(
                                f"\u26A0 Внимание!\n\nКурс {selected_currency} преодолел верхнюю границу: {rate}")

                except Exception as e:
                    print(f"Error: {e}")

                await asyncio.sleep(monitoring_interval * 60)

        task = asyncio.create_task(monitor_task())
        context.user_data['job'] = task
        await update.message.reply_text(
            f"\U0001F680 Мониторинг курса {selected_currency} начат с интервалом {monitoring_interval} минут.\n\n"
            "Используйте команду /currency, чтобы узнать последнее значение курса.\n\n"
            "Используйте команду /cancel, чтобы отменить мониторинг.")
    else:
        await update.message.reply_text("\U00002699 Настройте мониторинг, используя команду /settings.")
    return SELECTING
async def draw_graph(update: Update, context: CallbackContext):
    selected_currency = context.user_data.get('selected_currency')

    if selected_currency:
        currency_cache_data = load_rate_data_from_cache()
        if selected_currency in currency_cache_data:
            rates = currency_cache_data[selected_currency]['rates']
            times = currency_cache_data[selected_currency]['times']

            plt.figure(figsize=(10, 6))
            plt.plot(times[-12:], rates[-12:], marker='o')
            plt.gcf().autofmt_xdate()
            plt.xlabel('Время')
            plt.ylabel('Значения')
            plt.title(f'График курса {selected_currency}')
            plt.legend([f'{selected_currency} к USD'], loc='upper right')
            plt.grid(True)

            plt.savefig(f"{selected_currency}.png")

async def currency(update: Update, context: CallbackContext):
    selected_currency = context.user_data.get('selected_currency')

    if selected_currency:
        currency_cache_data = load_rate_data_from_cache()
        if selected_currency in currency_cache_data:
            last_rate = currency_cache_data[selected_currency]['rates'][-1]

            with open(f"{selected_currency}.png", 'rb') as photo_file:
                caption_text = f"\U0001F3C1 Последнее значение курса {selected_currency}: {last_rate}"
                await update.message.reply_photo(photo=photo_file, caption=caption_text)
        else:
            await update.message.reply_text("\U0000274C Нет данных о курсе. Начните мониторинг с помощью /monitor.")
    else:
        await update.message.reply_text("\U0000274C Не выбрана валюта для мониторинга.\n\nИспользуйте /settings.")

def main():
    print("Bot started!")
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING: [CommandHandler("settings", settings)],
            CHOOSING_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_currency)],
            CHOOSING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_interval)],
            SETTING_MIN_THRESHOLDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_min_threshold)],
            SETTING_MAX_THRESHOLDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_max_threshold)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("monitor", monitor))
    application.add_handler(CommandHandler("currency", currency))
    application.add_handler(CommandHandler("cancel", cancel))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
