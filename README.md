# Product Catalog API

A small online-store backend built with FastAPI, MySQL and Redis, plus a Streamlit storefront and an OpenAI-powered shopping assistant.

Users can sign up, browse and filter products, save favorites, build a cart, check out, and ask a chat assistant questions about the catalog.

## Features

- **Products**: list with filters (name, price, stock) and fetch by ID. The full catalog is cached in Redis for 60 seconds and the cache is cleared after every checkout.
- **Accounts**: registration, login, logout, account deletion. Passwords are hashed with Argon2.
- **Sessions**: opaque bearer tokens stored in Redis with a 1-hour TTL, so logout and account deletion take effect immediately.
- **Favorites**: add, remove and list per user.
- **Orders**: each user has at most one pending (`TEMP`) order, enforced by a unique constraint in MySQL. Checking out closes it with a shipping address and records product name and unit price at purchase time.
- **Chat assistant**: answers questions about products, prices and stock using the live catalog as context. Chat sessions live in Redis, are capped at 5 prompts each, and allow only one in-flight message per session.
- **Streamlit frontend**: Main, Orders, Favorites and Chat assistant pages.

## Stack

FastAPI, MySQL 8.4, Redis 7, Streamlit, OpenAI Responses API, Docker Compose (for MySQL and Redis only).

## Project layout

```
main.py            FastAPI app and /health
routers/           HTTP endpoints (products, users, favorites, orders, chat)
services/          business logic
repositories/      MySQL and Redis access (Lua scripts for chat limits)
schemas/           Pydantic request/response models
security/          password hashing and auth dependency
integrations/      OpenAI shopping assistant
exceptions/        domain errors mapped to HTTP status codes
sql/               schema and seed data, loaded by MySQL on first start
frontend/app.py    Streamlit UI
compose.yaml       MySQL + Redis
```

## Getting started

You need Python 3.10+, Docker, and an OpenAI API key (only the chat assistant uses it).

**1. Install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Set `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` and `OPENAI_API_KEY` in `.env`. The other defaults work with the Compose setup.

| Variable | Purpose |
| --- | --- |
| `API_BASE_URL` | where the Streamlit app finds the API (default `http://127.0.0.1:8000`) |
| `MYSQL_HOST`, `MYSQL_PORT` | MySQL connection (Compose exposes it on `127.0.0.1:3307`) |
| `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` | database name and credentials, also used by Compose |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` | Redis connection |
| `OPENAI_API_KEY` | key for the chat assistant |
| `OPENAI_MODEL` | model name passed to the Responses API |

**3. Start MySQL and Redis**

```bash
docker compose up -d
```

On the first start MySQL runs everything in `sql/`: it creates the tables and seeds 10 sample products. These scripts only run when the data volume is empty. To reset the database:

```bash
docker compose down -v && docker compose up -d
```

**4. Run the API**

```bash
uvicorn main:app --reload
```

The API is at http://127.0.0.1:8000 and the interactive docs at http://127.0.0.1:8000/docs.

**5. Run the frontend** (in a second terminal)

```bash
streamlit run frontend/app.py
```

## API overview

Everything except product reads, registration and login needs an `Authorization: Bearer <token>` header. Get a token from `POST /users/login`.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | health check |
| GET | `/products/` | list products, with filters |
| GET | `/products/{product_id}` | one product |
| POST | `/users/` | register |
| POST | `/users/login` | log in, returns a bearer token |
| POST | `/users/logout` | invalidate the current token |
| GET | `/users/me` | current user |
| DELETE | `/users/me` | delete account, sessions and chats |
| GET | `/favorites/` | list favorites |
| POST / DELETE | `/favorites/{product_id}` | add / remove a favorite |
| POST | `/orders/temp/items` | add an item to the pending order |
| GET | `/orders/temp` | view the pending order |
| DELETE | `/orders/temp/{product_id}` | remove one item from the pending order |
| DELETE | `/orders/temp` | discard the pending order |
| POST | `/orders/{order_id}/checkout` | close the order with a shipping address |
| GET | `/orders/` | order history |
| GET | `/orders/{order_id}` | order details |
| POST | `/chat/sessions` | start a chat session |
| GET | `/chat/sessions/{session_id}` | session info |
| GET | `/chat/sessions/{session_id}/messages` | message history |
| POST | `/chat/sessions/{session_id}/messages` | send a message, get the assistant's reply |

### Product filters

`GET /products/` accepts:

- `name`: partial match; repeat it to match any of several, e.g. `?name=Backpack&name=Basketball`
- `price` with `price_operator`
- `stock` with `stock_operator`

Operators are `lt`, `gt` and `eq`. A value and its operator must be sent together, otherwise the API returns 422.

```bash
curl "http://127.0.0.1:8000/products/?price=30&price_operator=lt&stock=0&stock_operator=gt"
```

### Example flow

```bash
# register
curl -X POST http://127.0.0.1:8000/users/ -H "Content-Type: application/json" -d '{
  "username": "dana", "password": "correct-horse-battery",
  "first_name": "Dana", "last_name": "Levi", "email": "dana@example.com",
  "phone": "0501234567", "country": "Israel", "city": "Haifa"
}'

# log in and keep the token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "dana", "password": "correct-horse-battery"}' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# add two backpacks to the cart
curl -X POST http://127.0.0.1:8000/orders/temp/items \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"product_id": 10, "quantity": 2}'

# check out
curl -X POST http://127.0.0.1:8000/orders/1/checkout \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"shipping_address": "1 Herzl St, Haifa"}'
```

## Behavior worth knowing

- Passwords must be 8 to 128 characters.
- Adding an item that exceeds available stock returns 409. Checkout also returns 409 if something went out of stock in the meantime.
- Chat errors: 404 unknown session, 409 a message is already being processed, 429 the 5-prompt limit is reached, 503 the OpenAI call failed.
- Prices are in USD.

## Notes

- `compose.yaml` runs only MySQL and Redis. The API and Streamlit app run on the host.
- The sample seed includes out-of-stock items (Sun Hat, Wireless Mouse) so you can see the stock handling.
