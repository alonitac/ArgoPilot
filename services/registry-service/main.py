from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="AgroPilot registry-service", version="0.1.0")

SQUARE_METERS_PER_DUNAM = 1000

# plot id -> {"id": int, "area_m2": float}
PLOTS: dict[int, dict] = {}


class NotFoundError(Exception):
    pass


def problem(status: int, code: str, title: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"type": "about:blank", "title": title, "status": status, "code": code, **extra},
        media_type="application/problem+json",
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return problem(404, "NOT_FOUND", "Not Found")


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return problem(422, "VALIDATION", "Validation Error")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/plots/{plot_id}/area-dunam")
def get_plot_area_dunam(plot_id: int) -> dict[str, float]:
    plot = PLOTS.get(plot_id)
    if plot is None:
        raise NotFoundError
    return {"dunam": round(plot["area_m2"] / SQUARE_METERS_PER_DUNAM, 2)}
