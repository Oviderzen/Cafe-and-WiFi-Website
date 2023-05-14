from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)
# db.init_app


#Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def read_database(self):
        with app.app_context():
            database = db.session.execute(db.select(Cafe)).scalars()
            return database.all()


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    img_url = StringField("Cafe Image Link (URL)", validators=[DataRequired(), URL()])
    location = StringField('Cafe Location (London Area)', validators=[DataRequired()])
    has_sockets = BooleanField('Does the Cafe have power sockets?')
    has_toilet = BooleanField('Does the Cafe have a toilet?')
    has_wifi = BooleanField('Does the Cafe have WiFi access?')
    can_take_calls = BooleanField('Can you take calls from the Cafe?')
    seats = StringField('Approximately how many seats does the Cafe have?', validators=[DataRequired()])
    coffee_price = StringField('How much does a coffee cost?', validators=[DataRequired()])
    submit = SubmitField('Add Cafe')


class PriceForm(FlaskForm):
    coffee_price = StringField('How much does a coffee cost?', validators=[DataRequired()])
    submit = SubmitField('Update Price')


@app.route("/")
def home():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).all()
    return render_template("index.html", all_cafes=all_cafes)


@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    form = CafeForm()
    if form.is_submitted():
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect('/')
    return render_template('add.html', form=form)


@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH", "POST"])
def update_price(cafe_id):
    form = PriceForm()
    if form.is_submitted():
        db.session.query(Cafe).get(cafe_id)
        db.session.query(Cafe).filter_by(id=cafe_id).update(dict(coffee_price=request.form.get('coffee_price')))
        db.session.commit()
        return redirect('/')
    return render_template('modify_price.html', form=form)


@app.route('/delete-cafe/<int:cafe_id>', methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    to_delete = db.session.query(Cafe).get(cafe_id)
    if to_delete:
        db.session.delete(to_delete)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)