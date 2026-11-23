import pytest

from app import db
from app.models import InventoryTransaction, Product
from app.services import (
    InventoryError,
    adjust_stock,
    create_product,
    receive_stock,
    sell_stock,
)


def make_product(**overrides):
    data = {
        "sku": "SKU1",
        "name": "Laptop",
        "category": "Electronics",
        "unit_cost": "500.00",
        "selling_price": "650.00",
        "quantity": 10,
        "low_stock_threshold": 3,
    }
    data.update(overrides)
    return create_product(**data)


def test_create_product_with_opening_stock(app_context):
    product = make_product()
    assert product.quantity == 10
    assert InventoryTransaction.query.count() == 1


def test_duplicate_sku_rejected(app_context):
    make_product()
    with pytest.raises(InventoryError):
        make_product()


def test_receive_stock_increases_quantity(app_context):
    product = make_product()
    receive_stock(product.id, 5)
    assert db.session.get(Product, product.id).quantity == 15


def test_sale_reduces_quantity(app_context):
    product = make_product()
    sell_stock(product.id, 4)
    assert db.session.get(Product, product.id).quantity == 6


def test_overselling_rejected(app_context):
    product = make_product()
    with pytest.raises(InventoryError):
        sell_stock(product.id, 11)
    assert db.session.get(Product, product.id).quantity == 10


def test_sale_quantity_must_be_positive(app_context):
    product = make_product()
    with pytest.raises(InventoryError):
        sell_stock(product.id, 0)


def test_negative_price_rejected(app_context):
    with pytest.raises(InventoryError):
        make_product(unit_cost="-1")


def test_adjustment_requires_reason(app_context):
    product = make_product()
    with pytest.raises(InventoryError):
        adjust_stock(product.id, 7, "")


def test_adjustment_records_audit_trail(app_context):
    product = make_product()
    adjust_stock(product.id, 7, "Stock count correction")
    tx = InventoryTransaction.query.filter_by(type="ADJUSTMENT").one()
    assert tx.quantity_before == 10
    assert tx.quantity_after == 7
    assert tx.quantity_change == -3


def test_audit_trail_for_sale(app_context):
    product = make_product()
    sell_stock(product.id, 2)
    tx = InventoryTransaction.query.filter_by(type="SALE").one()
    assert tx.quantity_before == 10
    assert tx.quantity_after == 8
