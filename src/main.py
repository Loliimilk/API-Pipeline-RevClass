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