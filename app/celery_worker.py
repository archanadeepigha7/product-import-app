from celery import Celery
import pandas as pd
import io
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app import models
from app.state import progress
from app.webhooks import trigger_webhooks

# ✅ IMPORTANT NAME CHANGE
app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@app.task
def process_csv_task(contents: bytes):
    db = SessionLocal()
    total = 0
    seen_skus = set()

    progress["status"] = "parsing"
    progress["processed"] = 0

    df = pd.read_csv(io.BytesIO(contents), chunksize=1000)

    for chunk in df:
        progress["status"] = "validating"

        chunk = chunk.drop_duplicates(subset=["sku"])
        records = []

        for _, row in chunk.iterrows():
            sku = str(row.get("sku", "")).strip().lower()
            if not sku or sku in seen_skus:
                continue

            seen_skus.add(sku)

            records.append({
                "sku": sku,
                "name": str(row.get("name", "")).strip(),
                "description": str(row.get("description", "")).strip(),
                "price": 0,
                "status": True
            })

        if records:
            progress["status"] = "importing"

            stmt = insert(models.Product).values(records)

            stmt = stmt.on_conflict_do_update(
                index_elements=["sku"],
                set_={
                    "name": stmt.excluded.name,
                    "description": stmt.excluded.description,
                    "price": stmt.excluded.price,
                    "status": stmt.excluded.status
                }
            )

            db.execute(stmt)
            db.commit()

            total += len(records)
            progress["processed"] = total

    progress["status"] = "completed"
    progress["processed"] = total

    trigger_webhooks(
        "import_completed",
        {"status": "completed", "total_records": total}
    )

    db.close()