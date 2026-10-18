# Document Search API

REST API для полнотекстового поиска и удаления документов с использованием FastAPI, PostgreSQL и Elasticsearch.

## Стек технологий

- **Python 3.13**, FastAPI, Pydantic
- **PostgreSQL 17**, SQLAlchemy, Alembic
- **Elasticsearch 8.19**
- **Docker Compose**
- **pytest**

## Возможности

- Импорт документов из CSV в PostgreSQL.
- Индексация документов в Elasticsearch.
- Полнотекстовый поиск с поддержкой русского языка и базовым поиском по другим языкам.
- Выдача до 20 документов, отсортированных по дате создания (от новых к старым).
- Удаление документа из PostgreSQL и Elasticsearch.
- Автоматическая миграция БД, импорт и индексация при запуске через Docker Compose.
- Автоматическая документация API через Swagger UI и OpenAPI.

## Запуск проекта

**Требования:** Docker Desktop с поддержкой Docker Compose.

1. Клонировать репозиторий:

```bash
git clone git@github.com:Groomet/doc-search-api.git
cd doc_search
```

2. Создать `.env` на основе `.env.example`.

Для PowerShell:

```powershell
Copy-Item .env.example .env
```

Для Linux/macOS:

```bash
cp .env.example .env
```

3. Запустить сервисы:

```bash
docker compose up --build -d
```

При первом запуске контейнер `init` автоматически:

1. Применит миграции Alembic.
2. Импортирует данные из `data/posts.csv`.
3. Создаст или обновит индекс Elasticsearch.
4. Проиндексирует документы из PostgreSQL.

После успешной инициализации запустится FastAPI.

## API

По умолчанию API доступен по адресу `http://127.0.0.1:8000`.

Интерактивная документация Swagger UI:

`http://127.0.0.1:8000/docs`

### GET /documents/search

Поиск документов по тексту.

Пример:

```http
GET /documents/search?q=новости
```

Результат — массив из максимум 20 документов, отсортированных по `created_date` по убыванию.

### DELETE /documents/{document_id}

Удаляет документ из PostgreSQL и Elasticsearch.

Пример:

```http
DELETE /documents/42
```

Если документ не найден, возвращается HTTP 404.

### GET /health

Проверка доступности приложения.

```json
{
  "status": "ok"
}
```

## Конфигурация

Параметры задаются в `.env`:

| Переменная | Назначение |
|---|---|
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Название базы данных |
| `POSTGRES_PORT` | Порт PostgreSQL на хосте |
| `ELASTIC_PORT` | Порт Elasticsearch на хосте |
| `API_PORT` | Порт FastAPI на хосте |

Внутри Docker сервисы взаимодействуют по именам `postgres` и `elasticsearch`.

## Тестирование

Создать виртуальное окружение, активировать его и установить зависимости для разработки:

```bash
pip install -r requirements-dev.txt
```

Запустить тесты:

```bash
python -m pytest -v
```

Тесты проверяют основные сценарии поиска, удаления, валидации запросов и обработки ошибок.

## OpenAPI

Спецификация API находится в файле `docs.json`.

## Остановка

```bash
docker compose down
```

Данные PostgreSQL и Elasticsearch сохраняются в Docker volumes между запусками.

## Ограничения

- Для казахского и кыргызского языков используется базовый поиск без полноценной морфологической обработки.
- Согласованность PostgreSQL и Elasticsearch при удалении реализована по принципу best-effort с попыткой восстановления индекса в случае ошибки БД.
- Тесты эндпоинтов используют моки внешних зависимостей и не заменяют полноценные интеграционные тесты.