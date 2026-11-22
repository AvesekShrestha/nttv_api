# NTC Notification Service

Handles notifications for the NTC Ticket Management System.

## Features

- Stores notifications in a personal inbox.
- Tracks read and unread notifications.
- Sends real-time updates through WebSockets.
- Sends ticket emails through a background worker.
- Retries failed deliveries and prevents duplicate event processing.
- Sends authentication and OTP emails without storing OTP content.

## Requirements

- Python 3.12+ and uv
- PostgreSQL
- Kafka
- Running authentication and ticket services
- SMTP credentials for email delivery

## Setup

Run these commands from the notification directory:

```bash
uv sync
cp .env.example .env
```

Configure `.env`, create the Kafka topics listed there, and apply migrations:

```bash
uv run alembic upgrade head
```

## Run

Start each process in a separate terminal.

**API**

```bash
uv run uvicorn src.main:app --reload --port 8000
```

**Kafka consumer**

```bash
uv run python -m src.infrastructure.messaging.kafka.consumer
```

**Email worker**

```bash
uv run python -m src.infrastructure.workers.delivery_worker
```

Use a separate active account for the email worker. Configure its
credentials in `.env` or enter them when prompted.

API documentation: http://localhost:8000/docs  
Health check: http://localhost:8000/health

## Notification API

Base path: `/api/v1/notifications`

All endpoints require an `Authorization: Bearer <access_token>` header.
Users can access only their own notifications.

| Method | Path | Purpose |
|---|---|---|
| GET | `/`* | List notifications |
| GET | `/unread-count` | Get unread count |
| GET | `/{id}` | Get a notification |
| PATCH | `/{id}/read` | Mark one as read |
| PATCH | `/read-all` | Mark all as read |

*Use the base path without a trailing slash for listing.
Supports `page`, `limit`, and `unread_only` query parameters.

## Real-Time Updates

Connect to:

```text
ws://localhost:8000/api/v1/notifications/ws
```

Send this message within 10 seconds:

```json
{"type": "authenticate", "access_token": "<access_token>"}
```

After receiving `ready`, fetch the inbox and unread count.
Fetch them again whenever a `notifications.changed` message arrives.

Reconnect with a fresh token when needed, and close the connection on logout.

## Notes

- Keep `.env` and `.runtime/` out of Git.
- Set `CORS_ALLOWED_ORIGINS` to your frontend URL.
- Email jobs allow up to three delivery attempts.
- Worker refresh tokens expire and may require a new session.
- A crash after SMTP accepts an email can cause a duplicate delivery.
