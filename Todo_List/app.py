import os
from datetime import datetime, timezone

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


STATUSES = ("À faire", "En cours", "Terminé")
NEXT_STATUS = {
    "À faire": "En cours",
    "En cours": "Terminé",
}

app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-secret-key"),
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///todo.db"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)
CSRFProtect(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="À faire")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


def get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    return task


def render_board(edit_task=None):
    tasks_by_status = {
        status: Task.query.filter_by(status=status)
        .order_by(Task.created_at.desc(), Task.id.desc())
        .all()
        for status in STATUSES
    }
    return render_template(
        "index.html",
        statuses=STATUSES,
        tasks_by_status=tasks_by_status,
        edit_task=edit_task,
    )


@app.get("/")
def index():
    return render_board()


@app.post("/tasks")
def create_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "À faire")

    if not title:
        flash("Le titre est obligatoire.", "error")
    elif len(title) > 120:
        flash("Le titre ne peut pas dépasser 120 caractères.", "error")
    elif len(description) > 1000:
        flash("La description ne peut pas dépasser 1 000 caractères.", "error")
    elif status not in STATUSES:
        flash("Veuillez choisir un statut valide.", "error")
    else:
        db.session.add(
            Task(title=title, description=description or None, status=status)
        )
        db.session.commit()
        flash("La tâche a été ajoutée.", "success")

    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task_or_404(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "")

        if not title:
            flash("Le titre est obligatoire.", "error")
        elif len(title) > 120:
            flash("Le titre ne peut pas dépasser 120 caractères.", "error")
        elif len(description) > 1000:
            flash("La description ne peut pas dépasser 1 000 caractères.", "error")
        elif status not in STATUSES:
            flash("Veuillez choisir un statut valide.", "error")
        else:
            task.title = title
            task.description = description or None
            task.status = status
            db.session.commit()
            flash("La tâche a été mise à jour.", "success")
            return redirect(url_for("index"))

    return render_board(edit_task=task)


@app.post("/tasks/<int:task_id>/advance")
def advance_task(task_id):
    task = get_task_or_404(task_id)
    next_status = NEXT_STATUS.get(task.status)
    if next_status is None:
        flash("Cette tâche est déjà terminée.", "info")
    else:
        task.status = next_status
        db.session.commit()
        flash(f"Tâche déplacée vers « {next_status} ».", "success")
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/toggle-complete")
def toggle_complete(task_id):
    task = get_task_or_404(task_id)
    task.status = "À faire" if task.status == "Terminé" else "Terminé"
    db.session.commit()
    flash("Le statut de la tâche a été mis à jour.", "success")
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    task = get_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("La tâche a été supprimée définitivement.", "success")
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
