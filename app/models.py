from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float, default=0)
    status = Column(Boolean, default=True)
    
class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    event = Column(String, default="import_completed")  # keep simple
    is_active = Column(Boolean, default=True)