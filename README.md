# Currency Monitoring Telegram Bot

This Telegram bot is designed for monitoring currency exchange rates. Users can configure the bot to track specific currencies, set monitoring intervals, and receive notifications based on threshold values.

## Features

- Currency Selection: Choose the currency to monitor (e.g., EUR, USD, JPY)
- Interval Setting: Set the monitoring interval in minutes
- Threshold Alerts: Receive notifications when the currency rate goes beyond specified thresholds
- Graphical Representation: View historical currency rates through graphical charts

## Prerequisites

Before running the bot, make sure you have the following dependencies installed:

- Python 3.x
- Required Python packages (See requirements.txt)

## Setup

1. Clone the repository:

        git clone https://github.com/yourusername/currencyrate_telegram_bot.git
        cd currencyrate_telegram_bot

2. Install dependencies:

        pip install -r requirements.txt

3. Configure API keys:

- Create a Telegram bot via @BotFather and get an API key
- Obtain an API key from the [API Layer](https://apilayer.com/marketplace/currency_data-api) service for currency data

4. Create a .env file in the project root and add your API keys:

        API_KEY_BOT="your_telegram_bot_api_key"
        API_KEY_LAYER="your_currency_layer_api_key"

5. Run the bot:

        python your_bot_script.py

## Usage

1. Start the bot by sending /start to initiate the setup process
2. Use /settings to configure monitoring preferences
3. Follow the bot's instructions to set the currency, monitoring interval, and threshold values
4. Start monitoring with /monitor
5. Check the latest currency rate with /currency
6. Cancel monitoring with /cancel at any time
