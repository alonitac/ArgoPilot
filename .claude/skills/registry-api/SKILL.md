---
name: registry-api
description: Conventions for building and testing endpoints in the AgroPilot registry-service (FastAPI). Use this whenever you add, change, or test a route, a request or response model, an error response, or a PATCH/list endpoint in services/registry-service, even if the user only says "add an endpoint", "add a route for products", or "make the error body match". Also use it when writing tests for registry-service.
---

# Registry API conventions

These rules apply to every endpoint in `services/registry-service`. They are the project's decisions, so follow them even where the existing code doesn't yet.

## Routes and responses

- Put every new route under `/v1`. The existing `/health` and `/product/count` predate this rule and are not under `/v1`. Don't move them without asking the user.
- Lists return a JSON array. An empty collection is `200` with `[]`, never `404`.
- Return only the fields the spec lists. Don't add fields on your own.
- A PATCH changes only the fields present in the request body. Missing fields stay as they are.

## Errors

Every error response is `application/problem+json` (RFC 9457) with a stable `code`. Never return FastAPI's default `{"detail": ...}` body.

| Situation | HTTP status | `code` | Extra |
|---|---|---|---|
| Invalid input | 422 | `VALIDATION` | |
| Missing resource | 404 | `NOT_FOUND` | |
| Conflicting state | 409 | `CONFLICT` | |
| Temporarily unavailable | 503 | `UNAVAILABLE` | `Retry-After` header |

Current state: the service has no error handlers yet. When you first need one, register the handlers once on `app` in `main.py`, so that every route gets the same body. Don't build the error body inside each route.

## Tests

- Every endpoint needs tests for its success case and for every failure case it can return. Map each row of the table above to a test if the endpoint can produce it.
- Put tests in `tests/test_<topic>.py` and use `fastapi.testclient.TestClient(main.app)`.
- Reset module state with an `autouse` fixture, as `tests/test_product_count.py` does. For example, clear `main.PRODUCTS` before and after each test.
- Run `uv run pytest` from `services/registry-service` and confirm it passes before you say the work is done.

## When the spec is silent

If the spec doesn't say what should happen in some case, ask the user. Don't invent behavior, such as a default value, a status code, or a field name.
