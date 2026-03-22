import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "caseroom_secret_2026"

# ================= DATABASE CONNECTION =================
def get_db_connection():
    # Vercel Postgres tərəfindən verilən əsas dəyişənlər
    uri = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    
    if not uri:
        raise ValueError("Verilənlər bazası linki (POSTGRES_URL) tapılmadı! Vercel-də Storage hissəsini yoxlayın.")

    # SQLAlchemy və bəzi driverlər üçün 'postgres://' olan hissəni 'postgresql://' etmək vacibdir
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # sslmode=require PostgreSQL uzaqdan qoşulmalar üçün vacibdir
    return psycopg2.connect(uri)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Cədvəllərin yaradılması
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, product TEXT, username TEXT, status TEXT DEFAULT 'Gözləmədə')")
    cur.execute("CREATE TABLE IF NOT EXISTS admin (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    
    # İlkin admin hesabı
    cur.execute("SELECT * FROM admin WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO admin (username, password) VALUES ('admin', '1234')")
    
    conn.commit()
    cur.close()
    conn.close()

# Sayt işə düşəndə bazanı yoxla və cədvəlləri yarat
try:
    init_db()
except Exception as e:
    print(f"Baza xətası: {e}")

# ================= ROUTES =================
@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", products=products)

# Login, Register və Admin hissələri eyni qaydada qalır...
# Sadəcə bazaya qoşularkən get_db_connection() funksiyasından istifadə et.

if __name__ == "__main__":
    app.run()
