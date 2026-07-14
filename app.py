from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from forecast_service import MODEL_PATH, get_forecast

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="WhereVulniusAI Forecast API",
    description="7-day weather forecast API powered by a trained ML model",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": MODEL_PATH.exists(),
        "model_path": str(MODEL_PATH),
    }


@app.get("/api/forecast")
def forecast() -> dict:
    try:
        return get_forecast()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Forecast error: {error}") from error
