import requests
from bs4 import BeautifulSoup
import time
import json
from telegram import Bot

# === KONFIGURÁCIA ===
BOT_TOKEN = '8057031273:AAHTay7x6nk0HrNj-wqPxObRZZLNzmMxxgc'  # Vlož svoj token od BotFather
CHAT_ID = -1002374985515      # Vlož ID tvojej skupiny
URL = 'https://www.pelikan.sk/sk/akciove-letenky/DF:VIE'
CHECK_INTERVAL = 300  # čas medzi kontrolami (v sekundách)

bot = Bot(token=BOT_TOKEN)

# === Na uchovávanie predchádzajúcich leteniek ===
sent_deals_file = 'sent_deals.json'

def load_sent_deals():
    try:
        with open(sent_deals_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_sent_deals(deals):
    with open(sent_deals_file, 'w') as f:
        json.dump(deals, f)

# === Scraper ===
def get_latest_deals():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    deals = []

    for deal in soup.select('.fare-card'):  # Závisí od layoutu
        try:
            title = deal.select_one('.fare-card__header').get_text(strip=True)
            price = deal.select_one('.fare-card__price').get_text(strip=True)
            link = deal.select_one('a')['href']
            full_link = 'https://www.pelikan.sk' + link

            deals.append({
                'title': title,
                'price': price,
                'link': full_link
            })
        except Exception as e:
            print(f"Chyba pri spracovaní: {e}")
            continue

    return deals

# === Hlavná slučka ===
def main():
    print("Spúšťam sledovanie leteniek...")
    sent_deals = load_sent_deals()

    while True:
        try:
            current_deals = get_latest_deals()
            new_deals = [d for d in current_deals if d['link'] not in sent_deals]

            for deal in new_deals:
                message = f"✈️ *{deal['title']}*\n💸 Cena: *{deal['price']}*\n🔗 [Zobraziť ponuku]({deal['link']})"
                bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
                sent_deals.append(deal['link'])

            if new_deals:
                save_sent_deals(sent_deals)

        except Exception as e:
            print(f"Chyba: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
