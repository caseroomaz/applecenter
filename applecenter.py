from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "applecenter_2026_premium_key"

# Admin məlumatları
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# Mövcud məhsullar (heç bir şey silinməyib)
products = [
    {
        "id": 1,
        "name": "iPhone 17 Pro Max",
        "price": 3199,
        "category": "iPhone",
        "images": [
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch_AV1?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch-deepblue?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch-silver?wid=5120&hei=2880&fmt=webp&qlt=90"
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
            "https://www.apple.com/v/iphone-17/e/images/overview/welcome/hero_startframe__e9e7pcnguyqi_xlarge.jpg",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-black_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-white_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-lavender_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-sage_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-mistblue_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90"
        ],
        "colors": ["#3a3a3c","#f5f5f7","#E6E6FA","#9CAF88","#A9C6D8"],
        "likes": 0
    },
    {
        "id": 3,
        "name": "AirPods 4",
        "price": 349,
        "category": "AirPods",
        "images": [
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/airpods-4-anc-select-202409_FV1?wid=976&hei=916&fmt=jpeg&qlt=90"
        ],
        "colors": ["#ffffff"],
        "likes": 0
    }
]

cart_items = []

# ---------- PUBLIC ROUTES ----------
@app.route("/")
def home():
    q = request.args.get("q")
    filtered = [p for p in products if q and q.lower() in p["name"].lower()] if q else products
    return render_template("index.html", products=filtered)

@app.route("/category/<cat>")
def category(cat):
    filtered = [p for p in products if p["category"] == cat]
    return render_template("index.html", products=filtered)

@app.route("/product/<int:id>")
def product(id):
    p = next((x for x in products if x["id"] == id), products[0])
    if p["category"] != "AirPods":
        p["storage_list"] = ["128GB","256GB","512GB"]
    else:
        p["storage_list"] = []
    return render_template("product.html", product=p)

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

# ---------- ADMIN ROUTES ----------
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["u"]==ADMIN_USER and request.form["p"]==ADMIN_PASS:
            session["admin"]=True
            return redirect("/admin")
        else:
            return "İstifadəçi adı və ya şifrə səhvdir!"
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

    images = request.form.getlist("images[]")
    colors = request.form.getlist("colors[]")
    
    products.append({
        "id": new_id,
        "name": request.form["name"],
        "price": int(request.form["price"]),
        "category": request.form.get("category","Other"),
        "images": images if images else [request.form["image"]],
        "colors": colors if colors else ["#000","#fff"],
        "likes":0
    })
    return redirect("/admin")

@app.route("/admin/delete/<int:id>")
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return redirect("/admin")

application = app
