import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
from decouple import config
from datetime import datetime, timedelta
import matplotlib.pylab as plt
import asyncio
from io import BytesIO

TOKEN = config("API_KEY_BOT")
API_KEY = config("API_KEY_LAYER")

SELECTING, CHOOSING_CURRENCY, CHOOSING_INTERVAL, MONITORING = range(4)

selected_currency = None
monitoring_interval = None

rate_data = []
time_data = []

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}!\n"
        "Этот бот предназначен для мониторинга курсов валют.\n"
        "Используйте /settings, чтобы настроить мониторинг."
    )
    return SELECTING

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Мониторинг отменен.")
    context.user_data.pop('job', None)
    return ConversationHandler.END

async def settings(update: Update, context: CallbackContext):
    await update.message.reply_text("Выберите валюту, курс которой вы хотите мониторить (например, EUR, RUB, JPY):")
    return CHOOSING_CURRENCY

async def set_currency(update: Update, context: CallbackContext):
    global selected_currency
    selected_currency = update.message.text.upper()
    await update.message.reply_text(
        f"Выбрана валюта: {selected_currency}.\n"
        "Теперь выберите интервал мониторинга в минутах (например, 15):"
    )
    return CHOOSING_INTERVAL

async def set_interval(update: Update, context: CallbackContext):
    global monitoring_interval
    monitoring_interval = int(update.message.text)
    await update.message.reply_text(
        f"Выбран интервал мониторинга: {monitoring_interval} минут.\n"
        "Используйте /monitor_start, чтобы начать мониторинг."
    )
    return ConversationHandler.END

async def monitor_start(update: Update, context: CallbackContext):
    if selected_currency:
        base_currency = "USD"
        symbols = selected_currency
        url = f'https://api.apilayer.com/currency_data/live?base={base_currency}&symbols={symbols}'
        headers = {'apikey': API_KEY}

        async def monitor_task():
            while True:
                response = requests.get(url, headers=headers)
                data = response.json()

                try:
                    if 'error' in data:
                        print("error")
                        await update.message.reply_text(f"Error: {data['error']['info']}")
                    else:
                        rate = data['quotes'].get(f'USD{selected_currency}')
                        rate_data.append(rate)
                        time_data.append(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

                except:
                    print("error except")

                await asyncio.sleep(monitoring_interval * 60)

        task = asyncio.create_task(monitor_task())
        context.user_data['job'] = task
        await update.message.reply_text(f"Мониторинг курса {selected_currency} начат с интервалом {monitoring_interval} минут.\n\n"
                                        "Используйте команду /get_currency, чтобы узнать последнее значение курса.\n\n"
                                        "Используйте команду /get_graph, чтобы получить график валюты.")
    else:
        await update.message.reply_text("Настройте мониторинг, используя /settings.")
    return SELECTING

async def get_currency(update: Update, context: CallbackContext):
    if rate_data:
        last_rate = rate_data[-1]
        await update.message.reply_text(f"Последнее значение курса {selected_currency}: {last_rate}")
    else:
        await update.message.reply_text("Нет данных о курсе. Начните мониторинг с помощью /monitor_start.")

async def get_graph(update: Update, context: CallbackContext):
    if time_data and rate_data:

        plt.figure(figsize=(10, 6))
        plt.plot(time_data, rate_data, marker='o')

        plt.gcf().autofmt_xdate()

        plt.xlabel('Время')
        plt.ylabel('Значения')
        plt.title(f'График курса {selected_currency}')
        plt.grid(True)

        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        await update.message.reply_photo(photo=image_stream)
    else:
        await update.message.reply_text("Нет данных для построения графика. Начните мониторинг с помощью /monitor_start.")

def main():
    print("Bot started!")
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING: [CommandHandler("settings", settings)],
            CHOOSING_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_currency)],
            CHOOSING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_interval)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("monitor_start", monitor_start))
    application.add_handler(CommandHandler("get_currency", get_currency))
    application.add_handler(CommandHandler("get_graph", get_graph))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
