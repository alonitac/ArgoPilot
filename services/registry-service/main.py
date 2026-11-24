from fastapi import FastAPI

app = FastAPI(title="AgroPilot registry-service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health2")
def health2() -> dict[str, str]:
    return {"status": "ok"}
