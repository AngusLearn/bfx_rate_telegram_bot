# BFX Rate Telegram Bot

This is a Telegram bot that provides real-time exchange rates for various cryptocurrencies using the Bitfinex API.

## Features

- Get real-time exchange rates for various cryptocurrencies.
- Supports multiple currency pairs.
- Easy to use commands.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/anguslearn/bfx_rate_telegram_bot.git
    ```
2. Navigate to the project directory:
    ```sh
    cd bfx_rate_telegram_bot
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the project directory and add your Telegram bot token:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    CHAT_ID=your_chat_id
    ```

## Usage

1. Add a cronjob:
    ```sh
    */5 * * * * python [your_dir]/bfx_rate_telegram_bot/bfx_rate.py
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Bitfinex API](https://docs.bitfinex.com/docs)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
