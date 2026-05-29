from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Order, OrderItem, Product, Category, OperationLog

admin_bp = Blueprint("admin", __name__)


def _require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != "admin":
        return None, jsonify({"error": "需要管理员权限"}), 403
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

@admin_bp.route("/api/admin/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user, err, code = _require_admin()
    if err:
        return err, code

    from sqlalchemy import func

    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0

    # Orders by status
    status_counts = {}
    for status in ["pending", "paid", "shipped", "completed"]:
        status_counts[status] = Order.query.filter_by(status=status).count()

    return jsonify({
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "orders_by_status": status_counts,
    }), 200


# ── Staff Management ──

@admin_bp.route("/api/admin/staff", methods=["GET"])
@jwt_required()
def list_staff():
    user, err, code = _require_admin()
    if err:
        return err, code

    staff = User.query.filter(User.role.in_(["sales", "admin"])).all()
    return jsonify({"staff": [s.to_dict() for s in staff]}), 200


@admin_bp.route("/api/admin/staff", methods=["POST"])
@jwt_required()
def create_staff():
    user, err, code = _require_admin()
    if err:
        return err, code

    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "sales")

    if not username or not email or not password:
        return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400
    if role not in ("sales", "admin"):
        return jsonify({"error": "角色无效"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "用户名已存在"}), 400

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    _log_operation(user.id, "添加员工", f"添加员工: {username} ({role})")
    db.session.commit()
    return jsonify({"message": "员工已创建", "user": new_user.to_dict()}), 201


@admin_bp.route("/api/admin/staff/<int:staff_id>", methods=["PUT"])
@jwt_required()
def update_staff(staff_id):
    user, err, code = _require_admin()
    if err:
        return err, code

    staff = User.query.get(staff_id)
    if not staff:
        return jsonify({"error": "员工不存在"}), 404

    data = request.get_json()
    if "username" in data:
        staff.username = data["username"]
    if "email" in data:
        staff.email = data["email"]

    _log_operation(user.id, "修改员工信息", f"修改员工: {staff.username}")
    db.session.commit()
    return jsonify({"message": "员工信息已更新", "user": staff.to_dict()}), 200


@admin_bp.route("/api/admin/staff/<int:staff_id>/reset-password", methods=["POST"])
@jwt_required()
def reset_password(staff_id):
    user, err, code = _require_admin()
    if err:
        return err, code

    staff = User.query.get(staff_id)
    if not staff:
        return jsonify({"error": "员工不存在"}), 404

    data = request.get_json()
    new_password = data.get("new_password", "123456")
    staff.set_password(new_password)
    _log_operation(user.id, "重置密码", f"重置员工密码: {staff.username}")
    db.session.commit()
    return jsonify({"message": f"已重置 {staff.username} 的密码"}), 200


@admin_bp.route("/api/admin/staff/<int:staff_id>", methods=["DELETE"])
@jwt_required()
def delete_staff(staff_id):
    user, err, code = _require_admin()
    if err:
        return err, code

    staff = User.query.get(staff_id)
    if not staff:
        return jsonify({"error": "员工不存在"}), 404
    if staff.role == "admin":
        return jsonify({"error": "不能删除管理员账户"}), 400

    _log_operation(user.id, "删除员工", f"删除员工: {staff.username}")
    db.session.delete(staff)
    db.session.commit()
    return jsonify({"message": f"已删除员工 {staff.username}"}), 200


# ── Reports ──

@admin_bp.route("/api/admin/reports", methods=["GET"])
@jwt_required()
def reports():
    user, err, code = _require_admin()
    if err:
        return err, code

    from sqlalchemy import func

    # Sales by category
    category_sales = (
        db.session.query(
            Category.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue"),
        )
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Category.name)
        .all()
    )

    # Sales by sales person
    sales_performance = (
        db.session.query(
            User.username,
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("total_sales"),
        )
        .filter(User.role == "sales")
        .join(Product, Product.sales_id == User.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .group_by(User.username)
        .all()
    )

    # Product leaderboard
    leaderboard = (
        db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label("sold_count"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(10)
        .all()
    )

    return jsonify({
        "category_sales": [
            {"name": c[0], "total_qty": c[1] or 0, "total_revenue": round(c[2] or 0, 2)}
            for c in category_sales
        ],
        "sales_performance": [
            {"username": s[0], "order_count": s[1] or 0, "total_sales": round(s[2] or 0, 2)}
            for s in sales_performance
        ],
        "leaderboard": [
            {"name": l[0], "sold_count": l[1] or 0, "revenue": round(l[2] or 0, 2)}
            for l in leaderboard
        ],
    }), 200


# ── Monitor (Anomaly Detection) ──

@admin_bp.route("/api/admin/monitor", methods=["GET"])
@jwt_required()
def monitor():
    user, err, code = _require_admin()
    if err:
        return err, code

    from sqlalchemy import func
    import statistics

    # Get all order amounts
    order_amounts = db.session.query(Order.total_amount).all()
    amounts = [o[0] for o in order_amounts]

    anomalies = []
    if len(amounts) >= 5:
        mean = statistics.mean(amounts)
        std = statistics.stdev(amounts)
        threshold = mean + 2 * std

        # Find anomalous orders
        anomalous_orders = Order.query.filter(Order.total_amount > threshold).order_by(
            Order.total_amount.desc()
        ).all()
        anomalies = [
            {**o.to_dict(), "z_score": round((o.total_amount - mean) / std, 2)}
            for o in anomalous_orders
        ]

    # Also find low-stock products
    low_stock = Product.query.filter(Product.stock < 5).all()

    # Top selling product category (trend)
    top_category = (
        db.session.query(Category.name, func.sum(OrderItem.quantity).label("qty"))
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Category.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .first()
    )

    return jsonify({
        "anomalies": anomalies,
        "stats": {
            "mean_amount": round(mean, 2) if len(amounts) >= 5 else 0,
            "std_amount": round(std, 2) if len(amounts) >= 5 else 0,
            "threshold": round(threshold, 2) if len(amounts) >= 5 else 0,
        },
        "low_stock": [p.to_dict() for p in low_stock],
        "top_category": {"name": top_category[0], "quantity": top_category[1]} if top_category else None,
    }), 200
