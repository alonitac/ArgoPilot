I added `POST /product` to `main.py` and tests for it in `tests/test_product_count.py`, but I have not run them. Running commands needs approval in this session and every attempt was blocked, so the tests are unverified. I checked the code by reading it.

**Behaviour**
- Request body is JSON `{"name": str, "price": float}`. Missing fields or a non-numeric price return 422.
- On success it returns 201 with `{"id", "name", "price"}`. The id is `len(PRODUCTS) + 1`, which is safe only because nothing deletes products.
- If a product with the same name already exists, it returns 409 and stores nothing.

**Choices I made that you may want to change**
- Duplicate matching is exact and case-sensitive, so "Tomato Seeds" and "tomato seeds" are different products.
- Price is not range-checked, so negative or zero prices are accepted.
- Name is not trimmed or required to be non-empty.

**Tests added**
- Creates a product and returns 201 with the right body.
- Stores the product, and `/product/count` reflects it.
- Rejects a duplicate name with 409 and leaves the original unchanged.
- Allows distinct names.
- Rejects a missing field and a non-numeric price with 422.

To run them: `uv run pytest` from the repo root.