I haven't changed any files yet. The registry-api conventions require me to ask when the spec is silent on behavior, field names, or status codes, and this task leaves several of those open.

**What I found:** `main.py` has `PRODUCTS: list[dict]`, with no product model and no creation endpoint. Only `GET /product/count` and `GET /health` exist, and there are no error handlers yet. The existing test uses `{"id": 1}`-style dicts.

**Questions, with my proposed defaults:**

1. **Route:** `PATCH /v1/product/{product_id}`, per the rule that new routes go under `/v1`. OK?
2. **Product id type:** Stored products have no schema in the repo. Are ids integers or strings? I need this to type the path parameter and do the lookup.
3. **Price field:** `price` as a number, rejected with `422 VALIDATION` if negative or non-numeric. Should it be a float, a decimal, or integer cents? Is `0` allowed?
4. **Missing product:** `404 NOT_FOUND`, per the table.
5. **Empty body (`{}`):** No fields to change. I'd return `422 VALIDATION`, but a no-op `200` is also defensible. Which do you want?
6. **Response body:** The full updated product, or only the changed fields?
7. **Error handlers:** The 404 and 422 responses need `application/problem+json` handlers. Registering them on `app` in `main.py` also changes FastAPI's default 422 body for every route. Is that OK?

Once you answer, I'll implement the endpoint, add tests for success, 404, and validation failure, and run `uv run pytest` from the registry-service directory. I'm assuming `repo/` is the registry-service. The skill refers to `services/registry-service`, and this checkout has no `services/` directory.