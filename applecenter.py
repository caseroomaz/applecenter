from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "applecenter_2026_premium_key"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ---------------- PRODUCTS ----------------
products = [
    {
        "id": 1,
        "name": "iPhone 17 Pro Max",
        "price": 3499,
        "category": "iPhone",
        "image": "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch_GEO_US?wid=5120&hei=2880&fmt=webp",
        "colors": ["#1c1c1e","#f5f5f7","#d4af37"],
        "likes": 0
    },
    {
        "id": 2,
        "name": "iPhone 17",
        "price": 2699,
        "category": "iPhone",
        "image": "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-unselect-gallery-1-202509_GEO_US?wid=5120&hei=2880&fmt=webp",
        "colors": ["#3a3a3c","#ffd1dc","#c7fcec"],
        "likes": 0
    },
    {
        "id": 3,
        "name": "AirPods 4",
        "price": 1299,
        "category": "AirPods",
        "image": "https://www.apple.com/v/airpods-4/g/images/overview/bento-gallery/bento_case_close__f0fhueeeoy2q_xlarge_2x.jpg",
        "colors": ["#e5e5ea","#a2845e","#000000"],
        "likes": 0
    }
]

# ---------------- HOME + SEARCH ----------------
@app.route("/")
def home():
    q = request.args.get("q")
    filtered = [p for p in products if q.lower() in p["name"].lower()] if q else products
    return render_template("index.html", products=filtered)

# ---------------- CATEGORY ----------------
@app.route("/category/<cat>")
def category(cat):
    filtered = [p for p in products if p["category"] == cat]
    return render_template("index.html", products=filtered)

# ---------------- PRODUCT ----------------
@app.route("/product/<int:id>")
def product(id):
    p = next((x for x in products if x["id"] == id), products[0])
    p["images"] = [p["image"], p["image"], p["image"]]
    p["storage_list"] = ["128GB","256GB","512GB"]
    return render_template("product.html", product=p)

# ---------------- CART ----------------
@app.route("/cart/add/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    session.modified = True
    return redirect("/cart")

@app.route("/cart")
def cart():
    cart_ids = session.get("cart", [])
    cart_items = [p for p in products if p["id"] in cart_ids]
    total = sum([p["price"] for p in cart_items])
    return render_template("cart.html", items=cart_items, total=total)

# ---------------- ADMIN ----------------
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["u"]==ADMIN_USER and request.form["p"]==ADMIN_PASS:
            session["admin"]=True
            return redirect("/admin")
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin.html", products=products)

@app.route("/admin/add", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect("/admin/login")
    new_id = max([p["id"] for p in products]) + 1 if products else 1
    products.append({
        "id": new_id,
        "name": request.form["name"],
        "price": int(request.form["price"]),
        "image": request.form["image"],
        "category": request.form.get("category","Other"),
        "colors": ["#000","#fff"],
        "likes":0
    })
    return redirect("/admin")

@app.route("/admin/delete/<int:id>")
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return redirect("/admin")

application = app
