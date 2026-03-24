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

def db():
    url = os.environ.get("POSTGRES_URL")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://")
    return psycopg2.connect(url)

# INIT
def init():
    conn = db()
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

# HOME + SEARCH + LIKE COUNT
@app.route("/")
def home():
    q = request.args.get("q")

    conn = db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

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

    return render_template("index.html", products=cur.fetchall())

# PRODUCT PAGE
@app.route("/product/<int:id>")
def product(id):
    conn = db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM products WHERE id=%s",(id,))
    p = cur.fetchone()

    p["images"]=[p["image"], p["image"], p["image"]]
    p["color_list"]=["black","silver","gold"]
    p["storage_list"]=["128GB","256GB","512GB"]

    return render_template("product.html", product=p)

# FAVORITE
@app.route("/wishlist/add/<int:id>")
def fav(id):
    conn = db()
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
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")

    return render_template("admin.html", products=cur.fetchall())

# ADD PRODUCT (UPLOAD)
@app.route("/admin/add", methods=["POST"])
def add():
    if "admin" not in session:
        return redirect("/admin/login")

    file = request.files["image"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    conn = db()
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
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s",(id,))
    conn.commit()
    return redirect("/admin")

# API (mobil üçün)
@app.route("/api/products")
def api_products():
    conn = db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products")
    return jsonify({"data": cur.fetchall()})

application = app
