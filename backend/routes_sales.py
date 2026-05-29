from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Product, Category, Order, BrowseLog, OperationLog

sales_bp = Blueprint("sales", __name__)


def _require_sales():
    """Check current user is sales or admin."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ("sales", "admin"):
        return None, jsonify({"error": "无权限"}), 403
    return user, None, None


def _log_operation(user_id, op_type, content):
    from flask import request as req
    log = OperationLog(
        user_id=user_id,
        operation_type=op_type,
        content=content,
        ip_address=req.remote_addr or "",
        timestamp=datetime.now(timezone.utc),
    )
    db.session.add(log)


# ── Dashboard ──

@sales_bp.route("/api/sales/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user, err, code = _require_sales()
    if err:
        return err, code

    from sqlalchemy import func

    # Today's orders
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = Order.query.filter(Order.created_at >= today).count()
    today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= today
    ).scalar() or 0

    # Total products
    product_count = Product.query.count()
    # Total orders
    total_orders = Order.query.count()

    return jsonify({
        "today_orders": today_orders,
        "today_revenue": round(today_revenue, 2),
        "product_count": product_count,
        "total_orders": total_orders,
    }), 200


# ── Categories ──

@sales_bp.route("/api/sales/categories", methods=["GET"])
@jwt_required()
def list_categories():
    user, err, code = _require_sales()
    if err:
        return err, code
    categories = Category.query.all()
    return jsonify({"categories": [c.to_dict() for c in categories]}), 200


@sales_bp.route("/api/sales/categories", methods=["POST"])
@jwt_required()
def create_category():
    user, err, code = _require_sales()
    if err:
        return err, code
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "分类名不能为空"}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "分类已存在"}), 400

    cat = Category(name=name, description=data.get("description", ""), created_by=user.id)
    db.session.add(cat)
    _log_operation(user.id, "创建分类", f"创建分类: {name}")
    db.session.commit()
    return jsonify({"message": "分类已创建", "category": cat.to_dict()}), 201


@sales_bp.route("/api/sales/categories/<int:cat_id>", methods=["PUT"])
@jwt_required()
def update_category(cat_id):
    user, err, code = _require_sales()
    if err:
        return err, code
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({"error": "分类不存在"}), 404

    data = request.get_json()
    if "name" in data:
        cat.name = data["name"]
    if "description" in data:
        cat.description = data["description"]

    _log_operation(user.id, "修改分类", f"修改分类: {cat.name}")
    db.session.commit()
    return jsonify({"message": "分类已更新", "category": cat.to_dict()}), 200


@sales_bp.route("/api/sales/categories/<int:cat_id>", methods=["DELETE"])
@jwt_required()
def delete_category(cat_id):
    user, err, code = _require_sales()
    if err:
        return err, code
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({"error": "分类不存在"}), 404

    _log_operation(user.id, "删除分类", f"删除分类: {cat.name}")
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message": "分类已删除"}), 200


# ── Products ──

@sales_bp.route("/api/sales/products", methods=["GET"])
@jwt_required()
def list_products():
    user, err, code = _require_sales()
    if err:
        return err, code
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify({"products": [p.to_dict() for p in products]}), 200


@sales_bp.route("/api/sales/products", methods=["POST"])
@jwt_required()
def create_product():
    user, err, code = _require_sales()
    if err:
        return err, code
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "商品名不能为空"}), 400

    product = Product(
        name=name,
        description=data.get("description", ""),
        price=float(data.get("price", 0)),
        stock=int(data.get("stock", 0)),
        image_url=data.get("image_url", ""),
        category_id=data.get("category_id"),
        sales_id=user.id,
    )
    db.session.add(product)
    _log_operation(user.id, "添加商品", f"添加商品: {name}")
    db.session.commit()
    return jsonify({"message": "商品已添加", "product": product.to_dict()}), 201


@sales_bp.route("/api/sales/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    user, err, code = _require_sales()
    if err:
        return err, code
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "商品不存在"}), 404

    data = request.get_json()
    for field in ["name", "description", "price", "stock", "image_url", "category_id"]:
        if field in data:
            setattr(product, field, data[field])

    _log_operation(user.id, "修改商品", f"修改商品: {product.name}")
    db.session.commit()
    return jsonify({"message": "商品已更新", "product": product.to_dict()}), 200


@sales_bp.route("/api/sales/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    user, err, code = _require_sales()
    if err:
        return err, code
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "商品不存在"}), 404

    _log_operation(user.id, "删除商品", f"删除商品: {product.name}")
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "商品已删除"}), 200


# ── Orders ──

@sales_bp.route("/api/sales/orders", methods=["GET"])
@jwt_required()
def list_orders():
    user, err, code = _require_sales()
    if err:
        return err, code
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({"orders": [o.to_dict() for o in orders]}), 200


@sales_bp.route("/api/sales/orders/<int:order_id>", methods=["PUT"])
@jwt_required()
def update_order(order_id):
    user, err, code = _require_sales()
    if err:
        return err, code
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404

    data = request.get_json()
    if "status" in data:
        order.status = data["status"]

    _log_operation(user.id, "更新订单", f"订单 #{order.id} 状态: {order.status}")
    db.session.commit()
    return jsonify({"message": "订单已更新", "order": order.to_dict()}), 200


# ── Logs ──

@sales_bp.route("/api/sales/logs", methods=["GET"])
@jwt_required()
def view_logs():
    user, err, code = _require_sales()
    if err:
        return err, code

    log_type = request.args.get("type", "browse")  # browse / operation
    page = request.args.get("page", 1, type=int)
    per_page = 20

    if log_type == "operation":
        q = OperationLog.query.order_by(OperationLog.timestamp.desc())
    else:
        q = BrowseLog.query.order_by(BrowseLog.timestamp.desc())

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "logs": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
    }), 200
