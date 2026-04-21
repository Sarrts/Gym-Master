import os
from flask import Flask
from flask_login import LoginManager
from .models import db, User
from werkzeug.security import generate_password_hash


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "..", "templates"),
        static_folder=os.path.join(base_dir, "..", "static"),
    )

    app.config["SECRET_KEY"] = "clave_segura_gym"

    # --- CONFIGURACIÓN POSTGRESQL ---
    DB_USER = "postgres"
    DB_PASS = "1234"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "fitness_db"

    # Construcción de la URL de conexión
    DATABASE_LOCAL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    uri = os.environ.get("DATABASE_URL", DATABASE_LOCAL)
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER_VIDEOS"] = os.path.join(app.static_folder, "videos")
    app.config["UPLOAD_FOLDER_IMAGES"] = os.path.join(app.static_folder, "uploads")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@gym.com").first():
            hashed_pw = generate_password_hash("admin123", method="pbkdf2:sha256")
            admin = User(
                nombre="Admin", email="admin@gym.com", password=hashed_pw, is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    return app
