from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Sahyog ML Service", version="1.0.0")
app.include_router(router)


@app.get("/health", summary="Liveness check")
def health() -> dict:
    return {"status": "ok"}
