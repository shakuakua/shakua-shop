import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db

jwt = JWTManager()


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    # Register API blueprints
    from auth import auth_bp
    from routes_customer import customer_bp
    from routes_sales import sales_bp
    from routes_admin import admin_bp
    from routes_data import data_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(data_bp)

    # ── Production: serve Vue static files ──
    frontend_dir = app.config.get("FRONTEND_DIR")
    if frontend_dir and os.path.isdir(frontend_dir):
        assets_dir = os.path.join(frontend_dir, "assets")

        # Serve static assets (JS/CSS/images)
        @app.route("/assets/<path:filename>")
        def serve_assets(filename):
            return send_from_directory(assets_dir, filename)

        # Serve index.html for all non-API routes (SPA fallback)
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            file_path = os.path.join(frontend_dir, path)
            if path and os.path.isfile(file_path):
                return send_from_directory(frontend_dir, path)
            return send_from_directory(frontend_dir, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
