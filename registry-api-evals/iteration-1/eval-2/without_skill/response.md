I added `PATCH /product/{product_id}`, which takes only `price` in the body, so the name is never resent. The full suite passes: 6 tests, 2 existing and 4 new.

**Endpoint (`main.py`)**
- Request body: `{"price": <number>}`. The body is validated with a small Pydantic model, so a missing or non-numeric price returns 422.
- Finds the product by `id` in `PRODUCTS`, updates only `price`, and returns the full product.
- Unknown id returns 404 with `"Product not found"`.

**Tests (`tests/test_product_price.py`)**
- Updating the price keeps the name and changes only the price, both in the response and in the stored product.
- Unknown product returns 404 and leaves the stored product unchanged.
- Empty body returns 422 and leaves the price unchanged.
- Non-numeric price returns 422 and leaves the price unchanged.

I ran the new tests before writing the endpoint and three of them failed with 404 as expected. The unknown-product test already passed then, because a missing route also returns 404, so it doesn't prove the new 404 path. It's still a useful regression check.

**Choices to confirm:**
- The URL is `/product/{product_id}` to match the existing `/product/count` style. If you'd rather have `/product/{id}/price`, that's a quick change.
- I did not add a lower bound on price, so negative prices are accepted. Say if you want `price >= 0` enforced.
- Products are plain dicts with no fixed schema, so the endpoint sets `price` on whatever dict it finds, creating the key if it's missing.

The `__pycache__/` directories from my test runs are still in the repo as untracked files. I left them because deleting them needed approval; they're safe to remove. Nothing is committed.