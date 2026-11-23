from decimal import Decimal, InvalidOperation

from app import db
from app.models import InventoryTransaction, Product


class InventoryError(ValueError):
    """Raised when an inventory operation is invalid."""


def _to_decimal(value, field):
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise InventoryError(f"{field} must be a number")
    if number < 0:
        raise InventoryError(f"{field} cannot be negative")
    return number


def _to_int(value, field):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise InventoryError(f"{field} must be a whole number")
    return number


def create_product(sku, name, category, unit_cost, selling_price,
                   quantity=0, low_stock_threshold=5):
    sku = (sku or "").strip()
    name = (name or "").strip()
    if not sku:
        raise InventoryError("SKU is required")
    if not name:
        raise InventoryError("Name is required")
    if Product.query.filter_by(sku=sku).first():
        raise InventoryError("SKU already exists")

    quantity = _to_int(quantity, "Quantity")
    threshold = _to_int(low_stock_threshold, "Low stock threshold")
    if quantity < 0 or threshold < 0:
        raise InventoryError("Quantity and threshold cannot be negative")

    product = Product(
        sku=sku,
        name=name,
        category=(category or "").strip() or None,
        unit_cost=_to_decimal(unit_cost, "Unit cost"),
        selling_price=_to_decimal(selling_price, "Selling price"),
        quantity=quantity,
        low_stock_threshold=threshold,
    )
    db.session.add(product)
    db.session.flush()
    if quantity > 0:
        db.session.add(InventoryTransaction(
            product_id=product.id, type="RECEIPT",
            quantity_change=quantity, quantity_before=0,
            quantity_after=quantity, reason="Opening stock",
        ))
    db.session.commit()
    return product


def _apply_stock_change(product, change, tx_type, reason):
    before = product.quantity
    after = before + change
    if after < 0:
        raise InventoryError("Insufficient stock")
    try:
        product.quantity = after
        db.session.add(InventoryTransaction(
            product_id=product.id, type=tx_type,
            quantity_change=change, quantity_before=before,
            quantity_after=after, reason=reason,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return product


def receive_stock(product_id, quantity, reason="Stock receipt"):
    product = db.session.get(Product, product_id)
    if product is None:
        raise InventoryError("Product not found")
    quantity = _to_int(quantity, "Quantity")
    if quantity <= 0:
        raise InventoryError("Receipt quantity must be positive")
    return _apply_stock_change(product, quantity, "RECEIPT", reason)


def sell_stock(product_id, quantity, reason="Sale"):
    product = db.session.get(Product, product_id)
    if product is None:
        raise InventoryError("Product not found")
    quantity = _to_int(quantity, "Quantity")
    if quantity <= 0:
        raise InventoryError("Sale quantity must be positive")
    return _apply_stock_change(product, -quantity, "SALE", reason)


def adjust_stock(product_id, new_quantity, reason):
    product = db.session.get(Product, product_id)
    if product is None:
        raise InventoryError("Product not found")
    new_quantity = _to_int(new_quantity, "New quantity")
    if new_quantity < 0:
        raise InventoryError("Quantity cannot be negative")
    if not (reason or "").strip():
        raise InventoryError("Reason is required for adjustments")
    change = new_quantity - product.quantity
    return _apply_stock_change(product, change, "ADJUSTMENT", reason.strip())