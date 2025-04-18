import requests
from bs4 import BeautifulSoup
import schedule
import time
import json
import os
from telegram import Bot
import asyncio

# Конфигурация
CONFIG = {
    "urls": [
        {
            "url": "https://ft.org.ua/performances/kaligula",
            "selector": ".performanceHero__wrapper",
            "name": "Kaligula"
        },
        {
            "url": "https://ft.org.ua/performances/koriolan",
            "selector": ".performanceHero__wrapper",
            "name": "koriolan"
        },
        {
            "url": "https://ft.org.ua/performances/konotopska-vidma",
            "selector": ".performanceHero__wrapper",
            "name": "konotopska-vidma"
        },
        {
            "url": "https://ft.org.ua/performances/makbet",
            "selector": ".performanceHero__wrapper",
            "name": "makbet"
        },
        {
            "url": "https://ft.org.ua/performances/mariia-stiuart",
            "selector": ".performanceHero__wrapper",
            "name": "mariia-stiuart"
        },
        {
            "url": "https://ft.org.ua/performances/per-giunt",
            "selector": ".performanceHero__wrapper",
            "name": "per-giunt"
        },
        {
            "url": "https://ft.org.ua/performances/tartiuf",
            "selector": ".performanceHero__wrapper",
            "name": "tartiuf"
        }
    ],
    "telegram_token": "7942085933:AAHG6aqaA7e0yJL61N2HFNDbLxo3a-i9ObA",
    "chat_id": "397563510",
    "check_interval": 300,
    "state_file": "page_state.json"
}

# Заголовки для запросов
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Инициализация бота
bot = Bot(token=CONFIG["telegram_token"])

def load_state():
    if os.path.exists(CONFIG["state_file"]):
        with open(CONFIG["state_file"], "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(CONFIG["state_file"], "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_page_content(url, selector):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.select_one(selector)
        return element.text.strip() if element else None
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CONFIG["chat_id"], text=message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

def check_pages():
    print("Проверка страниц...")
    state = load_state()
    new_state = {}

    for page in CONFIG["urls"]:
        url = page["url"]
        selector = page["selector"]
        name = page["name"]

        current_content = get_page_content(url, selector)
        if current_content is None:
            print(f"Не удалось получить содержимое для {name}")
            continue

        new_state[url] = current_content

        if url not in state:
            print(f"Первая проверка для {name}, состояние сохранено")
        elif state[url] != current_content:
            message = f"Изменение на странице '{name}' ({url}):\nНовое содержимое:\n{current_content[:200]}..."
            asyncio.run(send_telegram_message(message))
            print(f"Обнаружено изменение для {name}")

    save_state(new_state)

def main():
    # Отправка тестового сообщения при запуске
    asyncio.run(send_telegram_message("🎭 Бот успешно запущен и следит за изменениями на сайте!"))

    # Планирование проверок
    schedule.every(CONFIG["check_interval"]).seconds.do(check_pages)

    # Первая проверка
    check_pages()

    # Основной цикл
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
