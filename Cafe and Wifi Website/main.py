import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import or_
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False, default=False)
    has_toilet = db.Column(db.Boolean, nullable=False, default=False)
    has_wifi = db.Column(db.Boolean, nullable=False, default=False)
    can_take_calls = db.Column(db.Boolean, nullable=False, default=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250))


class CafeForm(FlaskForm):
    name = StringField(
        "Nom du café",
        validators=[DataRequired(), Length(max=250)],
    )
    map_url = StringField(
        "Lien Google Maps",
        validators=[DataRequired(), URL(), Length(max=500)],
    )
    img_url = StringField(
        "URL de l’image",
        validators=[DataRequired(), URL(), Length(max=500)],
    )
    location = StringField(
        "Ville / quartier",
        validators=[DataRequired(), Length(max=250)],
    )
    has_sockets = BooleanField("Prises électriques")
    has_toilet = BooleanField("Toilettes")
    has_wifi = BooleanField("Wi-Fi")
    can_take_calls = BooleanField("Appels autorisés")
    seats = StringField(
        "Nombre de places",
        validators=[DataRequired(), Length(max=250)],
    )
    coffee_price = StringField("Prix du café", validators=[Length(max=250)])
    submit = SubmitField("Enregistrer le café")


class UpdatePriceForm(FlaskForm):
    coffee_price = StringField(
        "Nouveau prix",
        validators=[DataRequired(), Length(max=250)],
    )
    submit = SubmitField("Mettre à jour")


class DeleteCafeForm(FlaskForm):
    submit = SubmitField("Supprimer")


class CafeFilterForm(FlaskForm):
    location = StringField("Ville ou quartier")
    wifi = SelectField(
        "Wi-Fi",
        choices=[
            ("", "Tous les cafés"),
            ("yes", "Wi-Fi disponible"),
            ("no", "Sans Wi-Fi"),
        ],
    )
    submit = SubmitField("Filtrer")


def find_cafes(search_term="", wifi=""):
    query = Cafe.query
    search_term = search_term.strip()

    if search_term:
        escaped_term = (
            search_term.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        pattern = f"%{escaped_term}%"
        query = query.filter(
            or_(
                Cafe.name.ilike(pattern, escape="\\"),
                Cafe.location.ilike(pattern, escape="\\"),
            )
        )

    if wifi == "yes":
        query = query.filter(Cafe.has_wifi.is_(True))
    elif wifi == "no":
        query = query.filter(Cafe.has_wifi.is_(False))

    return query.order_by(Cafe.name).all()


@app.route("/")
def home():
    filters = CafeFilterForm(request.args)
    wifi = request.args.get("wifi", "")
    if wifi not in {"", "yes", "no"}:
        flash("Le filtre Wi-Fi fourni n’est pas valide.", "warning")
        wifi = ""
        filters.wifi.data = wifi

    cafes = find_cafes(filters.location.data or "", wifi)
    return render_template(
        "index.html",
        cafes=cafes,
        filters=filters,
        delete_form=DeleteCafeForm(),
        title="Tous les cafés",
    )


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        if Cafe.query.filter_by(name=name).first():
            flash("Un café portant ce nom existe déjà.", "danger")
        else:
            cafe = Cafe(
                name=name,
                map_url=form.map_url.data.strip(),
                img_url=form.img_url.data.strip(),
                location=form.location.data.strip(),
                has_sockets=form.has_sockets.data,
                has_toilet=form.has_toilet.data,
                has_wifi=form.has_wifi.data,
                can_take_calls=form.can_take_calls.data,
                seats=form.seats.data.strip(),
                coffee_price=form.coffee_price.data.strip() or None,
            )
            db.session.add(cafe)
            db.session.commit()
            flash("Le café a été ajouté.", "success")
            return redirect(url_for("home"))

    return render_template(
        "add_cafe.html",
        form=form,
        title="Ajouter un café",
    )


@app.route("/update/<int:cafe_id>", methods=["GET", "POST"])
def update_price(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    form = UpdatePriceForm()
    if form.validate_on_submit():
        cafe.coffee_price = form.coffee_price.data.strip()
        db.session.commit()
        flash("Le prix du café a été mis à jour.", "success")
        return redirect(url_for("home"))

    if request.method == "GET":
        form.coffee_price.data = cafe.coffee_price

    return render_template(
        "update.html",
        form=form,
        cafe=cafe,
        title="Modifier le prix",
    )


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    form = DeleteCafeForm()
    if not form.validate_on_submit():
        flash("La demande de suppression n’a pas pu être vérifiée.", "danger")
        return redirect(url_for("home"))

    cafe = Cafe.query.get_or_404(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    flash("Le café a été supprimé.", "success")
    return redirect(url_for("home"))


@app.route("/search")
def search():
    search_term = request.args.get("location", "").strip()
    wifi = request.args.get("wifi", "")
    if wifi not in {"", "yes", "no"}:
        flash("Le filtre Wi-Fi fourni n’est pas valide.", "warning")
        wifi = ""

    return render_template(
        "search.html",
        cafes=find_cafes(search_term, wifi),
        location=search_term,
        wifi=wifi,
        delete_form=DeleteCafeForm(),
        title="Résultats de recherche",
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()
