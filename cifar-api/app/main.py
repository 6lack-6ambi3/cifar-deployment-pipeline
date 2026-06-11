import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.model import CIFAR10Model, predict, load_model

MODEL_PATH = Path(__file__).parent.parent / "model" / "best_cifar10_model.pth"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_FILE_SIZE_MB = 5

model: CIFAR10Model | None = None
startup_time: float = 0.0

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, startup_time
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model checkpoint not found at {MODEL_PATH}")
    model = load_model(str(MODEL_PATH))
    startup_time = time.time()
    yield

    del model

app = FastAPI(
    title="CIFAR-10 Image Classification API",
    description="A simple API for classifying images using a pre-trained CIFAR-10 model.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def read_root():
    """Root endpoint - doubles as a deploy smoke test."""
    return {
        "service": "CIFAR-10 Image Classification API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health_check():
    """Health check endpoint to verify that the API is running."""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "uptime_seconds": round(time.time() - startup_time,1)
    }

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """Endpoint to predict the class of an uploaded image.
       Accepts JPEG, PNG, WEBP, and BMP formats up to 5MB in size. Returns the top 3 predicted classes with probabilities.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum limit.")

    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    try:
        predictions = predict(model, contents, top_k=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred while making prediction: {str(e)}")
    
    return JSONResponse(content={"filename": file.filename, "predictions": predictions})