# Тестовое задание в компанию Аналитические программные решения

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-9.4-005571?logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Поисковый сервис по текстам csv-документов. Данные хранятся в **PostgreSQL**, полнотекстовый поиск — через **Elasticsearch**.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** (async) — ORM
- **asyncpg** — асинхронный драйвер PostgreSQL
- **elasticsearch-py** — клиент Elasticsearch
- **Pydantic** — валидация и настройки
- **Docker + Docker Compose** — контейнеризация
- **pytest** — тесты

## Структура проекта

```
├── src/
│ ├── main.py # Точка входа FastAPI
│ ├── router.py # Эндпоинты
│ ├── import_data.py # Скрипт импорта из CSV
│ ├── parser.py # Парсер CSV
│ ├── core/
│ │ ├── config.py # Настройки (pydantic-settings)
│ │ ├── database.py # Движок SQLAlchemy
│ │ └── dependencies.py # FastAPI-зависимости
│ │ └── logger.py # Логирование
│ └── models/
│   └── post.py # Модель Post
├── tests/ # Функциональные тесты
├── docker-compose.yml
├── Dockerfile
├── docs.json # OpenAPI-схема
└── posts.csv # Тестовые данные
```

## Запуск через Docker

```bash
# Клонируем репозиторий
git clone https://github.com/PurpleSwtr/test-assignment-APR.git
cd test-assignment-APR

# Создаём файл окружения из шаблона
cp .env.example .env

# Поднимаем все сервисы (PostgreSQL + Elasticsearch + App)
docker compose up --build -d

# Импортируем данные из posts.csv в БД и Elasticsearch
docker compose exec app python src/import_data.py
```

### Проверка работы

Сервис доступен:

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI схема**: http://localhost:8000/openapi.json

Проверить эндпоинты через терминал:

```bash
# Поиск
curl "http://localhost:8000/posts/search?query=привет"

# Удаление
curl -X DELETE "http://localhost:8000/posts/delete_post/1"
```

Остановить:

```bash
docker compose down
```

## Тесты

### Запуск тестов прямо в Docker

```bash
docker compose exec app pytest tests/ -v
```

### Локально

### Установка зависимостей

```bash
# Создаём окружение
python -m venv .venv

# Активируем
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Установка зависимостей

# через pip
pip install -r requirements.txt
# через uv
uv sync
```

#### Запуск тестов

```bash
# через pytest
pytest tests/ -v
# через uv
uv run pytest tests/ -v
```

## API

### `GET /posts/search?query=<текст>`

Полнотекстовый поиск по постам.

- Ищет в Elasticsearch по полю `text`
- Возвращает до 20 постов, отсортированных по `created_date` (сначала новые)
- В ответе все поля БД: `id`, `rubrics`, `text`, `created_date`

```bash
curl "http://localhost:8000/api/v1/posts/search?query=привет"
```

### `DELETE /posts/delete_post/{post_id}`

Удаляет пост из PostgreSQL и Elasticsearch.

- `200` — успешно
- `404` — пост не найден

```bash
curl -X DELETE "http://localhost:8000/api/v1/posts/delete_post/1"
```

## Документация API

OpenAPI-схема генерируется перед запуском (локально), и сохраняется как [`docs.json`](docs.json) в корне репозитория.

Также её можно открыть через запущенный сервис: `http://localhost:8000/openapi.json`
