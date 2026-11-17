I added `GET /products` and tests for it, but I could not run the test suite. Every shell command that would execute Python or pytest was blocked by the approval prompt, so the tests are unverified.

**Changes**
- **`main.py`**: new `list_products()` handler on `/products`, placed after `/product/count`. It returns the in-memory `PRODUCTS` list, so an empty registry gives `[]`.
- **`tests/test_list_products.py`** (new): two tests, following the same fixture pattern as `test_product_count.py`:
  - returns `[]` when there are no products
  - returns every product that has been added, in order

The endpoint has no response model, so it returns whatever dicts are stored, the same way `PRODUCTS` is typed in the existing code.

**To verify**, run this from the repo root:
```
uv run --frozen pytest -q
```
If you approve the command, I can run it and report the output.