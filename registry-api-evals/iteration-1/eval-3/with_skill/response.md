I added `GET /v1/products`, which returns the full product list, plus tests. The suite passes: 4 tests, including the 2 new ones.

**What changed**
- `main.py`: new `list_products()` route at `/v1/products` that returns `PRODUCTS` as a JSON array. Empty gives `[]` with 200.
- `tests/test_products.py`: two tests, one for the empty list and one for a list with two products. They use the same autouse fixture as `test_product_count.py`.

**Choices you may want to change**
- **Path is `/v1/products`, not `/products`.** The project's registry-api conventions require new routes under `/v1`. The existing `/health` and `/product/count` predate that rule and I left them alone. If you want the bare path, say so.
- **Response is the stored dicts as-is.** The spec doesn't define product fields, so I didn't pick a schema or filter fields.
- **No error-case tests.** This endpoint has no inputs and no way to return 404, 409, 422 or 503, so there's no failure case to test. The service also has no error handlers yet, which the conventions only ask for when an endpoint first needs one.

`uv run` created a `.venv/` directory in the repo, and there's no `.gitignore`, so it will show as untracked in `git status`. I did not commit anything.