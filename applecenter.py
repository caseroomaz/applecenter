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
            "data:image/jpeg;base64,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",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-black_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=WGdCRlQ0YVlqbTdXTEkxRnVQb0oxa3pYQjBteGp2cFFHL09TNGhVUUhxeHFkSUJZcmNjVXZ4cDk3YTVMcWk4SHF2TWlpSzUzejRCZGt2SjJUNGl1VEE4bm1RcmlWRWp2eDN1WHNkSjNmUlkwQ2hTNHZjREFYdVBRanJ6N1p0WHI&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-white_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=WGdCRlQ0YVlqbTdXTEkxRnVQb0oxclZmSzgzdlhzQS95ekpRalhXU0JMVkRQR0pzaFhHemZ3ZzZNcDlHRHpJYnF2TWlpSzUzejRCZGt2SjJUNGl1VEE4bm1RcmlWRWp2eDN1WHNkSjNmUmFBdlBzZ01jTzlOOGhYc3dpcENYM2Y&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-lavender_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=WGdCRlQ0YVlqbTdXTEkxRnVQb0oxbGoraU1aeXdWbEh0SUtyMmtxWGg5dUpDNHBIcmowQ3VoNVJwTm5xckpDV2xjZnhHRHJyenVmME5KTm9Sd1ZaU3NqbWRhTGpRM2xxVWJRWUhSaDlCQ3FTZnZjRTZTT0R6VFJnZ01JbHJqd0hlODBad1VqYUZ3RW54YkRKL2hzbXVR&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-sage_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=WGdCRlQ0YVlqbTdXTEkxRnVQb0oxZ3VBTlNROXF1MzBwZUoyNEVtMWw3aEtLUmpmVEZhTFpRYkxNWDZBb1R3dGd2S3NaRzcrU0dmYjNHTUFiMnlsWFUxSlgrVWMrMzU1OXo2c2JyNjJZTGcvWXoydVhtUUJyekgyU21tRjFxUUM&traceId=1",
            "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-finish-select-202509-mistblue_GEO_US?wid=5120&hei=2880&fmt=webp&qlt=90&.v=WGdCRlQ0YVlqbTdXTEkxRnVQb0oxcFYyWWhPSUg0YytZdmJ2dmY4d09xckN0VFdyaFlNakY5MGMxMWhINEhMWmxjZnhHRHJyenVmME5KTm9Sd1ZaU3NqbWRhTGpRM2xxVWJRWUhSaDlCQ3JHYmE3Q0tucGdwdjhDQ1JZbjRxQXRka0xmckVNVTBkS20yTzkwa0dhU09n&traceId=1"

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
