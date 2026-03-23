import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "applecenter_secret"

# DB
def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

# INIT
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name TEXT,
        price TEXT,
        image TEXT,
        description TEXT)
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
        id SERIAL PRIMARY KEY,
        p_name TEXT,
        c_name TEXT,
        phone TEXT)
        """)
        conn.commit()
        cur.close()
        conn.close()

init_db()

# HOME
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", products=products)

# PRODUCT DETAIL
@app.route("/product/<int:id>")
def product_detail(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cur.fetchone()
    cur.close(); conn.close()

    if not product:
        return "Product tapılmadı"

    return render_template("product.html", product=product)

# ORDER
@app.route("/order", methods=["POST"])
def order():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (p_name,c_name,phone) VALUES (%s,%s,%s)",
        (request.form['p_name'], request.form['c_name'], request.form['phone'])
    )
    conn.commit()
    cur.close(); conn.close()
    return redirect("/")

# ADMIN
@app.route("/admin")
def admin():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin.html", products=products, orders=orders)

# ADD
@app.route("/admin/add", methods=["POST"])
def add():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products(name,price,image,description) VALUES(%s,%s,%s,%s)",
        (
            request.form['name'],
            request.form['price'],
            request.form['image'],
            request.form['description']
        )
    )
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

# DELETE
@app.route("/admin/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

application = app
