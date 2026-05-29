from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, LoginLog

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供注册信息"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    region = data.get("region", "").strip()

    if not username or not email or not password:
        return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "用户名已存在"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "邮箱已被注册"}), 400

    user = User(username=username, email=email, role="customer", region=region)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "注册成功", "user": user.to_dict()}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供登录信息"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401

    # Record login log
    ip = request.remote_addr or ""
    log = LoginLog(user_id=user.id, login_time=datetime.now(timezone.utc), ip_address=ip)
    db.session.add(log)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "username": user.username},
    )
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({"user": user.to_dict()}), 200
