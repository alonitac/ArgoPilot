import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clean_plots():
    main.PLOTS.clear()
    yield
    main.PLOTS.clear()


def test_plot_area_in_dunam():
    main.PLOTS[1] = {"id": 1, "area_m2": 2500}

    response = client.get("/v1/plots/1/area-dunam")

    assert response.status_code == 200
    assert response.json() == {"dunam": 2.5}


def test_plot_area_in_dunam_is_rounded_to_two_decimals():
    main.PLOTS[1] = {"id": 1, "area_m2": 1234.567}

    response = client.get("/v1/plots/1/area-dunam")

    assert response.status_code == 200
    assert response.json() == {"dunam": 1.23}


def test_unknown_plot_returns_not_found_problem():
    response = client.get("/v1/plots/99/area-dunam")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "NOT_FOUND"


def test_invalid_plot_id_returns_validation_problem():
    response = client.get("/v1/plots/abc/area-dunam")

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "VALIDATION"
