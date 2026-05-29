"""
Data analysis and recommendation API routes.
"""
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Product, Category, Order, OrderItem, BrowseLog

data_bp = Blueprint("data", __name__)


# ── Sales Trend ──

@data_bp.route("/api/data/sales-trend", methods=["GET"])
@jwt_required()
def sales_trend():
    period = request.args.get("period", "day")  # day / week / month
    now = datetime.now(timezone.utc)
    from sqlalchemy import func

    if period == "week":
        start = now - timedelta(days=7)
        format_str = "%Y-%m-%d"
    elif period == "month":
        start = now - timedelta(days=30)
        format_str = "%Y-%m-%d"
    else:  # day: last 24 hours (grouped by hour)
        start = now - timedelta(hours=24)
        # Query orders in last 24h grouped by hour
        results = (
            db.session.query(
                func.strftime("%H", Order.created_at, '+8 hours').label("hour"),
                func.count(Order.id).label("count"),
                func.sum(Order.total_amount).label("revenue"),
            )
            .filter(Order.created_at >= start)
            .group_by("hour")
            .order_by("hour")
            .all()
        )
        return jsonify({
            "period": "day",
            "data": [
                {"label": f"{r[0]}:00", "count": r[1], "revenue": round(r[2] or 0, 2)}
                for r in results
            ],
        }), 200

    # For week/month, group by day
    results = (
        db.session.query(
            func.strftime("%Y-%m-%d", Order.created_at, '+8 hours').label("day"),
            func.count(Order.id).label("count"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .filter(Order.created_at >= start)
        .group_by("day")
        .order_by("day")
        .all()
    )
    return jsonify({
        "period": period,
        "data": [
            {"label": r[0], "count": r[1], "revenue": round(r[2] or 0, 2)}
            for r in results
        ],
    }), 200


# ── Leaderboard ──

@data_bp.route("/api/data/leaderboard", methods=["GET"])
@jwt_required()
def leaderboard():
    from sqlalchemy import func

    results = (
        db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label("sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(10)
        .all()
    )
    return jsonify({
        "leaderboard": [
            {"name": r[0], "sold": r[1] or 0, "revenue": round(r[2] or 0, 2)}
            for r in results
        ],
    }), 200


# ── User Profiling ──

@data_bp.route("/api/data/user-profile", methods=["GET"])
@jwt_required()
def user_profile():
    from sqlalchemy import func

    # Region distribution
    region_dist = (
        db.session.query(User.region, func.count(User.id))
        .filter(User.role == "customer")
        .group_by(User.region)
        .all()
    )

    # Preferred categories (overall)
    cat_prefs = (
        db.session.query(Category.name, func.count(BrowseLog.id).label("views"))
        .join(BrowseLog, BrowseLog.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.count(BrowseLog.id).desc())
        .limit(8)
        .all()
    )

    # Average order value
    from sqlalchemy import func as f
    avg_order = db.session.query(f.avg(Order.total_amount)).scalar() or 0

    return jsonify({
        "region_distribution": [
            {"region": r[0] or "未知", "count": r[1]} for r in region_dist
        ],
        "category_preferences": [
            {"name": c[0], "views": c[1]} for c in cat_prefs
        ],
        "avg_order_value": round(avg_order, 2),
    }), 200


# ── Recommendations ──

@data_bp.route("/api/data/recommendations/<int:product_id>", methods=["GET"])
def also_bought(product_id):
    """Also-bought recommendations for a product."""
    from routes_customer import _get_also_bought
    products = _get_also_bought(product_id)
    return jsonify({"recommendations": products}), 200


@data_bp.route("/api/data/recommendations/user", methods=["GET"])
@jwt_required()
def personalized():
    """Collaborative filtering: recommend based on similar users."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    # Find users in the same region
    if user.region:
        similar_users = User.query.filter(
            User.region == user.region,
            User.id != user_id,
            User.role == "customer",
        ).all()
    else:
        similar_users = User.query.filter(
            User.role == "customer",
            User.id != user_id,
        ).limit(20).all()

    similar_user_ids = [u.id for u in similar_users]

    # Get products bought by similar users that current user hasn't bought
    user_bought = set(
        pid[0] for pid in db.session.query(OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id == user_id)
        .all()
    )

    from sqlalchemy import func
    recommendations = (
        db.session.query(
            Product,
            func.count(OrderItem.id).label("freq"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id.in_(similar_user_ids))
        .filter(~Product.id.in_(user_bought) if user_bought else True)
        .group_by(Product.id)
        .order_by(func.count(OrderItem.id).desc())
        .limit(8)
        .all()
    )

    return jsonify({
        "recommendations": [
            {**p.to_dict(), "bought_by_similar": freq}
            for p, freq in recommendations
        ],
    }), 200


# ── Anomalies ──

@data_bp.route("/api/data/anomalies", methods=["GET"])
@jwt_required()
def anomalies():
    import statistics

    amounts = [o[0] for o in db.session.query(Order.total_amount).all()]
    if len(amounts) < 5:
        return jsonify({"anomalies": [], "stats": {"mean": 0, "std": 0, "threshold": 0}}), 200

    mean = statistics.mean(amounts)
    std = statistics.stdev(amounts)
    threshold = mean + 2 * std

    anomalous_orders = Order.query.filter(Order.total_amount > threshold).order_by(
        Order.total_amount.desc()
    ).all()

    return jsonify({
        "anomalies": [
            {**o.to_dict(), "z_score": round((o.total_amount - mean) / std, 2)}
            for o in anomalous_orders
        ],
        "stats": {"mean": round(mean, 2), "std": round(std, 2), "threshold": round(threshold, 2)},
    }), 200
