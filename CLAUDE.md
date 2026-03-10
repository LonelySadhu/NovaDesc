# NovaDesc — Project Context for Claude

## Overview
Maintenance and repair management system for high-tech enterprises (data centers, industrial facilities, vessels).
Main feature: AI assistant for technicians to query equipment info and repair guidance.

## Stack
- **Backend**: FastAPI, Python 3.12, Pydantic v2, pydantic-settings
- **Frontend**: React 18 + Vite, TypeScript, TailwindCSS, TanStack Query, Zustand
- **Database**: PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic
- **Cache/Queue**: Redis + Celery
- **AI**: Ollama (local/air-gapped) or Anthropic Claude (cloud) — switchable via `AI_PROVIDER` env
- **Deploy**: Docker Compose + installer scripts (bash for Linux/macOS, PowerShell for Windows)
- **Mobile**: PWA (same React app, manifest.json included)

## Architecture
**Backend**: Clean Architecture + Pragmatic DDD

```
domain/        → pure business logic, no frameworks
application/   → use cases, commands, handlers
infrastructure/→ DB repositories, AI adapters, external integrations
api/v1/        → FastAPI routers + Pydantic schemas
core/          → config (pydantic-settings), DI
```

**Bounded Contexts**: `equipment`, `work_orders`, `maintenance`, `users`, `ai_assistant`

**AI pattern**: Port & Adapter — `AIProviderPort` (ABC) in domain, `OllamaAdapter` + `AnthropicAdapter` in infrastructure. Switch provider via `AI_PROVIDER=ollama|anthropic` in `.env`.

**Frontend**: Feature-Sliced Design (FSD)

```
app/      → providers, router, global styles
pages/    → dashboard, equipment, work-orders, maintenance, ai-assistant, settings
widgets/  → composite UI blocks
features/ → business features (create-work-order, ask-ai, ...)
entities/ → domain types + API clients (equipment, work-order, user)
shared/   → axios client, ui-kit, types, hooks
```

Path aliases: `@app`, `@pages`, `@widgets`, `@features`, `@entities`, `@shared`

## User Roles
`admin` | `manager` | `engineer` | `dispatcher` | `technician`

## Domain Entities
- **Equipment**: serial number, manufacturer, model, location, status, maintenance interval
- **WorkOrder**: title, description, type (preventive/corrective/inspection/emergency), priority, status, logs, hours
- **MaintenanceSchedule**: interval-based schedule, overdue detection
- **User**: role-based, department
- **AIQuery**: question + equipment/workorder context + answer + model used

## Key Files
- `backend/core/config.py` — all settings via pydantic-settings
- `backend/core/dependencies.py` — DI factory for AI provider
- `backend/domain/ai_assistant/ports.py` — AIProviderPort interface
- `backend/infrastructure/ai/ollama_adapter.py` — local LLM adapter
- `backend/infrastructure/ai/anthropic_adapter.py` — cloud AI adapter
- `frontend/src/shared/api/client.ts` — axios client with JWT interceptor
- `docker-compose.yml` — production services
- `docker-compose.dev.yml` — dev override (hot reload, exposed ports)
- `installer/install.sh` — Linux/macOS installer
- `installer/install.ps1` — Windows installer

## Development Commands
```bash
make dev          # start with hot reload
make dev-down     # stop dev containers
make migrate      # run alembic migrations
make ollama-pull  # pull llama3 model into Ollama
```

## Git
- **Active branch**: `claude/review-readme-planning-wNzD4`
- Never push to `main` directly

## Next Steps (in priority order)
1. SQLAlchemy ORM models + Alembic migration setup
2. JWT authentication + role-based access control (RBAC)
3. CRUD API endpoints for `equipment` and `work_orders`
4. Figma designs → React page/widget components
5. AI chat endpoint with streaming (SSE) + equipment context injection
6. Alembic seed script for initial admin user
7. External API integration layer (SAP, 1C adapters)
