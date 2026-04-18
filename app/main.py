from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import requests

from .database import engine, Base, SessionLocal
from . import models, schemas
from app.state import progress

# ✅ FastAPI app
app = FastAPI()

# ================================
# ✅ CORS
# ================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 🔥 TEMP allow all (for now)
    allow_credentials=True,
    allow_methods=["*"],   # IMPORTANT for DELETE
    allow_headers=["*"],
)

# ================================
# ✅ Create tables
# ================================
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# ================================
# ✅ DB Dependency
# ================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================================
# 🔥 WEBHOOK FUNCTION
# ================================
def trigger_webhooks(event: str, payload: dict):
    db = SessionLocal()

    webhooks = db.query(models.Webhook).filter(
        models.Webhook.event == event,
        models.Webhook.is_active == True
    ).all()

    for webhook in webhooks:
        try:
            requests.post(webhook.url, json=payload, timeout=5)
        except Exception as e:
            print("Webhook failed:", e)

    db.close()

# ================================
# 🔥 UPLOAD API (CELERY)
# ================================
@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()

    print("UPLOAD HIT ✅")

    # 🔥 Convert bytes → string
    csv_data = contents.decode("utf-8")

    # 🔥 Import celery task
    from app.celery_worker import process_csv_task

    # 🔥 Reset progress
    progress["status"] = "started"
    progress["processed"] = 0

    # 🔥 Send to Celery
    task = process_csv_task.delay(csv_data)

    return {
        "message": "Upload started",
        "task_id": task.id
    }

# ================================
# 🔥 PROGRESS API
# ================================
@app.get("/progress")
def get_progress():
    return progress

# ================================
# 📦 GET PRODUCTS
# ================================
@app.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

# ================================
# ❌ DELETE ALL PRODUCTS
# ================================
@app.delete("/products")
def delete_all_products(db: Session = Depends(get_db)):
    db.query(models.Product).delete()
    db.commit()

    return {"message": "All products deleted"}

# ================================
# 🏠 HOME
# ================================
@app.get("/")
def home():
    return {"message": "API Running"}