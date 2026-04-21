import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import db, Plan, Seccion, TablaDia, Ejercicio, Reseña

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    planes = Plan.query.all()
    return render_template("index.html", planes=planes, viendo_favoritos=False)


@main.route("/mis-favoritos")
@login_required
def ver_favoritos():
    planes = current_user.planes_favoritos
    return render_template("index.html", planes=planes, viendo_favoritos=True)


@main.route("/toggle-favorito/<int:plan_id>")
@login_required
def toggle_favorito(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    if plan in current_user.planes_favoritos:
        current_user.planes_favoritos.remove(plan)
    else:
        current_user.planes_favoritos.append(plan)
    db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


@main.route("/reseñar/<int:plan_id>", methods=["POST"])
@login_required
def reseñar(plan_id):
    estrellas = request.form.get("estrellas")
    comentario = request.form.get("comentario")
    if estrellas:
        nueva = Reseña(
            estrellas=int(estrellas),
            comentario=comentario,
            user_id=current_user.id,
            plan_id=plan_id,
        )
        db.session.add(nueva)
        db.session.commit()
    return redirect(url_for("main.ver_plan", id=plan_id))


@main.route("/plan/<int:id>")
@login_required
def ver_plan(id):
    plan = Plan.query.get_or_404(id)
    return render_template("detalle.html", plan=plan)


@main.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if not current_user.is_admin:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        img = request.files.get("imagen_portada")
        nombre_img = "default.jpg"
        if img and img.filename != "":
            nombre_img = secure_filename(img.filename)
            img.save(
                os.path.join(current_app.config["UPLOAD_FOLDER_IMAGES"], nombre_img)
            )

        nuevo_plan = Plan(titulo=request.form["titulo"], imagen_portada=nombre_img)
        db.session.add(nuevo_plan)
        db.session.flush()

        for texto in request.form.getlist("seccion_texto[]"):
            if texto.strip():
                db.session.add(Seccion(contenido=texto, plan_id=nuevo_plan.id))

        dias = request.form.getlist("nombre_dia[]")
        ej_por_tabla = request.form.getlist("ej_por_tabla[]")
        ej_nombres = request.form.getlist("ej_nombre[]")
        ej_series = request.form.getlist("ej_series[]")
        ej_reps = request.form.getlist("ej_reps[]")
        ej_descansos = request.form.getlist("ej_descanso[]")
        ej_videos = request.files.getlist("ej_video[]")

        idx_ej = 0
        for i, nombre_dia in enumerate(dias):
            t = TablaDia(nombre_dia=nombre_dia, plan_id=nuevo_plan.id)
            db.session.add(t)
            db.session.flush()
            for _ in range(int(ej_por_tabla[i])):
                if idx_ej < len(ej_nombres):
                    v_name = None
                    if idx_ej < len(ej_videos) and ej_videos[idx_ej].filename != "":
                        v_file = ej_videos[idx_ej]
                        v_name = secure_filename(v_file.filename)
                        v_file.save(
                            os.path.join(
                                current_app.config["UPLOAD_FOLDER_VIDEOS"], v_name
                            )
                        )
                    ej = Ejercicio(
                        nombre=ej_nombres[idx_ej],
                        series=int(ej_series[idx_ej] or 0),
                        reps=int(ej_reps[idx_ej] or 0),
                        descanso=int(ej_descansos[idx_ej] or 0),
                        video_url=v_name,
                        tabla_id=t.id,
                    )
                    db.session.add(ej)
                idx_ej += 1
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("crear.html")


@main.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    if current_user.is_admin:
        plan = Plan.query.get_or_404(id)
        db.session.delete(plan)
        db.session.commit()
    return redirect(url_for("main.index"))
