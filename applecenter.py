from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "applecenter_2026_premium_key"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

products = [
    {
        "id": 1,
        "name": "iPhone 17 Pro Max",
        "price": 3199,
        "category": "iPhone",
        "images": [
            "https://store.storeimages.cdn-apple.com/iphone1.jpg",
            "https://store.storeimages.cdn-apple.com/iphone2.jpg"
        ],
        "colors": ["#f5f5f7","#0A1F44","#FF8C00"],
        "likes": 0
    },
    {
        "id": 2,
        "name": "iPhone 17",
        "price": 2249,
        "category": "iPhone",
        "images": [
            "https://www.apple.com/iphone.jpg"
        ],
        "colors": ["#3a3a3c","#f5f5f7"],
        "likes": 0
    },
    {
        "id": 3,
        "name": "AirPods 4",
        "price": 349,
        "category": "AirPods",
        "images": [
            "https://store.storeimages.cdn-apple.com/airpods.jpg"
        ],
        "likes": 0
    }
]

cart_items = []

# ANA SƏHİFƏ
@app.route("/")
def home():
    q = request.args.get("q")
    filtered = [p for p in products if q.lower() in p["name"].lower()] if q else products
    return render_template("index.html", products=filtered)

# KATEQORİYA
@app.route("/category/<cat>")
def category(cat):
    filtered = [p for p in products if p["category"] == cat]
    return render_template("index.html", products=filtered)

# PRODUCT
@app.route("/product/<int:id>")
def product(id):
    p = next((x for x in products if x["id"] == id), products[0])

    # 🔥 ƏLAVƏ (storage yalnız uyğun məhsullar üçün)
    if p["category"] != "AirPods":
        p["storage_list"] = ["128GB","256GB","512GB"]
    else:
        p["storage_list"] = []

    return render_template("product.html", product=p)

# CART
@app.route("/cart")
def cart():
    total = sum(item['price'] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/cart/add/<int:id>")
def cart_add(id):
    p = next((x for x in products if x["id"] == id), None)
    if p:
        cart_items.append(p)
    return redirect("/cart")

# ADMIN LOGIN
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["u"]==ADMIN_USER and request.form["p"]==ADMIN_PASS:
            session["admin"]=True
            return redirect("/admin")
    return render_template("admin_login.html")

# ADMIN PANEL
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin.html", products=products)

# ADD PRODUCT
@app.route("/admin/add", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect("/admin/login")

    new_id = max([p["id"] for p in products]) + 1 if products else 1

    products.append({
        "id": new_id,
        "name": request.form["name"],
        "price": int(request.form["price"]),
        "images": [request.form["image"]],
        "category": request.form.get("category","Other"),
        "colors": ["#000","#fff"],
        "likes":0
    })

    return redirect("/admin")

# DELETE
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return redirect("/admin")

application = app
