# API-Pipeline-Review-Classification

## Описание проекта

Классификация отзывов: скрипт читает отзывы → LLM определяет тональность (positive/negative/neutral) и тему (кратко пересказ комментария и короткое название товара) → результат в CSV.

## Входные данные

Файл: `data/input_reviews.csv`

Содержит столбцы:
- `review_id` - ID отзыва  
- `product_name` - название товара  
- `rating` - оценка  
- `review_text` - текст отзыва  

## Выходные данные

Файл: `data/output_reviews.csv`

Содержит столбцы: 
- `review_id`
- `sentiment` - тональность (положительный / отрицательный / нейтральный)
- `topic` - тема (1–2 слова)
- `summary` - краткое содержание (до 10 слов)

## Технический стек

- Python
- requests (работа с API)
- pandas (обработка CSV)
- python-dotenv (переменные окружения)

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Loliimilk/API-Pipeline-RevClass
cd API-Pipeline-RevClass
```
### 2. Установить зависимости
```bash
pip install -r requirements.txt
```
### 3. Создать файл .env
Укажите актуальный API_KEY, MODEL и API_URL в созданном файле как в нем описано
```bash
cp .env.example .env
```
или
```bash
copy .env.example .env
```
### 4. Запуск скрипта
```bash
python src/main.py
```


---

## Особенности реализации
- Используется **батчевая обработка** (по 5 отзывов за запрос)
- Есть обработка ошибок:
    - rate limit (429)
    - проблемы сети
    - некорректный JSON
- Если батч не обработался - данные помечаются как `"ошибка"`
- Ответ модели очищается перед парсингом JSON
- Поддерживается **русский язык** (и вход, и выход)
