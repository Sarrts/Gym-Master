from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


favoritos = db.Table(
    "favoritos",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("plan_id", db.Integer, db.ForeignKey("plan.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    planes_favoritos = db.relationship(
        "Plan",
        secondary=favoritos,
        backref=db.backref("usuarios_que_guardaron", lazy="dynamic"),
    )


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    imagen_portada = db.Column(db.String(200))
    secciones = db.relationship("Seccion", backref="plan", cascade="all, delete-orphan")
    tablas = db.relationship("TablaDia", backref="plan", cascade="all, delete-orphan")
    reseñas = db.relationship("Reseña", backref="plan", cascade="all, delete-orphan")

    @property
    def media_estrellas(self):
        if not self.reseñas:
            return 0
        total = sum(r.estrellas for r in self.reseñas)
        return round(total / len(self.reseñas), 1)


class Reseña(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estrellas = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    usuario = db.relationship("User", backref="mis_reseñas")


class Seccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text)
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))


class TablaDia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_dia = db.Column(db.String(100))
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    ejercicios = db.relationship(
        "Ejercicio", backref="tabla", cascade="all, delete-orphan"
    )


class Ejercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    series = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    descanso = db.Column(db.Integer)
    video_url = db.Column(db.String(200))
    tabla_id = db.Column(db.Integer, db.ForeignKey("tabla_dia.id"))
