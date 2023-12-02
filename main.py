import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
from decouple import config
from datetime import datetime
import matplotlib.pylab as plt

TOKEN = config("API_KEY_BOT")
API_KEY = config("API_KEY_LAYER")

SELECTING, CHOOSING_CURRENCY, MONITORING = range(3)

selected_currency = None

rate_data = []
time_data = []

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}!\n"
        "Этот бот предназначен для мониторинга курсов валют.\n"
        "Используйте /monitor, чтобы начать мониторинг."
    )
    return SELECTING

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Мониторинг отменен.")
    context.user_data.pop('job', None)
    return ConversationHandler.END

async def monitor(update: Update, context: CallbackContext):
    await update.message.reply_text("Выберите валюту, курс которой вы хотите мониторить (например, EUR, RUB, JPY):")
    return CHOOSING_CURRENCY

async def set_currency(update: Update, context: CallbackContext):
    global selected_currency
    selected_currency = update.message.text.upper()
    await update.message.reply_text(
        f"Выбрана валюта: {selected_currency}.\n"
        "Используйте /monitor_currency, чтобы узнать текущий курс."
    )
    return ConversationHandler.END

async def monitor_currency(update: Update, context: CallbackContext):
    if selected_currency:
        base_currency = "USD"
        symbols = selected_currency
        url = f'https://api.apilayer.com/currency_data/live?base={base_currency}&symbols={symbols}'
        headers = {'apikey': API_KEY}

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
                print(rate_data, "\n", time_data)
                draw(time_data, rate_data)
                await update.message.reply_text(f"Текущий курс {selected_currency}: {rate}")

        except:
            print("error execpt")
    else:
        await update.message.reply_text("Выберите валюту, используя /monitor.")
    return SELECTING

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING: [CommandHandler("monitor", monitor)],
            CHOOSING_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_currency)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("monitor_currency", monitor_currency))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

def draw(datetimes, values):
    # Создание графика
    plt.figure(figsize=(10, 6))
    plt.plot(datetimes, values, marker='o')

    # Поворот меток времени для лучшей читаемости
    plt.gcf().autofmt_xdate()

    #Наименование осей и графика
    plt.xlabel('Время')
    plt.ylabel('Значения')
    plt.title('График курса выбранной валюты')
    plt.grid(True)

    plt.savefig("graph.png")

if __name__ == "__main__":
    main()
