import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "caseroom_2026_key"

# ================= DATABASE CONNECTION =================
def get_db_connection():
    try:
        url = os.environ.get('POSTGRES_URL')
        if not url: return None
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except:
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC, image TEXT, stock INTEGER DEFAULT 10)")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'user')")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, username TEXT, product_name TEXT, status TEXT DEFAULT 'Gözləmədə')")
        
        cur.execute("SELECT * FROM users WHERE username='admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        
        conn.commit()
        cur.close(); conn.close()

init_db()

# ================= ROUTES =================
@app.route("/")
def index():
    conn = get_db_connection()
    if not conn:
        return "Baza qoşulmayıb! Vercel-də 'Connect' düyməsini yoxla."
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
        cur.close(); conn.close()
        return render_template("index.html", products=products)
    except Exception as e:
        return f"Səhv: {str(e)}"

@app.route("/admin")
def admin():
    if session.get('role') != 'admin':
        return "Giriş qadağandır!"
    return "Admin Panel Tezliklə..."

if __name__ == "__main__":
    app.run(debug=True)
