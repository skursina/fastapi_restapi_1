# 📋 Advertisement API

Асинхронный REST API для создания, просмотра, изменения, удаления и поиска объявлений о продаже/покупке товаров.

Проект выполнен на **FastAPI** с использованием **SQLAlchemy Async**, **PostgreSQL** и **Docker Compose**.

---

## 🛠 Технологии

- 🐍 Python 3.13
- ⚡ FastAPI
- 🔄 SQLAlchemy 2.x Async
- 🐘 PostgreSQL 16
- 🔌 asyncpg
- 📦 Pydantic 2
- 🐳 Docker
- 🧩 Docker Compose
- 🚀 Uvicorn

Все операции с базой данных выполняются асинхронно.

---

## 📁 Структура проекта

```text
fastapi_advertisements/
│
├── app/
│   ├── __init__.py
│   ├── database.py       # Подключение к PostgreSQL
│   ├── main.py           # FastAPI-приложение и API endpoints
│   ├── models.py         # SQLAlchemy-модели
│   └── schemas.py        # Pydantic-схемы
│
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🏗 Архитектура

Приложение состоит из двух Docker-контейнеров:

```text
                HTTP
                 │
                 ▼
        ┌─────────────────┐
        │   FastAPI API   │
        │   Python 3.13   │
        └────────┬────────┘
                 │
          SQLAlchemy Async
                 │
                 ▼
        ┌─────────────────┐
        │   PostgreSQL    │
        │       16        │
        └─────────────────┘
```

Контейнеры находятся в одной Docker-сети.

FastAPI обращается к PostgreSQL по адресу:

```text
db:5432
```

Порт PostgreSQL наружу не публикуется, поэтому конфликт с локальным PostgreSQL отсутствует.

---

# 🚀 Запуск проекта

## 1. Клонирование репозитория

```bash
git clone https://github.com/skursina/fastapi_restapi_1.git
cd fastapi_advertisements
```

---

## 2. Запуск Docker Compose

Сборка и запуск приложения:

```bash
docker compose up --build
```

После запуска будут созданы два контейнера:

- `advertisements_api`
- `advertisements_postgres`

PostgreSQL перед запуском API проходит проверку готовности через `healthcheck`.

---

## 3. Проверка контейнеров

В отдельном терминале:

```bash
docker compose ps
```

Ожидаемый результат:

```text
NAME                       STATUS
advertisements_postgres    Up (healthy)
advertisements_api         Up
```

---

## 4. Проверка API

Откройте:

```text
http://localhost:8000/
```

Ответ:

```json
{
    "message": "Advertisement API работает"
}
```

---

# 📚 Swagger UI

FastAPI автоматически создаёт интерактивную документацию API.

Swagger UI:

```text
http://localhost:8000/docs
```

Через Swagger можно выполнять запросы к API непосредственно из браузера.

Также доступна альтернативная документация:

```text
http://localhost:8000/redoc
```

---

# 🔌 API

## Создание объявления

### `POST /advertisement`

Создаёт новое объявление.

### Request

```json
{
    "title": "Продам ноутбук",
    "description": "Ноутбук в хорошем состоянии",
    "price": 75000,
    "author": "Светлана"
}
```

### Response

```json
{
    "id": 1,
    "title": "Продам ноутбук",
    "description": "Ноутбук в хорошем состоянии",
    "price": 75000,
    "author": "Светлана",
    "created_at": "2026-10-01T12:30:00Z"
}
```

---

## Получение объявления

### `GET /advertisement/{advertisement_id}`

Получает объявление по его идентификатору.

Пример:

```http
GET /advertisement/1
```

Ответ:

```json
{
    "id": 1,
    "title": "Продам ноутбук",
    "description": "Ноутбук в хорошем состоянии",
    "price": 75000,
    "author": "Светлана",
    "created_at": "2026-10-01T12:30:00Z"
}
```

Если объявление не найдено:

```http
404 Not Found
```

---

## Изменение объявления

### `PATCH /advertisement/{advertisement_id}`

Позволяет изменить только необходимые поля объявления.

Например:

```json
{
    "price": 70000
}
```

Можно изменить несколько полей:

```json
{
    "title": "Продам ноутбук Lenovo",
    "price": 68000
}
```

Неуказанные поля сохраняют прежние значения.

---

## Удаление объявления

### `DELETE /advertisement/{advertisement_id}`

Удаляет объявление.

Пример:

```http
DELETE /advertisement/1
```

Ответ:

```json
{
    "message": "Advertisement deleted"
}
```

---

# 🔎 Поиск объявлений

### `GET /advertisement`

Поддерживается поиск по параметрам:

- `title`
- `description`
- `author`
- `price`
- `created_at`

Параметры можно использовать отдельно или совместно.

### Поиск по названию

```http
GET /advertisement?title=ноутбук
```

### Поиск по автору

```http
GET /advertisement?author=Светлана
```

### Поиск по цене

```http
GET /advertisement?price=70000
```

### Поиск по дате создания

```http
GET /advertisement?created_at=2026-01-06
```

### Комбинированный поиск

```http
GET /advertisement?author=Светлана&price=70000
```

Для поиска по текстовым полям используется частичное совпадение.

Например:

```text
?title=ноут
```

найдёт объявления с названиями:

```text
Ноутбук Lenovo
Игровой ноут
Ноутбук в хорошем состоянии
```

---

# 🗄 Модель данных

В PostgreSQL создаётся таблица:

```text
advertisements
```

| Поле | Тип | Описание |
|---|---|---|
| `id` | Integer | Уникальный идентификатор |
| `title` | String | Заголовок объявления |
| `description` | Text | Описание |
| `price` | Integer | Цена |
| `author` | String | Автор объявления |
| `created_at` | DateTime | Дата и время создания |

---

# ⚡ Асинхронность

Приложение использует асинхронный стек:

```text
FastAPI
    ↓
async def
    ↓
SQLAlchemy Async
    ↓
asyncpg
    ↓
PostgreSQL
```

Например, получение записи из базы:

```python
advertisement = await db.get(
    Advertisement,
    advertisement_id,
)
```

А выполнение SQL-запроса:

```python
result = await db.execute(query)
```

Использование асинхронного драйвера `asyncpg` позволяет не блокировать обработку других HTTP-запросов во время ожидания операций с базой данных.

---

# 🐳 Docker

## Сборка

```bash
docker compose build
```

## Запуск

```bash
docker compose up
```

## Запуск в фоновом режиме

```bash
docker compose up -d
```

## Просмотр контейнеров

```bash
docker compose ps
```

## Просмотр логов API

```bash
docker compose logs api
```

## Просмотр логов PostgreSQL

```bash
docker compose logs db
```

## Остановка

```bash
docker compose down
```

## Остановка с удалением данных PostgreSQL

```bash
docker compose down -v
```

> ⚠️ Команда `docker compose down -v` удаляет Docker volume с базой данных.

---

# 🧪 Пример сценария проверки API

Последовательность тестирования:

### 1. Создать объявление

```http
POST /advertisement
```

```json
{
    "title": "Велосипед",
    "description": "Горный велосипед",
    "price": 30000,
    "author": "Иван"
}
```

### 2. Получить объявление

```http
GET /advertisement/1
```

### 3. Изменить цену

```http
PATCH /advertisement/1
```

```json
{
    "price": 27000
}
```

### 4. Найти объявления автора

```http
GET /advertisement?author=Иван
```

### 5. Удалить объявление

```http
DELETE /advertisement/1
```

### 6. Проверить удаление

```http
GET /advertisement/1
```

Ожидаемый ответ:

```http
404 Not Found
```

---

# 🔐 Валидация

Pydantic выполняет проверку входных данных.

Например:

- `title` не может быть пустым;
- `description` не может быть пустым;
- `price` не может быть отрицательным;
- `author` не может быть пустым;
- длина `title` и `author` ограничена 255 символами.

При некорректных данных FastAPI возвращает:

```http
422 Unprocessable Entity
```

---

# 📌 Особенности проекта

- ✅ полностью асинхронное API;
- ✅ PostgreSQL вместо хранения данных в памяти;
- ✅ SQLAlchemy 2.x Async;
- ✅ Pydantic 2;
- ✅ автоматическая валидация данных;
- ✅ автоматическая документация Swagger;
- ✅ Docker-контейнеризация;
- ✅ проверка готовности PostgreSQL через `healthcheck`;
- ✅ частичное обновление через `PATCH`;
- ✅ поиск по нескольким параметрам;
- ✅ обработка ошибки `404`;
- ✅ автоматическое создание таблицы при запуске приложения.

---

# 👩‍💻 Автор

**Svetlana K.**

Учебный проект по разработке асинхронного REST API на Python.
