import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.secret_key = "caseroom_ultra_secret_2026"

# ================= DATABASE CONNECTION =================
def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

def init_db():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    # Cədvəllərin yaradılması
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC, image TEXT, category TEXT, stock INTEGER DEFAULT 10)")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, fullname TEXT, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'user')")
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, username TEXT, product_name TEXT, price NUMERIC, status TEXT DEFAULT 'Gözləmədə', date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS favorites (id SERIAL PRIMARY KEY, username TEXT, product_id INTEGER)")
    
    # İlkin Admin
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (fullname, username, password, role) VALUES ('Admin Uzeyir', 'admin', 'admin123', 'admin')")
    
    conn.commit()
    cur.close(); conn.close()

init_db()

# ================= ROUTES =================

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", products=products)

# --- USER SYSTEM ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Qeydiyyat məntiqi bura yazılacaq
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == 'admin' and pw == 'admin123':
            session['user'] = 'admin'
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
    return render_template("login.html")

# --- SHOPPING & ORDERS ---
@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    # Səbət məntiqi (Session-da saxlamaq)
    return redirect(url_for('index'))

@app.route("/order", methods=['POST'])
def place_order():
    # Sifariş və Satus sistemi
    return jsonify({"status": "success", "message": "Sifarişiniz qəbul edildi!"})

# --- ADMIN DASHBOARD ---
@app.route("/admin")
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM products")
    prods = cur.fetchall()
    cur.execute("SELECT * FROM orders ORDER BY date DESC")
    orders = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin.html", products=prods, orders=orders)

# --- AI CHATBOT (Süni İntellekt) ---
@app.route("/chat", methods=['POST'])
def chat():
    user_msg = request.json.get("message", "").lower()
    # Sadə AI cavab məntiqi
    if "salam" in user_msg: response = "Salam! CaseRoom AI köməkçisiyəm. Sizə necə kömək edə bilərəm?"
    elif "qiymət" in user_msg: response = "Ən yeni iPhone modellərimizin qiyməti 1500 AZN-dən başlayır."
    else: response = "Üzr istəyirəm, bunu hələ öyrənməmişəm. Amma adminimiz sizə zəng edə bilər."
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
