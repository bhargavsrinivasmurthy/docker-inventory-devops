from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app import db
from app.models import InventoryTransaction, Product
from app.services import (
    InventoryError,
    adjust_stock,
    create_product,
    receive_stock,
    sell_stock,
)

bp = Blueprint("main", __name__)


@bp.route("/health")
def health():
    return jsonify(status="ok")


@bp.route("/")
def dashboard():
    products = Product.query.filter_by(is_active=True).all()
    total_units = sum(p.quantity for p in products)
    low_stock = [p for p in products if 0 < p.quantity <= p.low_stock_threshold]
    out_of_stock = [p for p in products if p.quantity == 0]
    value = sum((p.unit_cost * p.quantity for p in products), Decimal("0"))
    recent = (
        InventoryTransaction.query.order_by(InventoryTransaction.id.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        product_count=len(products),
        total_units=total_units,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        value=value,
        recent=recent,
    )


@bp.route("/products")
def products():
    q = request.args.get("q", "").strip()
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(Product.name.ilike(like) | Product.sku.ilike(like))
    return render_template("products.html", products=query.order_by(Product.name).all(), q=q)


@bp.route("/products/new", methods=["GET", "POST"])
def product_new():
    if request.method == "POST":
        try:
            create_product(
                request.form.get("sku"),
                request.form.get("name"),
                request.form.get("category"),
                request.form.get("unit_cost") or 0,
                request.form.get("selling_price") or 0,
                request.form.get("quantity") or 0,
                request.form.get("low_stock_threshold") or 5,
            )
            flash("Product created", "success")
            return redirect(url_for("main.products"))
        except InventoryError as error:
            db.session.rollback()
            flash(str(error), "danger")
    return render_template("product_form.html")


@bp.route("/products/<int:product_id>/stock", methods=["GET", "POST"])
def stock(product_id):
    product = db.get_or_404(Product, product_id)
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "receipt":
                receive_stock(product_id, request.form.get("quantity"))
            elif action == "sale":
                sell_stock(product_id, request.form.get("quantity"))
            elif action == "adjustment":
                adjust_stock(
                    product_id,
                    request.form.get("quantity"),
                    request.form.get("reason"),
                )
            else:
                raise InventoryError("Choose a valid action")
            flash("Stock updated", "success")
            return redirect(url_for("main.stock", product_id=product_id))
        except InventoryError as error:
            db.session.rollback()
            flash(str(error), "danger")
    return render_template("stock.html", product=product)


@bp.route("/products/<int:product_id>/deactivate", methods=["POST"])
def deactivate(product_id):
    product = db.get_or_404(Product, product_id)
    product.is_active = False
    db.session.commit()
    flash("Product deactivated", "success")
    return redirect(url_for("main.products"))


@bp.route("/transactions")
def transactions():
    items = InventoryTransaction.query.order_by(InventoryTransaction.id.desc()).all()
    return render_template("transactions.html", transactions=items)