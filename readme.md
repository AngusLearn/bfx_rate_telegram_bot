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
    TELEGRAM_TOKEN=your_telegram_bot_token
    ```

## Usage

1. Run the bot:
    ```sh
    python bot.py
    ```
2. Open Telegram and start a chat with your bot.
3. Use the following commands to get exchange rates:
    - `/rate BTCUSD` - Get the exchange rate for BTC to USD.
    - `/rate ETHUSD` - Get the exchange rate for ETH to USD.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Bitfinex API](https://docs.bitfinex.com/docs)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
