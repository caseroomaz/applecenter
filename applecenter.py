import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "caseroom_ultra_secret_2026"

def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url: return None
    try:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except: return None

# Baza Strukturunu Qurmaq
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC, image TEXT, description TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, product_name TEXT, customer_name TEXT, phone TEXT, status TEXT DEFAULT 'Gözləmədə')")
        conn.commit()
        cur.close(); conn.close()

init_db()

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", products=products)

@app.route("/order", methods=["POST"])
def place_order():
    name = request.form.get("customer_name")
    phone = request.form.get("phone")
    p_name = request.form.get("product_name")
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (product_name, customer_name, phone) VALUES (%s, %s, %s)", (p_name, name, phone))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('index'))

# --- ADMIN FUNKSİYALARI ---
@app.route("/admin/delete/<int:id>")
def delete_product(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()
    cur.close(); conn.close()
    return redirect(url_for('index'))

application = app
