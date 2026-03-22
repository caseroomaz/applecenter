import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "caseroom_secret_key"

# ================= BAZA İLƏ ƏLAQƏ =================
def get_db_connection():
    try:
        # Vercel-in verdiyi rəsmi linki götürürük
        url = os.environ.get('POSTGRES_URL')
        
        if not url:
            return None

        # Vercel üçün postgres:// hissəsini postgresql:// etmək mütləqdir
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        return psycopg2.connect(url)
    except:
        return None

# Cədvəlləri avtomatik yaradan funksiya
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, product TEXT, username TEXT, status TEXT DEFAULT 'Gözləmədə')")
        cur.execute("CREATE TABLE IF NOT EXISTS admin (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
        
        # Admin yoxdursa yarat
        cur.execute("SELECT * FROM admin WHERE username='admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO admin (username, password) VALUES ('admin', '1234')")
            
        conn.commit()
        cur.close()
        conn.close()

# Sayt açılanda bazanı yoxla
init_db()

# ================= ROUTES =================
@app.route("/")
def hello():
    conn = get_db_connection()
    if not conn:
        return "Salam! Sayt isleyir, amma BAZA QOSULMAYIB. Vercel Storage-da Connect etdiyini yoxla."
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products ORDER BY id DESC")
        products = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", products=products)
    except Exception as e:
        return f"Səhv: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
