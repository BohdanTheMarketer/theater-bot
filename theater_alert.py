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
            "selector": ".performanceHero__wrapper",  # CSS-селектор элемента для отслеживания
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
    "telegram_token": "7942085933:AAHG6aqaA7e0yJL61N2HFNDbLxo3a-i9ObA",  # Токен бота
    "chat_id": "397563510",  # ID чата для уведомлений
    "check_interval": 300,  # Интервал проверки в секундах (5 минут)
    "state_file": "page_state.json"  # Файл для хранения состояния
}

# Заголовки для запросов, чтобы избежать блокировки
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Инициализация Telegram-бота
bot = Bot(token=CONFIG["telegram_token"])

def load_state():
    """Загружает предыдущее состояние страниц из файла."""
    if os.path.exists(CONFIG["state_file"]):
        with open(CONFIG["state_file"], "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    """Сохраняет текущее состояние страниц в файл."""
    with open(CONFIG["state_file"], "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_page_content(url, selector):
    """Получает содержимое элемента на странице по URL и селектору."""
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
    """Отправляет сообщение в Telegram."""
    try:
        await bot.send_message(chat_id=CONFIG["chat_id"], text=message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")

def check_pages():
    """Проверяет изменения на страницах и отправляет уведомления."""
    print("Проверка страниц...")
    state = load_state()
    new_state = {}

    for page in CONFIG["urls"]:
        url = page["url"]
        selector = page["selector"]
        name = page["name"]

        # Получаем текущее содержимое
        current_content = get_page_content(url, selector)
        if current_content is None:
            print(f"Не удалось получить содержимое для {name}")
            continue

        # Сохраняем новое состояние
        new_state[url] = current_content

        # Сравниваем с предыдущим состоянием
        if url not in state:
            print(f"Первая проверка для {name}, состояние сохранено")
        elif state[url] != current_content:
            message = f"Изменение на странице '{name}' ({url}):\nНовое содержимое:\n{current_content[:200]}..."
            asyncio.run(send_telegram_message(message))
            print(f"Обнаружено изменение для {name}")

    # Сохраняем новое состояние
    save_state(new_state)

def main():

    # Планируем проверку каждые 5 минут
    schedule.every(CONFIG["check_interval"]).seconds.do(check_pages)

    # Первая проверка при запуске
    check_pages()

    # Основной цикл
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
