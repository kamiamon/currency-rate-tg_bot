"""
Telegram bot main module.
"""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from src.currency_settings import (
    start,
    cancel,
    settings,
    set_currency,
    set_interval,
    set_min_threshold,
    set_max_threshold,
)
from src.currency_monitor import (
    monitor,
    currency,
)
from src.constants import (
    TELEGRAM_BOT_TOKEN,
    SELECTING,
    CHOOSING_CURRENCY,
    CHOOSING_INTERVAL,
    SETTING_MIN_THRESHOLDS,
    SETTING_MAX_THRESHOLDS,
)

def main():
    """
    Main function to start the Telegram bot.
    """
    print("Bot started!")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING: [CommandHandler("settings", settings)],
            CHOOSING_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_currency)],
            CHOOSING_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_interval)],
            SETTING_MIN_THRESHOLDS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_min_threshold)
            ],
            SETTING_MAX_THRESHOLDS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_max_threshold)
            ],
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
