# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-tenant SaaS platform for automating WhatsApp Business reservations via an AI-powered bot. Businesses (restaurants, clinics, salons) connect their WhatsApp and a Claude-powered bot handles bookings conversationally.

## Repository Structure

```
hermesmessages/
├── backend/     # FastAPI API — Python 3.12+
├── frontend/    # (in progress)
└── database/    # docker-compose.yml (PostgreSQL + Redis)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy (async) + Alembic |
| Cache | Redis |
| Validation | Pydantic v2 |
| Auth | JWT |
| AI | Claude API (`claude-sonnet-4-20250514`) |
| Testing | Pytest |

## Common Commands

All backend commands run from `backend/`:

```bash
# Start local services
cd database && docker-compose up -d

# Install dependencies
cd backend && pip install -r requirements.txt

# Run development server
cd backend && uvicorn app.main:app --reload

# Run migrations
cd backend && alembic upgrade head

# Generate new migration
cd backend && alembic revision --autogenerate -m "description"

# Run tests
cd backend && pytest

# Run a single test file
cd backend && pytest tests/test_calendar.py
```

## Backend Architecture

### Module Structure

```
backend/
├── app/
│   ├── main.py
│   ├── core/                    # Config & infrastructure
│   │   ├── config.py            # pydantic-settings
│   │   ├── database.py          # async PostgreSQL
│   │   ├── redis.py
│   │   ├── security.py          # JWT, hashing
│   │   ├── dependencies.py      # get_current_business, require_admin
│   │   └── errors.py            # global exception handler
│   ├── modules/
│   │   ├── auth/
│   │   ├── business/
│   │   ├── whatsapp/
│   │   ├── bot_engine/
│   │   ├── calendar/
│   │   ├── reservations/
│   │   ├── notifications/
│   │   ├── dashboard/
│   │   ├── billing/
│   │   └── admin/
│   └── shared/
├── alembic/
│   └── versions/0001_initial.py
└── requirements.txt
```

Each module contains: `router.py`, `service.py`, `models.py`, `schemas.py`, and optionally `dependencies.py`.

### Module Data Flow

```
WhatsApp webhook → Bot Engine → Calendar → Reservations → Notifications
                       ↑
                 Business Config
```

## Critical Business Logic

### Multi-tenancy Rule
`business_id` is **always** extracted from the JWT token — never from the request body or path params. All queries must filter by `business_id` from the token. Exception: the WhatsApp webhook resolves `business_id` via `whatsapp_phone_number_id` (no JWT on webhook calls).

### Availability Calculation (`calendar/service.py`)
1. Fetch `BusinessConfig` for the business
2. Check if date is in `open_days` and not in `blocked_dates`
3. Generate all time slots using `open_time`, `close_time`, `slot_duration`
4. Query confirmed+pending reservations for that day
5. Filter slots where existing count < `max_per_slot`
6. Cache result in Redis with 5-minute TTL
7. Invalidate cache when a reservation is created, updated, cancelled, or deleted

### WhatsApp Webhook (`whatsapp/router.py`)
- `GET /whatsapp/webhook` — Meta verification (return `hub.challenge`)
- `POST /whatsapp/webhook` — Validate `X-Hub-Signature-256`, dispatch to bot engine via `BackgroundTasks`, respond 200 immediately

### Bot Engine (`bot_engine/service.py`)
1. Load/create `ConversationContext` from Redis (TTL: 30 min, key: `conv:{business_id}:{phone}`)
2. Build system prompt with: assistant name/tone, available slots, collected data, language instruction
3. Call Claude API — response must be JSON with `action: collect_more | create_reservation | cancel`
4. If `create_reservation` → call `reservations/service.py::create_reservation`, clear context
5. If `cancel` → clear context
6. Send reply via WhatsApp Graph API
7. Save updated context to Redis

## Key Models

- **Business** — tenant record with Meta/WhatsApp credentials, plan (`free|basic|pro`), status (`trial|active|suspended`)
- **BusinessConfig** — `open_days` (list of 0-6 ints), `open_time/close_time`, `slot_duration` (minutes), `max_per_slot`, `blocked_dates` (PostgreSQL ARRAY columns)
- **Reservation** — `status: pending|confirmed|cancelled|no_show`, `source: whatsapp|manual`, `time_end` computed from `slot_duration`
- **User** — `role: owner|admin`, `meta_user_id` for Facebook OAuth

## Environment Variables

Defined in `backend/.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hermesmessages
REDIS_URL=redis://localhost:6379
SECRET_KEY=
META_APP_ID=
META_APP_SECRET=
META_WEBHOOK_VERIFY_TOKEN=
ANTHROPIC_API_KEY=
ENVIRONMENT=development|production
```

## Access Control

- All endpoints require JWT except `GET/POST /whatsapp/webhook` and `/auth/*`
- `/admin/*` routes require `role: admin` (enforced via `require_admin` dependency)
