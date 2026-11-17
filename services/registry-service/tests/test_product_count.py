import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clean_products():
    main.PRODUCTS.clear()
    yield
    main.PRODUCTS.clear()


def test_product_count_is_zero_when_no_products():
    response = client.get("/product/count")

    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_product_count_reflects_number_of_products():
    main.PRODUCTS.extend([{"id": 1}, {"id": 2}, {"id": 3}])

    response = client.get("/product/count")

    assert response.status_code == 200
    assert response.json() == {"count": 3}
