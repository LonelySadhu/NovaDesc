# NovaDesc

Система управления техническим обслуживанием и ремонтом для дата-центров, судов и промышленных предприятий.
Ключевая функция: AI-ассистент для технического персонала с поиском по загруженным мануалам оборудования.

## Стек

- **Backend**: FastAPI, Python 3.12, SQLAlchemy 2.0 async, Alembic
- **Frontend**: React 18 + Vite, TypeScript, TailwindCSS, TanStack Query
- **БД**: PostgreSQL 16 + pgvector
- **Очередь**: Redis + Celery
- **AI**: Ollama (локально) / Anthropic Claude (облако)
- **Хранилище файлов**: MinIO (S3-совместимый)
- **Деплой**: Docker Compose

---

## Быстрый старт

### 1. Переменные окружения

`.env` уже готов для локальной разработки. В продакшене обязательно смени:

| Переменная | Описание |
|---|---|
| `SECRET_KEY` | JWT-подпись — должен быть случайным и секретным |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `MINIO_ROOT_PASSWORD` | Пароль MinIO |
| `ADMIN_USER` / `ADMIN_PASS` | Логин и пароль первого admin-пользователя |

### 2. Запуск (разработка)

```bash
make dev
```

Поднимает все сервисы с hot reload: PostgreSQL, Redis, MinIO, Celery, Ollama, backend, frontend.

### 3. Миграции и первый пользователь

```bash
make migrate   # применить миграции к БД
make seed      # создать admin-пользователя из .env (ADMIN_USER / ADMIN_PASS)
```

### 4. Загрузить AI-модели (первый запуск)

```bash
make ollama-pull   # скачивает llama3 + nomic-embed-text (~5 ГБ)
```

После этого доступно:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs

---

## Команды

```bash
make dev                        # запуск в dev-режиме с hot reload
make dev-down                   # остановить dev-контейнеры
make prod                       # запуск в production-режиме (-d)
make prod-down                  # остановить prod-контейнеры
make logs                       # хвост всех логов
make migrate                    # alembic upgrade head
make makemigration m=<name>     # сгенерировать миграцию
make seed                       # создать admin-пользователя
make ollama-pull                # pull llama3 + nomic-embed-text
```

---

## API

Документация после запуска:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Аутентификация

```bash
# Логин — получить токены
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin_dev"}'
# → { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }

# Текущий пользователь
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# Обновить access_token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

---

## Архитектура

```
backend/
├── domain/          # бизнес-логика, без фреймворков
├── application/     # use cases, сервисы
├── infrastructure/  # репозитории, AI-адаптеры, интеграции
├── api/v1/          # FastAPI роутеры + Pydantic схемы
├── core/            # config, DI (dependencies.py)
└── scripts/         # seed и утилиты

frontend/
├── app/             # провайдеры, роутер
├── pages/           # страницы
├── widgets/         # составные UI-блоки
├── features/        # бизнес-фичи
├── entities/        # доменные типы + API-клиенты
└── shared/          # axios, ui-kit, хуки
```

### Роли пользователей

| Роль | Права |
|---|---|
| `admin` | полный доступ |
| `manager` | просмотр фото, управление |
| `engineer` | завершение нарядов, работа с оборудованием |
| `dispatcher` | создание нарядов |
| `technician` | просмотр и логи |

### AI / RAG

Документы загружаются через `POST /api/v1/knowledge-base/documents`, парсятся, индексируются в pgvector.
При каждом запросе к AI топ-5 релевантных чанков инжектируются в промт.

Переключение провайдера без изменения кода:
```bash
# .env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Разработка

### Новая миграция

```bash
# 1. Изменить модели в backend/infrastructure/database/models/
# 2. Сгенерировать миграцию
make makemigration m=add_equipment_index
# 3. Применить
make migrate
```

### RBAC в новом эндпоинте

```python
from core.dependencies import require_roles
from domain.users.value_objects import UserRole

@router.post("/work-orders")
async def create(user = Depends(require_roles(UserRole.DISPATCHER, UserRole.ENGINEER, UserRole.ADMIN))):
    ...
```

### Git workflow

- Никогда не пушить напрямую в `main`
- Каждая фича — отдельная ветка: `feat/<name>`
- PR → merge в `main`