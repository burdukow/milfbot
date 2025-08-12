import requests
import json
import time

# Если хотите авторизацию, вставьте сюда свои данные
USERNAME = ""  # Ваш логин на Danbooru
API_KEY = ""   # Ваш API key (в профиле -> API key)

OUTPUT_FILE = "danbooru_tags.json"
BASE_URL = "https://danbooru.donmai.us/tags.json"
LIMIT = 1000  # максимум у API
PAGE = 1

all_tags = []

while True:
    params = {
        "limit": LIMIT,
        "page": PAGE,
        "search[order]": "count"  # можно убрать или изменить порядок
    }

    print(f"Скачиваю страницу {PAGE}...")
    if USERNAME and API_KEY:
        r = requests.get(BASE_URL, params=params, auth=(USERNAME, API_KEY))
    else:
        r = requests.get(BASE_URL, params=params)

    if r.status_code != 200:
        print(f"Ошибка {r.status_code}: {r.text}")
        break

    tags = r.json()
    if not tags:
        print("Достигнут конец списка.")
        break

    all_tags.extend(tags)
    PAGE += 1

    time.sleep(1)  # пауза чтобы не нагружать API

# Записываем в один файл
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_tags, f, ensure_ascii=False, indent=2)

print(f"Сохранено {len(all_tags)} тегов в {OUTPUT_FILE}")
