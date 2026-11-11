#!/usr/bin/env python3
"""Bitfinex funding-rate monitor that alerts via Telegram.

Rate conventions (verified against the live Bitfinex API):
- /funding/stats/{currency}/hist field [3] is the daily FRR *divided by 365*,
  so daily FRR % = frr * 365 * 100 and APR % = frr * 365 * 365 * 100.
- Book and trade rates are already daily fractions: APR % = rate * 365 * 100.
"""
import os
import sys
import time

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration (see env.example)
BASE_URL = "https://api-pub.bitfinex.com/v2"
HTTP_TIMEOUT = 10  # seconds per request
HTTP_RETRIES = 3

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CURRENCIES = [c.strip() for c in os.getenv("CURRENCIES", "fUST,fUSD").split(",") if c.strip()]
try:
    ALERT_APR = float(os.getenv("ALERT_APR", "15"))  # alert when High APR (%) >= this
except ValueError:
    sys.exit("ALERT_APR must be a number (percent), e.g. 15")


def fetch_json(path, params=None):
    """GET a Bitfinex v2 endpoint with timeout and retries. Returns None on failure."""
    url = f"{BASE_URL}/{path}"
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching {url} (attempt {attempt}/{HTTP_RETRIES}): {e}")
        else:
            # Bitfinex signals some errors with HTTP 200 + ["error", code, message]
            if isinstance(data, list) and data and data[0] == "error":
                print(f"Bitfinex returned an error for {url}: {data}")
                return None
            return data
        if attempt < HTTP_RETRIES:
            time.sleep(2 * attempt)
    return None


def format_amount(amount):
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= 1_000_000_000:
        return f"{sign}{amount / 1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"{sign}{amount / 1_000_000:.2f}M"
    if amount >= 1_000:
        return f"{sign}{amount / 1_000:.2f}K"
    return f"{sign}{amount:.2f}"


def add_money(amount):
    icons = ""
    while amount >= 1_000:
        icons += "💵"
        amount /= 10
    return icons


def add_money_bags(amount):
    icons = ""
    while amount >= 1_000:
        icons += "💰"
        amount /= 10
    return icons


def add_rockets(apr_percent):
    rockets = ""
    while apr_percent >= ALERT_APR:
        rockets += "🚀"
        apr_percent -= 5
    return rockets


def fetch_funding_stats(currency):
    """Latest FRR entry: the daily rate divided by 365 (see module docstring)."""
    data = fetch_json(f"funding/stats/{currency}/hist")
    if not data:
        print(f"No funding stats available for {currency}.")
        return None
    try:
        return float(data[0][3])
    except (TypeError, ValueError, IndexError):
        print(f"Unexpected funding stats payload for {currency}: {data[:1]}")
        return None


def fetch_funding_pool(currency):
    """Total offered/loaned volume from the funding book (top 100 levels).

    Entry layout: [RATE, PERIOD, COUNT, AMOUNT]; AMOUNT is negative for bids.
    """
    data = fetch_json(f"book/{currency}/P0", params={"len": 100})
    if not data:
        print(f"No funding pool data available for {currency}.")
        return None, None
    try:
        amounts = [float(entry[3]) for entry in data]
    except (TypeError, ValueError, IndexError):
        print(f"Unexpected book payload for {currency}.")
        return None, None
    total_offers = sum(a for a in amounts if a > 0)
    total_bids = sum(-a for a in amounts if a < 0)
    return total_offers, total_bids


def fetch_funding_history(currency):
    """Highest daily rate and bought/sold volume of the latest 125 funding trades."""
    data = fetch_json(f"trades/{currency}/hist", params={"limit": 125})
    if not data:
        print(f"No funding history data available for {currency}.")
        return None, None, None
    try:
        rates = [float(trade[3]) for trade in data]
        amounts = [float(trade[2]) for trade in data]
    except (TypeError, ValueError, IndexError):
        print(f"Unexpected trades payload for {currency}.")
        return None, None, None
    highest_rate = max(rates)
    total_bought = sum(a for a in amounts if a > 0)
    total_sold = sum(-a for a in amounts if a < 0)
    return highest_rate, total_bought, total_sold


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "link_preview_options": {"is_disabled": True},
    }
    try:
        response = requests.post(url, json=payload, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        body = response.json()
    except (requests.RequestException, ValueError) as e:
        detail = f" response: {e.response.content}" if getattr(e, "response", None) is not None else ""
        print(f"Error sending message to Telegram: {e}{detail}")
        return False
    if not body.get("ok"):
        print(f"Telegram API error: {body}")
        return False
    print("Message sent to Telegram.")
    return True


def build_message(currency):
    """Build the alert message. Returns (message, high_apr_percent) or None on bad data."""
    frr = fetch_funding_stats(currency)
    total_offers, total_bids = fetch_funding_pool(currency)
    highest_rate, total_bought, total_sold = fetch_funding_history(currency)

    if frr is None or highest_rate is None or total_offers is None or total_bids is None:
        print(f"Error fetching data for {currency}.")
        return None

    high_apr = highest_rate * 100 * 365
    daily_frr = frr * 365 * 100
    frr_apr = frr * 365 * 365 * 100
    message = (
        f"⚠️⚠️⚠️\n"
        f"===[   {currency}   ]===\n"
        f"High: {highest_rate * 100:.4f}% ({high_apr:.2f}% APR)  {add_rockets(high_apr)}\n"
        f"Borrowed: {format_amount(total_bought)}  {add_money_bags(total_bought)}\n"
        f"Loaned: {format_amount(total_sold)}  {add_money_bags(total_sold)}\n"
        f"Bids: {format_amount(total_bids)}  {add_money(total_bids)}\n"
        f"Offers: {format_amount(total_offers)}  {add_money(total_offers)}\n"
        f"FRR: {daily_frr:.5f}% ({frr_apr:.5f}% APR)"
    )
    return message, high_apr


def check_currency(currency):
    """Fetch data and send an alert if the High APR crosses the threshold. True if OK."""
    result = build_message(currency)
    if result is None:
        return False
    message, high_apr = result
    if high_apr >= ALERT_APR:
        return send_telegram_message(message)
    print(f"[{currency}] High APR {high_apr:.2f}% is below the {ALERT_APR}% alert threshold; no message sent.")
    return True


def main():
    missing = [name for name, value in (("BOT_TOKEN", BOT_TOKEN), ("CHAT_ID", CHAT_ID)) if not value]
    if missing:
        sys.exit(f"Missing required environment variable(s): {', '.join(missing)}")
    failures = 0
    for currency in CURRENCIES:
        if not check_currency(currency):
            failures += 1
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
