import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "applecenter_secret_key_123"

def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Sütunları tək-tək yoxlayıb əlavə edirik (Xəta verməməsi üçün)
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image TEXT, description TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, p_name TEXT, c_name TEXT, phone TEXT)")
        
        # Yeni sütunları ehtiyatla əlavə edirik
        cols = [('category', 'TEXT'), ('colors', 'TEXT'), ('storages', 'TEXT')]
        for col_name, col_type in cols:
            try:
                cur.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
            except:
                conn.rollback()
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

@app.route("/product/<int:id>")
def product_detail(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cur.fetchone()
    cur.close(); conn.close()
    
    if not product: return "Məhsul tapılmadı", 404

    # Xəta verməməsi üçün yoxlama:
    product['color_list'] = product.get('colors').split(',') if product.get('colors') else []
    product['storage_list'] = product.get('storages').split(',') if product.get('storages') else []
    
    return render_template("product.html", product=product)

@app.route("/admin/add", methods=["POST"])
def add():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, image, description, category, colors, storages) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (request.form['name'], request.form['price'], request.form['image'], 
         request.form.get('description', ''), request.form.get('category', 'iphone'),
         request.form.get('colors', ''), request.form.get('storages', ''))
    )
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

@app.route("/admin")
def admin():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin.html", products=products)

@app.route("/admin/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

application = app
