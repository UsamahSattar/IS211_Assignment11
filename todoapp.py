from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db

bp = Blueprint("todoapp", __name__)


# index bp
@bp.route("/")
def index():
    db = get_db()
    user_id = g.user["id"]
    lists = db.execute(
        "SELECT p.id, title, complete, created, user_id, username"
        " FROM todo p JOIN user u ON p.user_id = u.id"
        " WHERE p.user_id = ?"
        " ORDER BY created ASC",
        (user_id,),
    ).fetchall()
    return render_template("todo/index.html", lists=lists)


# create pb
@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        # body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO todo (title,  user_id)" " VALUES (?,  ?)",
                (title, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("todoapp.index"))

    return render_template("todo/create.html")


# getting a single list
def get_list(id, check_author=True):
    list = (
        get_db()
        .execute(
            "SELECT p.id, title, created, user_id, username"
            " FROM todo p JOIN user u ON p.user_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if list is None:
        abort(404, f"List id {id} doesn't exist.")

    if check_author and list["user_id"] != g.user["id"]:
        abort(403)

    return list


# update bp
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    list = get_list(id)

    if request.method == "POST":
        title = request.form["title"]
        # body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE todo SET title = ?" " WHERE id = ?", (title, id))
            db.commit()
            return redirect(url_for("todoapp.index"))

    return render_template("todo/update.html", list=list)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_list(id)
    db = get_db()
    db.execute("DELETE FROM todo WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("todoapp.index"))


@bp.route("/<int:id>/complete", methods=("POST",))
@login_required
def complete(id):
    # list = get_list(id)
    db = get_db()
    db.execute("UPDATE todo SET complete = TRUE WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("todoapp.index"))


@bp.route("/<int:id>/incomplete", methods=("POST",))
@login_required
def incomplete(id):
    # list = get_list(id)
    db = get_db()
    db.execute("UPDATE todo SET complete = FALSE WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("todoapp.index"))
