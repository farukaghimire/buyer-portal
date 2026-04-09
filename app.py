from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Favourite
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-jwt-key'  # change for production

# ✅ ADD THESE (JWT COOKIE CONFIG)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# Sample properties with Unsplash images
PROPERTIES = [
    {
        "id": 1,
        "name": "Ocean View Apartment",
        "image": "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=800&q=80",
        "description": "A modern apartment with a stunning ocean view, 2 bedrooms, 2 bathrooms, and a spacious balcony.",
        "price": "$350,000",
        "location": "Miami, FL"
    },
    {
        "id": 2,
        "name": "Modern Loft",
        "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "description": "Stylish loft with open floor plan, high ceilings, and industrial design elements.",
        "price": "$420,000",
        "location": "New York, NY"
    },
    {
        "id": 3,
        "name": "Cozy Cottage",
        "image": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
        "description": "Charming cottage surrounded by nature, featuring 3 bedrooms, a fireplace, and a garden.",
        "price": "$280,000",
        "location": "Asheville, NC"
    },
    {
        "id": 4,
        "name": "Luxury Villa",
        "image": "https://images.unsplash.com/photo-1599423300746-b62533397364?auto=format&fit=crop&w=800&q=80",
        "description": "A luxurious villa with private pool, modern amenities, and panoramic views of the city.",
        "price": "$1,200,000",
        "location": "Los Angeles, CA"
    },
    {
        "id": 5,
        "name": "City Penthouse",
        "image": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800&q=80",
        "description": "Elegant penthouse in the heart of the city with rooftop terrace, 3 bedrooms, and smart home features.",
        "price": "$950,000",
        "location": "Chicago, IL"
    }
]

@app.route("/")
def index():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        if User.query.filter_by(email=data['email']).first():
            return "Email already exists", 400
        hashed_pw = generate_password_hash(data['password'])
        new_user = User(email=data['email'], password=hashed_pw, name=data['name'])
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return "Invalid credentials", 401

        access_token = create_access_token(identity=str(user.id))

        response = redirect("/dashboard")
        set_access_cookies(response, access_token)  # ✅ FIXED

        return response
    return render_template("login.html")

@app.route("/dashboard")
@jwt_required(locations=["cookies"])  # ✅ FIXED
def dashboard():
    user_id = int(get_jwt_identity()) # ✅ FIXED
    user = User.query.get(user_id)
    favourites = Favourite.query.filter_by(user_id=user.id).all()
    return render_template("dashboard.html", user=user, favourites=favourites, properties=PROPERTIES)

@app.route("/favourites/add", methods=["POST"])
@jwt_required(locations=["cookies"])  # ✅ FIXED
def add_favourite():
    user_id = int(get_jwt_identity()) # ✅ FIXED
    data = request.json
    if Favourite.query.filter_by(user_id=user_id, property_id=data['id']).first():
        return jsonify({"message": "Already in favourites"}), 400
    fav = Favourite(
        user_id=user_id,
        property_id=data['id'],
        property_name=data['name'],
        property_image=data['image']
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Added to favourites"}), 200

@app.route("/favourites/remove", methods=["POST"])
@jwt_required(locations=["cookies"])  # ✅ FIXED
def remove_favourite():
    user_id = int(get_jwt_identity())# ✅ FIXED
    data = request.json
    fav = Favourite.query.filter_by(user_id=user_id, property_id=data['id']).first()
    if not fav:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Removed from favourites"}), 200

# ✅ OPTIONAL (but good for interview)
@app.route("/logout", methods=["POST"])
def logout():
    response = redirect("/login")
    # Clear the access token cookie
    response.set_cookie("access_token", "", expires=0)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)