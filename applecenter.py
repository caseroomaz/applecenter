import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# 🔥 SAFE DB CONNECT
def db():
    try:
        url = os.environ.get("POSTGRES_URL")

        if not url:
            print("❌ POSTGRES_URL yoxdur")
            return None

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://")

        return psycopg2.connect(url)

    except Exception as e:
        print("DB ERROR:", e)
        return None

# INIT (error verməsin deyə safe)
def init():
    conn = db()
    if not conn:
        return

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
    id SERIAL PRIMARY KEY,
    name TEXT,
    price INT,
    image TEXT,
    category TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS wishlist(
    id SERIAL PRIMARY KEY,
    product_id INT
    )
    """)

    conn.commit()
    conn.close()

init()

# 🔥 FALLBACK DATA (DB yoxdursa)
def fake_products():
    return [
        {
            "id":1,
            "name":"iPhone 17 Pro",
            "price":3499,
            "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-model-unselect-gallery-2-202409",
            "likes":5
        },
        {
            "id":2,
            "name":"AirPods Max",
            "price":1299,
            "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-max-select-202409-silver",
            "likes":3
        }
    ]

# HOME
@app.route("/")
def home():
    try:
        conn = db()

        if not conn:
            return render_template("index.html", products=fake_products())

        cur = conn.cursor(cursor_factory=RealDictCursor)

        q = request.args.get("q")

        if q:
            cur.execute("""
            SELECT p.*, COUNT(w.id) as likes
            FROM products p
            LEFT JOIN wishlist w ON p.id=w.product_id
            WHERE p.name ILIKE %s
            GROUP BY p.id
            """, ('%'+q+'%',))
        else:
            cur.execute("""
            SELECT p.*, COUNT(w.id) as likes
            FROM products p
            LEFT JOIN wishlist w ON p.id=w.product_id
            GROUP BY p.id
            ORDER BY p.id DESC
            """)

        data = cur.fetchall()
        return render_template("index.html", products=data)

    except Exception as e:
        return f"ERROR: {str(e)}"

# PRODUCT
@app.route("/product/<int:id>")
def product(id):
    try:
        conn = db()

        if not conn:
            p = fake_products()[0]
        else:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM products WHERE id=%s",(id,))
            p = cur.fetchone()

        p["images"]=[p["image"], p["image"], p["image"]]
        p["color_list"]=["black","silver","gold"]
        p["storage_list"]=["128GB","256GB","512GB"]

        return render_template("product.html", product=p)

    except Exception as e:
        return f"ERROR: {str(e)}"

# FAVORITE
@app.route("/wishlist/add/<int:id>")
def fav(id):
    conn = db()

    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO wishlist(product_id) VALUES(%s)",(id,))
        conn.commit()

    return redirect("/")

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

    conn = db()

    if not conn:
        return "DB yoxdur"

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")

    return render_template("admin.html", products=cur.fetchall())

# ADD PRODUCT (UPLOAD safe)
@app.route("/admin/add", methods=["POST"])
def add():
    if "admin" not in session:
        return redirect("/admin/login")

    conn = db()

    if not conn:
        return "DB yoxdur"

    file = request.files["image"]

    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
    else:
        path = ""

    cur = conn.cursor()
    cur.execute("""
    INSERT INTO products(name,price,image,category)
    VALUES(%s,%s,%s,%s)
    """,(request.form["name"], request.form["price"], path, request.form["category"]))

    conn.commit()

    return redirect("/admin")

# DELETE
@app.route("/admin/delete/<int:id>")
def delete(id):
    conn = db()

    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=%s",(id,))
        conn.commit()

    return redirect("/admin")

# API
@app.route("/api/products")
def api_products():
    conn = db()

    if not conn:
        return jsonify({"data": fake_products()})

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products")

    return jsonify({"data": cur.fetchall()})

application = apps
