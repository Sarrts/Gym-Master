from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import db, User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for("main.index"))
        flash("Error en los datos.")
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = User(
            nombre=request.form.get("nombre"),
            email=request.form.get("email"),
            telefono=request.form.get("telefono"),
            password=generate_password_hash(
                request.form.get("password"), method="pbkdf2:sha256"
            ),
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
