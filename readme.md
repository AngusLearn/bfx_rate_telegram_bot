# BFX Rate Telegram Bot

This is a Telegram bot that sends funding rate notifications of fUSD and fUST using the Bitfinex API.

## Features

-   Get funding rates for various cryptocurrencies.
-   Supports multiple currency pairs (default fUSD, fUST), configurable via `CURRENCIES`.
-   Only send alert if APR >= `ALERT_APR` (default 15%)

![alt text](https://i.imgur.com/xzk8GOy.png)

## Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/anguslearn/bfx_rate_telegram_bot.git
    ```

2.  **Navigate to the project directory:**
    ```sh
    cd bfx_rate_telegram_bot
    ```

3.  **Create a virtual environment:**
    ```sh
    python3 -m venv .venv
    ```

4.  **Activate the virtual environment:**
    ```sh
    source .venv/bin/activate
    ```

5.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create the `.env` file:**

    *   Copy the `env.example` file to `.env`:
        ```sh
        cp env.example .env
        ```
    *   Edit the `.env` file and add your Telegram bot token and chat ID:

        ```env
        BOT_TOKEN=your_telegram_bot_token
        CHAT_ID=your_chat_id

        # Optional (defaults shown)
        CURRENCIES=fUST,fUSD
        ALERT_APR=15
        ```

    *   **IMPORTANT:** Never commit the `.env` file to version control.

## Usage

### Without Docker

1. Add a cronjob (use the venv's Python so dependencies are available):
    ```sh
    12,32,52 * * * * [your_dir]/bfx_rate_telegram_bot/.venv/bin/python [your_dir]/bfx_rate_telegram_bot/bfx_rate.py
    ```

### With Docker

1.  **Build the Docker image:**
    ```sh
    docker build -t bfx-rate-telegram-bot .
    ```

2.  **Run the Docker container:**

    ```sh
    docker compose up -d
    ```
    * The container will start in detached mode.
    * The environment variables must be set in your shell or in a `.env` file next to `docker-compose.yml` (compose reads `BOT_TOKEN`, `CHAT_ID`, and optionally `CURRENCIES` / `ALERT_APR` from there).

### Pull from Docker Hub

You can pull the pre-built image from Docker Hub:

```bash
docker pull anguslearn/bfx_rate_telegram_bot:latest
```

### Docker Image Information
* The docker image is based on the image `python:3.12-slim`.
* The `cron` is installed in the image and runs every 20 minutes (defined in `/etc/cron.d/bfx_rate_cron`).
* The container exports its environment to `/etc/environment` on start so the cron jobs can see `BOT_TOKEN` and `CHAT_ID`.
* The log of the cron is in `/var/log/cron.log` inside the container.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

-   [Bitfinex API](https://docs.bitfinex.com/docs)
