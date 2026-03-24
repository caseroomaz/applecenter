from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "applecenter_2026_premium_key"

# Admin məlumatları
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# -----------------------------------
# Məhsullar və Wishlist
# -----------------------------------
products = [
    {
        "id": 1,
        "name": "iPhone 17 Pro",
        "price": 3499,
        "category": "iPhone",
        "image": "",  # buraya link əlavə et
        "colors": ["#1c1c1e","#f5f5f7","#d4af37"],
        "likes": 0
    },
    {
        "id": 2,
        "name": "iPhone 17",
        "price": 2699,
        "category": "iPhone",
        "image": "",  # buraya link əlavə et
        "colors": ["#3a3a3c","#ffd1dc","#c7fcec"],
        "likes": 0
    },
    {
        "id": 3,
        "name": "AirPods 4",
        "price": 1299,
        "category": "AirPods",
        "image": "https://avatars.mds.yandex.net/i?id=f6b9fe5672c5d819ec4d890481faeb0a582798af-4216017-images-thumbs&n=13",  # buraya link əlavə et
        "colors": ["#e5e5ea","#a2845e","#000000"],
        "likes": 0
    }
]

# -----------------------------------
# Ana səhifə
# -----------------------------------
@app.route("/")
def home():
    q = request.args.get("q")
    filtered = [p for p in products if q.lower() in p["name"].lower()] if q else products
    return render_template("index.html", products=filtered)

# -----------------------------------
# Kateqoriya səhifəsi
# -----------------------------------
@app.route("/category/<cat>")
def category(cat):
    filtered = [p for p in products if p["category"] == cat]
    return render_template("index.html", products=filtered)

# -----------------------------------
# Product səhifəsi
# -----------------------------------
@app.route("/product/<int:id>")
def product(id):
    p = next((x for x in products if x["id"] == id), products[0])
    p["images"] = [p["image"], p["image"], p["image"]]  # Demo üçün eyni şəkil
    p["storage_list"] = ["128GB","256GB","512GB"]
    return render_template("product.html", product=p)

# -----------------------------------
# Wishlist (Favori)
# -----------------------------------
@app.route("/wishlist/add/<int:id>")
def wishlist_add(id):
    for p in products:
        if p["id"] == id:
            p["likes"] += 1
    return redirect("/")

# -----------------------------------
# Admin login
# -----------------------------------
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["u"]==ADMIN_USER and request.form["p"]==ADMIN_PASS:
            session["admin"]=True
            return redirect("/admin")
    return render_template("admin_login.html")

# -----------------------------------
# Admin panel
# -----------------------------------
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin/login")
    return render_template("admin.html", products=products)

# -----------------------------------
# Məhsul əlavə et (link ilə)
# -----------------------------------
@app.route("/admin/add", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect("/admin/login")
    new_id = max([p["id"] for p in products]) + 1 if products else 1
    products.append({
        "id": new_id,
        "name": request.form["name"],
        "price": int(request.form["price"]),
        "image": request.form["image"],   # buraya link əlavə edəcəksən
        "category": request.form.get("category","Other"),
        "colors": ["#000","#fff"],  # default colors
        "likes":0
    })
    return redirect("/admin")

# -----------------------------------
# Məhsul sil
# -----------------------------------
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return redirect("/admin")

# -----------------------------------
# API (istəyə görə)
# -----------------------------------
@app.route("/api/products")
def api_products():
    return {"data": products}

application = app
