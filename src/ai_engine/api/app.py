from fastapi import FastAPI

from ai_engine.api.routes import router

app = FastAPI(
    title="Predictive Maintenance AI Engine",
    version="0.1.0",
)

app.include_router(router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
