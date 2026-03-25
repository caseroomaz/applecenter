from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "applecenter_2026_premium_key"

# Admin məlumatları
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# -----------------------------------
# Məhsullar
# -----------------------------------
products = [
    {
        "id": 1,
        "name": "iPhone 17 Pro Max",
        "price": 3499,
        "category": "iPhone",
        "images": [
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=NUNzdzNKR0FJbmhKWm5YamRHb05tUzkyK3hWak1ybHhtWDkwUXVINFc0RkZqUFNQc3E5VDh2SEx1ZlJpSjNkR0FOL1haWCt6TDJ0UWlLb09XajVNdENYR1ZZZnEyMVlVQUliTThGMjNyaFFxbm9iakpBWkhjT1hBM3BZeU9zQ0JzNmlxRHcrTG16TVFTaEZGMjZVM3ZB&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch_AV1?wid=5120&hei=2880&fmt=webp&qlt=90&.v=NUNzdzNKR0FJbmhKWm5YamRHb05tUzkyK3hWak1ybHhtWDkwUXVINFc0RUNxZ2Y2UndFVkhoZG1DQ0NWVTFWa2xjZnhHRHJyenVmME5KTm9Sd1ZaU3NqbWRhTGpRM2xxVWJRWUhSaDlCQ3E0aFZQSlZXTG00RTR2aXlYRzBpVUxlODBad1VqYUZ3RW54YkRKL2hzbXVR&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch-deepblue?wid=5120&hei=2880&fmt=webp&qlt=90&.v=NUNzdzNKR0FJbmhKWm5YamRHb05tUzkyK3hWak1ybHhtWDkwUXVINFc0RWhhOHJGRUNHdlh6a3VuZVVqdnNrNXVHdDcxbVFRSnhaQ0pnV1pOaG5KaGhNQnJMcnc4RkxJd3ZMc3hKZVVFWHREelVULzVXd2xCbVltNVMyUXhsYlBpMEowc2xaa1ByZlpMdyt3ZFlhVkhn&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-202509-6-9inch-silver?wid=5120&hei=2880&fmt=webp&qlt=90&.v=NUNzdzNKR0FJbmhKWm5YamRHb05tUzkyK3hWak1ybHhtWDkwUXVINFc0RVRqUkJqUGFyN1pGMnlaV3JkWU9jdjF1TmpsTkNoRVRMR1N6UXlVZFBaU0NYR1ZZZnEyMVlVQUliTThGMjNyaFFxd1ZHd3R2RmlpWk50MW5LU2N1cWNxdlBsK2ZicnRLY2oza08vTDBZeXZ3&traceId=1"
        ],
        "colors": ["#f5f5f7","#0A1F44","#FF8C00"],
        "likes": 0
    },
    {
        "id": 2,
        "name": "iPhone 17",
        "price": 2699,
        "category": "iPhone",
        "images": [
            "/static/iphone17_front.png",
            "/static/iphone17_back.png",
            "/static/iphone17_back.png",
            "/static/iphone17_back.png",
            "/static/iphone17_back.png",
            "/static/iphone17_top.png"
        ],
        "colors": ["#3a3a3c","#f5f5f7","#E6E6FA","#9CAF88","#A9C6D8"],
        "likes": 0
    },
    {
        "id": 3,
        "name": "AirPods 4",
        "price": 1299,
        "category": "AirPods",
        "images": [
            "/static/airpods4_front.png",
            "/static/airpods4_case.png"
        ],
        "likes": 0
    }
]

cart_items = []

# -----------------------------------
# Səbət sistemi
# -----------------------------------
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
    p["storage_list"] = ["128GB","256GB","512GB"]
    return render_template("product.html", product=p)

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
        "images": [request.form["image"]],
        "category": request.form.get("category","Other"),
        "colors": ["#000","#fff"],
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
