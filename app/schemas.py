from pydantic import BaseModel

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    status: bool = True

class ProductOut(ProductCreate):
    id: int


class Config:
    from_attributes = True
class WebhookCreate(BaseModel):
    url: str
    event: str = "import_completed"
    is_active: bool = True

class WebhookOut(BaseModel):
    id: int
    url: str
    event: str
    is_active: bool

    class Config:
        from_attributes  = True
