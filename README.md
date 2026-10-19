# Document Search API

Простой REST API для полнотекстового поиска и удаления документов на базе **FastAPI**, **PostgreSQL** и **Elasticsearch**.

## Технологии

- Python 3.13, FastAPI, Pydantic
- PostgreSQL 17, SQLAlchemy, Alembic
- Elasticsearch 8.19
- Docker Compose
- pytest

## Возможности

- Импорт документов из `data/posts.csv` в PostgreSQL.
- Индексация текстов в Elasticsearch.
- Асинхронные поиск и удаление через `AsyncSession` (SQLAlchemy) и `AsyncElasticsearch`.
- Поиск по русскому тексту и базовый поиск по текстам на других языках.
- Возврат до 20 найденных документов со всеми полями БД в порядке убывания `created_date`.
- Удаление документа по `id` из PostgreSQL и Elasticsearch.
- Автоматические миграции, импорт CSV и индексация при запуске через Docker Compose.
- Документация OpenAPI и интерактивный Swagger UI.

## Быстрый запуск

**Требования:** Docker с поддержкой Docker Compose.

1. Клонируйте репозиторий и перейдите в его каталог:

   ```bash
   git clone https://github.com/Groomet/doc-search-api.git
   cd doc-search-api
   ```

2. Создайте `.env` на основе примера:

   **Windows PowerShell:**

   ```powershell
   Copy-Item .env.example .env
   ```

   **Linux/macOS:**

   ```bash
   cp .env.example .env
   ```

   При необходимости измените параметры в `.env`.

3. Соберите и запустите сервисы:

   ```bash
   docker compose up --build -d
   ```

При первом запуске служебный контейнер `init` последовательно:

1. Применяет миграции Alembic.
2. Импортирует документы из `data/posts.csv` в PostgreSQL.
3. Создаёт или обновляет поисковый индекс Elasticsearch.
4. Индексирует документы из PostgreSQL.

После успешной инициализации запускается API. Проверить состояние контейнеров можно командой:

```bash
docker compose ps -a
```

Нормальное состояние: PostgreSQL и Elasticsearch — `healthy`, `init` — `Exited (0)`, API — `Up`.

## API

По умолчанию API доступен по адресу **http://127.0.0.1:8000** (порт настраивается через `API_PORT`).

Swagger UI: **http://127.0.0.1:8000/docs**  
OpenAPI JSON через API: **http://127.0.0.1:8000/openapi.json**

### `GET /documents/search`

Принимает параметр `q` — текст поискового запроса. Возвращает до 20 документов, отсортированных по дате создания от новых к старым. 
Каждый результат содержит `id`, `rubrics`, `text` и `created_date`.

Пример:

```http
GET /documents/search?q=новости
```

### `DELETE /documents/{document_id}`

Удаляет документ по идентификатору из PostgreSQL и Elasticsearch.

Пример:

```http
DELETE /documents/42
```

Если документ отсутствует в PostgreSQL, возвращается `404 Not Found`.

### `GET /health`

Проверка запуска приложения:

```json
{
  "status": "ok"
}
```

## Конфигурация

Параметры задаются в файле `.env`:

| Переменная | Назначение |
|---|---|
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Имя базы данных |
| `POSTGRES_PORT` | Порт PostgreSQL на компьютере |
| `ELASTIC_PORT` | Порт Elasticsearch на компьютере |
| `API_PORT` | Порт HTTP API на компьютере |

Внутри сети Docker API обращается к PostgreSQL по адресу `postgres:5432`, а к Elasticsearch — по адресу `elasticsearch:9200`. Внешние порты настраиваются отдельно и не меняют внутренние адреса сервисов.

## Тестирование

Для запуска тестов локально нужен Python 3.13.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

В проекте 11 тестов, покрывающих ответы API при поиске и удалении, порядок выдачи, проверку входных данных и отдельные сценарии ошибок. Внешние зависимости в тестах заменены моками, поэтому для их запуска не требуется работающий Docker.

## Документация OpenAPI

Экспортированная спецификация API находится в файле [`docs.json`](docs.json). Актуальная спецификация запущенного приложения также доступна по адресу `/openapi.json`.

## Остановка

```bash
docker compose down
```

Данные PostgreSQL и Elasticsearch сохраняются в именованных Docker volumes. Команда `docker compose down -v` дополнительно **удаляет эти тома вместе с данными** — используйте её только при необходимости полного сброса окружения.

## Ограничения

- Для казахского и кыргызского текста доступен базовый поиск без полноценного морфологического анализа.
- Удаление из PostgreSQL и Elasticsearch не является единой атомарной транзакцией: используется попытка компенсации при сбое сохранения в БД.
- Автоматические тесты используют моки внешних зависимостей и не являются интеграционными тестами с реальными PostgreSQL и Elasticsearch.
