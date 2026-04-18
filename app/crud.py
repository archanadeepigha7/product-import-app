from sqlalchemy.orm import Session
from . import models, schemas

# ✅ CREATE or UPDATE product
def create_product(db: Session, product: schemas.ProductCreate):
    # This block MUST be indented
    existing_product = db.query(models.Product).filter(
        models.Product.sku == product.sku
    ).first()

    # 🔁 UPDATE if exists
    if existing_product:
        existing_product.name = product.name
        existing_product.description = product.description
        existing_product.price = product.price
        existing_product.status = product.status

        db.commit()
        db.refresh(existing_product)
        return existing_product

    # ➕ CREATE new
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# ✅ GET all products
def get_products(db: Session):
    return db.query(models.Product).all()


# ✅ GET product by ID
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()


# ✅ DELETE product
def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()

    if product:
        db.delete(product)
        db.commit()
        return product
    return None


# ✅ DELETE ALL products
def delete_all_products(db: Session):
    db.query(models.Product).delete()
    db.commit()
    return {"message": "All products deleted"}