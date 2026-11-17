I added `DELETE /v1/product/{product_id}` to `main.py` with tests. The full suite passes: 6 tests, the 4 new ones and the 2 existing ones.

**Behavior**
- **Found:** removes the product whose `id` matches and returns `204` with an empty body.
- **Not found:** `404` with `code: NOT_FOUND`, as the project's error table specifies. The list is left unchanged.
- **Non-integer id** (e.g. `/v1/product/abc`): `422` with `code: VALIDATION`. FastAPI produces this from the `int` path parameter, so I covered it too.

**Choices to confirm**
- **Route:** `/v1/product/{product_id}`, under `/v1` per the project rules and singular like the existing `/product/count`.
- **ID type:** integer, matching the `{"id": 1}` shape in the existing tests. The spec doesn't define product ids, so if they're strings or UUIDs, the path parameter type needs changing.
- **Error handling:** the service had no error handlers, so I registered two on `app` in `main.py`: one for the new `ApiError` and one for `RequestValidationError`. Both return `application/problem+json` with `type`, `title`, `status`, `detail`, and `code`.

**Gaps**
- Framework-generated errors, such as an unknown route (404) or wrong method (405), still return FastAPI's default `{"detail": ...}` body. The project rules say never to return that, but 405 has no code in the error table, so I left it alone. Say if you want a catch-all handler for these.
- I didn't commit anything. The changes are in the working tree: `main.py` modified, `tests/test_delete_product.py` new.