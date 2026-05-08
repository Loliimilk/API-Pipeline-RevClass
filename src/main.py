import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import sys
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
API_URL = os.getenv("API_URL")

INPUT_FILE = "data/input_reviews.csv"
OUTPUT_FILE = "data/output_reviews.csv"

if not API_KEY or not MODEL:
    raise ValueError("Нет API_KEY или MODEL в .env")

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
total_rows = len(df)

results = []
BATCH_SIZE = 5

for i in range(0, total_rows, BATCH_SIZE):
    batch = df.iloc[i:i+BATCH_SIZE]
    print(f"Обрабатываю отзывы с {i+1} по {min(i+BATCH_SIZE, total_rows)} из {total_rows}...")

    reviews_text = ""
    for _, row in batch.iterrows():
        reviews_text += f"ID: {row['review_id']}\nТовар: {row['product_name']}\nОценка: {row['rating']}\nОтзыв: {row['review_text']}\n---\n"

    prompt = f"""
Определи тональность и тему для каждого отзыва из списка.

Верни ТОЛЬКО валидный JSON-массив (начинается с [ и заканчивается ]). Без Markdown-разметки.
Формат ответа должен быть строго такой:
[
  {{
    "review_id": "ID из текста (сохрани как есть)",
    "sentiment": "положительный | отрицательный | нейтральный",
    "topic": "1-2 слова",
    "summary": "кратко до 10 слов"
  }}
]

Вот отзывы:
{reviews_text}
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 800 
    }

    max_retries = 3
    success = False

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

            if response.status_code == 429:
                print(f"  [!] Rate limit, жду 15 сек... (Попытка {attempt+1}/{max_retries})")
                time.sleep(15)
                continue

            if response.status_code != 200:
                print(f"  [!] Ошибка API: {response.status_code}")
                break

            content = response.json()["choices"][0]["message"]["content"].strip()
            
            start = content.find('[')
            end = content.rfind(']')
            
            if start != -1 and end != -1:
                clean_json = content[start:end+1]
            else:
                clean_json = content

            batch_results = json.loads(clean_json)
            
            if isinstance(batch_results, list):
                results.extend(batch_results)
                success = True
                print("  Успешно!")
                time.sleep(3)
                break
            else:
                raise ValueError("Модель вернула не список (массив).")

        except Exception as e:
            print(f"  [!] Ошибка парсинга или сети: {e}")
            time.sleep(5)
            continue

    if not success:
        print(f"  [!!!] Пропуск батча (строки {i+1}-{min(i+BATCH_SIZE, total_rows)})")
        for _, row in batch.iterrows():
            results.append({
                "review_id": row["review_id"],
                "sentiment": "ошибка",
                "topic": "ошибка",
                "summary": "ошибка"
            })

pd.DataFrame(results).to_csv(OUTPUT_FILE, sep=";", index=False, encoding="utf-8-sig")

OUTPUT_JSON = OUTPUT_FILE.replace('.csv', '.json')
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nГотово! Сохранено в {OUTPUT_FILE} и {OUTPUT_JSON}")
print(f"Всего записей в файле: {len(results)}")
