import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_db_connection():
    # Vercel-dəki Postgres linkini götürürük
    url = os.environ.get('POSTGRES_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
        cur.close(); conn.close()
        return render_template("index.html", products=products)
    except Exception as e:
        return f"Ana səhifə xətası: {str(e)}"

@app.route("/product/<int:id>")
def product_detail(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id=%s", (id,))
        product = cur.fetchone()
        cur.close(); conn.close()
        
        if not product: return "Məhsul tapılmadı", 404

        # Məlumatları təmizləyirik ki, səhifə çökməsin
        product['color_list'] = product.get('colors', "").split(',') if product.get('colors') else []
        product['storage_list'] = product.get('storages', "").split(',') if product.get('storages') else []
        
        return render_template("product.html", product=product)
    except Exception as e:
        return f"Məhsul səhifəsi xətası: {str(e)}"

# Admin hissəsini də sadələşdiririk
@app.route("/admin")
def admin():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin.html", products=products)

@app.route("/admin/add", methods=["POST"])
def add():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, image, category, colors, storages) VALUES (%s,%s,%s,%s,%s,%s)",
        (request.form['name'], request.form['price'], request.form['image'], 
         request.form.get('category', 'iPhone'), request.form.get('colors', ''), request.form.get('storages', ''))
    )
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

application = app
