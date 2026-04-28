import os
import json
import re
import requests
import pandas as pd
from dotenv import load_dotenv
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

if not API_KEY:
    raise ValueError("API_KEY не найден в .env")

if not MODEL:
    raise ValueError("MODEL не найдена в .env")

INPUT_FILE = "data/input_reviews.csv"
OUTPUT_FILE = "data/output_reviews.csv"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")
df = df[["review_id", "product_name", "rating", "review_text"]]

results = []