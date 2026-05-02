import os
import sys
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# Настройка консоли
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

# Константы
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
INPUT_FILE = "data/input_reviews.csv"
OUTPUT_FILE = "data/output_reviews.csv"
BATCH_SIZE = 5

def extract_json_array(text):
    try:
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            clean_content = text[start:end+1]
            return json.loads(clean_content)
        return json.loads(text)
    except (ValueError, json.JSONDecodeError):
        return None
    
def fetch_batch_analysis(batch_data):
    reviews_text = ""
    for _, row in batch_data.iterrows():
        reviews_text += f"ID: {row['review_id']}\nТовар: {row['product_name']}\nОтзыв: {row['review_text']}\n---\n"

    prompt = f"Определи тональность и тему. Верни ТОЛЬКО JSON-массив [{{'review_id': '...', 'sentiment': '...', 'topic': '...', 'summary': '...'}}].\nОтзывы:\n{reviews_text}"
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1000
    }

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=40)
            if resp.status_code == 429:
                time.sleep(15)
                continue
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return extract_json_array(content)
        except Exception as e:
            print(f"Ошибка попытки {attempt}: {e}")
            time.sleep(5)
    return None

def main():
    if not API_KEY or not MODEL:
        print("Ошибка: Проверьте .env файл!")
        return

    df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
    all_results = []

    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i : i + BATCH_SIZE]
        print(f"Обработка: {i+1} - {min(i+BATCH_SIZE, len(df))}")
        
        batch_results = fetch_batch_analysis(batch)
        
        if batch_results:
            all_results.extend(batch_results)
        else:
            # Если батч не удался, создаем пустые записи
            for _, row in batch.iterrows():
                all_results.append({"review_id": row["review_id"], "sentiment": "ошибка"})
        
        time.sleep(3) # Пауза для стабильности

    save_results(all_results)