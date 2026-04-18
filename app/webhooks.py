from app.database import SessionLocal
from app import models
import requests

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