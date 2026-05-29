from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Product, Category, CartItem, Order, OrderItem, BrowseLog

customer_bp = Blueprint("customer", __name__)


# ── Products ──

@customer_bp.route("/api/products", methods=["GET"])
def list_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id", type=int)
    sort = request.args.get("sort", "newest")  # newest / price_asc / price_desc

    q = Product.query
    if search:
        q = q.filter(Product.name.contains(search) | Product.description.contains(search))
    if category_id:
        q = q.filter_by(category_id=category_id)

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "products": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
    }), 200


@customer_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "商品不存在"}), 404

    # Get "also bought" recommendations
    also_bought = _get_also_bought(product_id)

    return jsonify({"product": product.to_dict(), "also_bought": also_bought}), 200


@customer_bp.route("/api/categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify({"categories": [c.to_dict() for c in categories]}), 200


# ── Browse Log ──

@customer_bp.route("/api/browse-log", methods=["POST"])
@jwt_required(optional=True)
def record_browse():
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效请求"}), 400

    user_id = None
    if get_jwt_identity():
        user_id = int(get_jwt_identity())

    log = BrowseLog(
        user_id=user_id,
        product_id=data.get("product_id"),
        category_id=data.get("category_id"),
        duration_seconds=data.get("duration_seconds", 0),
        timestamp=datetime.now(timezone.utc),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "ok"}), 200


# ── Cart ──

@customer_bp.route("/api/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify({"cart": [item.to_dict() for item in items]}), 200


@customer_bp.route("/api/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "商品不存在"}), 404
    if product.stock < quantity:
        return jsonify({"error": "库存不足"}), 400

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({"message": "已添加到购物车"}), 200


@customer_bp.route("/api/cart/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "购物车项目不存在"}), 404

    data = request.get_json()
    quantity = data.get("quantity", 1)
    if quantity <= 0:
        db.session.delete(item)
    else:
        if item.product.stock < quantity:
            return jsonify({"error": "库存不足"}), 400
        item.quantity = quantity

    db.session.commit()
    return jsonify({"message": "购物车已更新"}), 200


@customer_bp.route("/api/cart/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "购物车项目不存在"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "已从购物车移除"}), 200


# ── Checkout / Orders ──

@customer_bp.route("/api/checkout", methods=["POST"])
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "购物车为空"}), 400

    total = 0
    order_items = []
    for ci in cart_items:
        product = Product.query.get(ci.product_id)
        if product.stock < ci.quantity:
            return jsonify({"error": f"商品 [{product.name}] 库存不足"}), 400
        product.stock -= ci.quantity
        total += product.price * ci.quantity
        order_items.append({
            "product_id": product.id,
            "quantity": ci.quantity,
            "unit_price": product.price,
        })
        db.session.delete(ci)

    order = Order(user_id=user_id, total_amount=round(total, 2), status="paid")
    db.session.add(order)
    db.session.flush()  # get order.id

    for oi in order_items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=oi["product_id"],
            quantity=oi["quantity"],
            unit_price=oi["unit_price"],
        ))

    db.session.commit()
    return jsonify({"message": "下单成功", "order": order.to_dict()}), 201


@customer_bp.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify({"orders": [o.to_dict() for o in orders]}), 200


@customer_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    # Get user stats
    order_count = Order.query.filter_by(user_id=user_id).count()
    browse_count = BrowseLog.query.filter_by(user_id=user_id).count()
    return jsonify({
        "user": user.to_dict(),
        "stats": {
            "order_count": order_count,
            "browse_count": browse_count,
        },
    }), 200


# ── Helper ──

def _get_also_bought(product_id, limit=6):
    """Simple: find other products bought by users who also bought this product."""
    # Get users who bought this product
    related_orders = db.session.query(OrderItem.order_id).filter_by(product_id=product_id).subquery()
    related_product_ids = (
        db.session.query(OrderItem.product_id, db.func.count(OrderItem.id).label("cnt"))
        .filter(OrderItem.order_id.in_(related_orders))
        .filter(OrderItem.product_id != product_id)
        .group_by(OrderItem.product_id)
        .order_by(db.func.count(OrderItem.id).desc())
        .limit(limit)
        .all()
    )
    if not related_product_ids:
        # Fallback: random products from same category
        product = Product.query.get(product_id)
        if product:
            related = Product.query.filter(
                Product.category_id == product.category_id,
                Product.id != product_id,
            ).limit(limit).all()
            return [p.to_dict() for p in related]
        return []

    ids = [r[0] for r in related_product_ids]
    products = Product.query.filter(Product.id.in_(ids)).all()
    product_map = {p.id: p for p in products}
    return [product_map[pid].to_dict() for pid in ids if pid in product_map]
