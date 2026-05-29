import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "course-design-secret-key-2026")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'shop.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Production mode
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Frontend static files path (for production)
    FRONTEND_DIR = os.environ.get(
        "FRONTEND_DIR",
        os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist"),
    )
