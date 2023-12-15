from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext
from src.utils import is_valid_currency
from src.constants import SELECTING, CHOOSING_CURRENCY, CHOOSING_INTERVAL, SETTING_MIN_THRESHOLDS, SETTING_MAX_THRESHOLDS, CURRENCIES_FILE_PATH
import json

with open(CURRENCIES_FILE_PATH, 'r', encoding='utf-8') as file:
    currencies_data = json.load(file)

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

    await update.message.reply_html("\U000026D4 <b>Мониторинг отменен. Все настройки сброшены.</b>\n\n"
                                    "Используйте /settings, чтобы настроить мониторинг.")
    return ConversationHandler.END

async def settings(update: Update, context: CallbackContext):
    await update.message.reply_html("\U0001F4B5 Выберите валюту, курс которой вы хотите мониторить (например, EUR, RUB, JPY):")
    return CHOOSING_CURRENCY

async def set_currency(update: Update, context: CallbackContext):
    entered_currency = update.message.text.upper()

    if is_valid_currency(entered_currency, currencies_data):
        context.user_data['selected_currency'] = entered_currency
        await update.message.reply_html(
            f"\U00002705 <b>Выбрана валюта: {context.user_data['selected_currency']}.</b>\n\n"
            "Теперь выберите интервал мониторинга в минутах (например, 15):"
        )
        return CHOOSING_INTERVAL
    else:
        await update.message.reply_html("\U0000274C Пожалуйста, выберите корректную валюту!")
        return CHOOSING_CURRENCY

async def set_interval(update: Update, context: CallbackContext):
    try:
        context.user_data['monitoring_interval'] = int(update.message.text)
        if context.user_data['monitoring_interval'] <= 0:
            raise ValueError("\U0000274C Интервал мониторинга должен быть положительным числом!")
        await update.message.reply_html(
            f"\U000023F1 <b>Выбран интервал мониторинга: {context.user_data['monitoring_interval']} минут.</b>\n\n"
            "Введите нижнее значение курса, при достижении которого бот будет Вас уведомлять:"
        )
        return SETTING_MIN_THRESHOLDS
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное положительное число для интервала мониторинга.")
        return CHOOSING_INTERVAL

async def set_min_threshold(update: Update, context: CallbackContext):
    try:
        context.user_data['min_threshold'] = float((update.message.text).replace(',', '.'))
        await update.message.reply_html(f"\U0001F4C9 <b>Нижняя граница установлена: {context.user_data['min_threshold']}</b>\n\n"
                                        "Введите вверхнее значение курса, при достижении которого бот будет Вас уведомлять:")
        return SETTING_MAX_THRESHOLDS
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное числовое значение для нижней границы!")
        return SETTING_MIN_THRESHOLDS

async def set_max_threshold(update: Update, context: CallbackContext):
    try:
        context.user_data['max_threshold'] = float((update.message.text).replace(',', '.'))
        await update.message.reply_html(f"\U0001F4C8 <b>Верхняя граница установлена: {context.user_data['max_threshold']}</b>\n\n"
                                        "Используйте /monitor, чтобы начать мониторинг.")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("\U0000274C Пожалуйста, введите корректное числовое значение для верхней границы.")
        return SETTING_MAX_THRESHOLDS
