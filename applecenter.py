import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "applecenter_secret_key_2026"


# ================= DB CONNECTION =================
def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url:
        return None
    try:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except Exception as e:
        print("DB error:", e)
        return None


# ================= INIT DB =================
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            price TEXT,
            image TEXT,
            description TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            p_name TEXT,
            c_name TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Gözləmədə'
        )
        """)

        conn.commit()
        cur.close()
        conn.close()


# ================= SEED DATA =================
def seed_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")

        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO products (name, price, image) VALUES (%s,%s,%s)",
                ("iPhone 17 Pro Max", "3499",
                 "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-model-unselect-gallery-2-202409")
            )

            cur.execute(
                "INSERT INTO products (name, price, image) VALUES (%s,%s,%s)",
                ("iPhone 17", "2699",
                 "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-model-unselect-gallery-1-202409")
            )

            cur.execute(
                "INSERT INTO products (name, price, image) VALUES (%s,%s,%s)",
                ("AirPods Max", "1299",
                 "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/airpods-max-select-202409-silver")
            )

            conn.commit()

        cur.close()
        conn.close()


# ================= START =================
init_db()
seed_db()


# ================= HOME =================
@app.route("/")
def index():
    conn = get_db_connection()
    if not conn:
        return "<h1>Baza qoşulmayıb</h1>"

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", products=products)


# ================= PRODUCT DETAIL =================
@app.route("/product/<int:id>")
def product_detail(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("product.html", product=product)


# ================= ORDER =================
@app.route("/order", methods=["POST"])
def place_order():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO orders (p_name, c_name, phone) VALUES (%s,%s,%s)",
            (
                request.form['p_name'],
                request.form['c_name'],
                request.form['phone']
            )
        )

        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("index"))


# ================= ADMIN =================
@app.route("/admin")
def admin_panel():
    conn = get_db_connection()
    if not conn:
        return "DB error"

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()

    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin.html", products=products, orders=orders)


# ADD PRODUCT
@app.route("/admin/add", methods=["POST"])
def add_product():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO products (name, price, image) VALUES (%s,%s,%s)",
            (
                request.form['name'],
                request.form['price'],
                request.form['image']
            )
        )

        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("admin_panel"))


# DELETE PRODUCT
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()

        cur.execute("DELETE FROM products WHERE id=%s", (id,))

        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("admin_panel"))


# ================= VERCEL =================
application = app
