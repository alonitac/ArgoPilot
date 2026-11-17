I added `DELETE /product/{product_id}` to `main.py`, with three new tests. The full suite passes (5 tests).

**Behavior**
- **Product exists:** removes it from `PRODUCTS` and returns `204 No Content`.
- **Product doesn't exist:** returns `404 Not Found` with `{"detail": "Product <id> not found"}` and leaves the list unchanged. Deleting the same id twice gives 404 the second time.

**Choices I made**
- The id is an `int` path parameter, matching the integer ids in the existing tests.
- The route is `/product/{product_id}`, following the singular `/product/count` style.
- Products are plain dicts in an in-memory list, so the handler scans for a matching `id` and removes it. If you later move to a database, this handler is the part to change.

**TDD sequence**
- I wrote the three tests first. They failed with 404 because no DELETE route existed.
- Then I added the handler, and all five tests passed.

**Housekeeping**
- I didn't commit anything.
- The test runs left `__pycache__/` directories and a `.venv/` in the repo. I couldn't remove the `__pycache__` directories because the shell asked for approval. They're harmless, but you may want to delete them.
- The edit to the test file went through the file tool, because a shell command containing that test code was blocked by a quoting check.