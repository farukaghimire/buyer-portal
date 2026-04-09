from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default="buyer")

class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    property_id = db.Column(db.Integer, nullable=False)
    property_name = db.Column(db.String(200), nullable=False)
    property_image = db.Column(db.String(500), nullable=False)