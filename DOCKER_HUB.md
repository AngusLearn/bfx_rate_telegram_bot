# BFX Rate Telegram Bot

Telegram bot that monitors Bitfinex funding rates (default: fUSD, fUST) and alerts a chat when the highest recent rate crosses an APR threshold.

![Bot alert example](https://i.imgur.com/xzk8GOy.png)

## Features

- Bitfinex public API: FRR, funding book depth, and recent funding trades
- Alert sent only when the highest trade APR ≥ threshold (default 15%)
- Configurable currencies and threshold via environment variables
- Runs on a schedule via cron (host cron or the built-in cron in this image)

## Quick start

```sh
docker run -d --name bfx-rate-bot \
  -e BOT_TOKEN=your_telegram_bot_token \
  -e CHAT_ID=your_chat_id \
  -e CURRENCIES=fUST,fUSD \
  -e ALERT_APR=15 \
  anguslearn/bfx_rate_telegram_bot:latest
```

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — (required) | Telegram bot token from @BotFather |
| `CHAT_ID` | — (required) | Target chat/user id |
| `CURRENCIES` | `fUST,fUSD` | Comma-separated Bitfinex funding symbols |
| `ALERT_APR` | `15` | Minimum High APR (%) that triggers a message |

The container runs cron internally (every 20 minutes); logs are in `/var/log/cron.log`:

```sh
docker logs bfx-rate-bot
```

## Tags

- `latest` / `main` — current main branch
- `sha-<shortsha>` — pinned to a commit
- `<version>` — release tags (e.g. `1.0.0`)

Source, issues and docs: [github.com/AngusLearn/bfx_rate_telegram_bot](https://github.com/AngusLearn/bfx_rate_telegram_bot)
