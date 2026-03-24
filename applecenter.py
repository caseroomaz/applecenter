import os
from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "secret123"

# 🔥 FAKE DATA (Vercel üçün stabil)
products = [
    {
        "id":1,
        "name":"iPhone 17 Pro",
        "price":3499,
        "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-model-unselect-gallery-2-202409",
        "likes":10
    },
    {
        "id":2,
        "name":"AirPods Max",
        "price":1299,
        "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-max-select-202409-silver",
        "likes":5
    }
]

# HOME
@app.route("/")
def home():
    q = request.args.get("q")

    if q:
        filtered = [p for p in products if q.lower() in p["name"].lower()]
    else:
        filtered = products

    return render_template("index.html", products=filtered)

# PRODUCT
@app.route("/product/<int:id>")
def product(id):
    p = next((x for x in products if x["id"] == id), products[0])

    p["images"]=[p["image"], p["image"], p["image"]]
    p["color_list"]=["black","silver","gold"]
    p["storage_list"]=["128GB","256GB","512GB"]

    return render_template("product.html", product=p)

# FAVORITE
@app.route("/wishlist/add/<int:id>")
def fav(id):
    for p in products:
        if p["id"] == id:
            p["likes"] += 1
    return redirect("/")

# ADMIN LOGIN
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["u"]=="admin" and request.form["p"]=="1234":
            session["admin"]=True
            return redirect("/admin")
    return "<form method='POST'><input name='u'><input name='p'><button>Login</button></form>"

# ADMIN PANEL
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin/login")

    return "<h1>Admin Panel işləyir ✅</h1>"

# API
@app.route("/api/products")
def api_products():
    return jsonify({"data": products})

application = app
