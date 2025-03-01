#!/usr/bin/env python3
import requests
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# API endpoints
base_url = "https://api-pub.bitfinex.com/v2"
telegram_url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"
chat_id = os.getenv('CHAT_ID')

# Debugging: Print BOT_TOKEN and CHAT_ID to ensure they are loaded correctly
# print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN')}")
# print(f"CHAT_ID: {chat_id}")

def format_amount(amount):
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{amount / 1_000:.2f}K"
    else:
        return f"{amount:.2f}"

def fetch_funding_stats(currency):
    try:
        url = f"{base_url}/funding/stats/{currency}/hist"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data:
            latest_entry = data[0]
            frr = latest_entry[3]  # Flash Return Rate (daily rate)
            return frr
        else:
            print(f"No funding stats available for {currency}.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding stats for {currency}: {e}")
        return None

def fetch_funding_pool(currency):
    try:
        url = f"{base_url}/book/{currency}/P0?len=100"
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            offers = [offer for offer in data if float(offer[3]) > 0]
            bids = [bid for bid in data if float(bid[3]) < 0]
            
            total_offers = sum(float(offer[3]) for offer in offers)
            total_bids = sum(abs(float(bid[3])) for bid in bids)
            
            return total_offers, total_bids
        else:
            print(f"No funding pool data available for {currency}.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding pool data for {currency}: {e}")
        return None, None

def fetch_funding_history(currency):
    try:
        # Fetch the latest 125 trades for the given currency in the last 10 minutes
        url = f"{base_url}/trades/{currency}/hist?limit=125"
        headers = {
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            highest_rate = max(float(trade[3]) for trade in data)
            total_bought = sum(float(trade[2]) for trade in data if float(trade[2]) > 0)
            total_sold = sum(abs(float(trade[2])) for trade in data if float(trade[2]) < 0)
            
            return highest_rate, total_bought, total_sold
        else:
            print(f"No funding history data available for {currency}.")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding history data for {currency}: {e}")
        return None, None, None

def send_telegram_message(message):
    try:
        payload = {
            'chat_id': chat_id,
            'text': message,
            'disable_web_page_preview': True
        }
        # print(f"Payload: {payload}")  # Debugging: Print the payload
        response = requests.post(telegram_url, json=payload)  # Use json=payload to send JSON data
        response.raise_for_status()
        # print(f"Message sent to Telegram: {message}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        print(f"Response content: {e.response.content}")  # Print the response content for debugging

def fetch_and_print_data(currency):
    frr = fetch_funding_stats(currency)
    total_offers, total_bids = fetch_funding_pool(currency)
    highest_rate, total_bought, total_sold = fetch_funding_history(currency)

    if frr is not None and total_offers is not None and total_bids is not None and highest_rate is not None:
        def add_money(amount):
            money = ""
            while amount >= 1000:
                money += "💵"
                amount /= 10
            return money
        
        def add_money_bags(amount):
            money_bags = ""
            while amount >= 1000:
                money_bags += "💰"
                amount /= 10
            return money_bags

        def add_rockets(rate):
            rockets = ""
            while rate >= 15:
                rockets += "🚀"
                rate -= 5
            return rockets

        message = (
            f"⚠️⚠️⚠️\n"
            f"===[   {currency}   ]===\n"
            f"High: {highest_rate * 100:.4f}% ({highest_rate * 100 * 365:.2f}% APR)  {add_rockets(highest_rate * 100 * 365)}\n"
            f"Borrowed: {format_amount(total_bought)}  {add_money_bags(total_bought)}\n"
            f"Loaned: {format_amount(total_sold)}  {add_money_bags(total_sold)}\n"
            f"Bids: {format_amount(total_bids)}  {add_money(total_bids)}\n"
            f"Offers: {format_amount(total_offers)}  {add_money(total_offers)}\n"
            f"FRR: {frr * 365 * 100:.5f}% ({frr * 100 * 365 * 365:.5f}% APR)"
        )
        if highest_rate * 100 * 365 >= 15:
            send_telegram_message(message)
    else:
        print(f"Error fetching data for {currency}.")

# Fetch and print data for fUST and fUSD
fetch_and_print_data("fUST")
fetch_and_print_data("fUSD")

