import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = "caseroom_secret_2026"

# ================= DB CONNECTION =================
def get_db_connection():
    uri = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(uri)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Cədvəlləri PostgreSQL formatında yaradırıq
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS wishlist (id SERIAL PRIMARY KEY, username TEXT, product_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, product TEXT, username TEXT, status TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS admin (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    
    # Admin yoxdursa yarat
    cur.execute("SELECT * FROM admin WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO admin (username, password) VALUES ('admin', '1234')")
    
    conn.commit()
    cur.close()
    conn.close()

# İlk işə düşəndə bazanı hazırla
try:
    init_db()
except Exception as e:
    print(f"DB Error: {e}")

# ================= AUTH =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u, p = request.form["username"], request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (u, p))
            conn.commit()
            return redirect("/login")
        except:
            return "Bu istifadəçi artıq mövcuddur!"
        finally:
            cur.close(); conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u, p = request.form["username"], request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
        user = cur.fetchone()
        cur.close(); conn.close()
        if user:
            session["user"] = u
            return redirect("/")
    return render_template("login.html")

# ================= HOME + SEARCH =================
@app.route("/")
def home():
    q = request.args.get("q")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if q:
        cur.execute("SELECT * FROM products WHERE name ILIKE %s", ('%' + q + '%',))
    else:
        cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close(); conn.close()
    return render_template("index.html", products=products)

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session: return redirect("/admin_login")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        name, price = request.form["name"], request.form["price"]
        image = request.form["image"] # Vercel-də link istifadə etmək daha yaxşıdır
        cur.execute("INSERT INTO products (name, price, image) VALUES (%s, %s, %s)", (name, price, image))
        conn.commit()

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cur.fetchall()
    cur.execute("SELECT COUNT(*) as count FROM users")
    user_count = cur.fetchone()['count']
    
    cur.close(); conn.close()
    return render_template("admin.html", products=products, orders=orders, users=user_count)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("admin_login.html")

@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session: return redirect("/")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cur.close(); conn.close()
    return redirect("/admin")

# ================= ORDER =================
@app.route("/order/<int:id>")
def order(id):
    if "user" not in session: return redirect("/login")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products WHERE id=%s", (id,))
    p = cur.fetchone()
    if p:
        cur.execute("INSERT INTO orders (product, username, status) VALUES (%s, %s, %s)", 
                    (p[0], session["user"], "Hazırlanır"))
        conn.commit()
    cur.close(); conn.close()
    return redirect("/my_orders")

@app.route("/my_orders")
def my_orders():
    if "user" not in session: return redirect("/login")
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM orders WHERE username=%s", (session["user"],))
    orders = cur.fetchall()
    cur.close(); conn.close()
    return render_template("orders.html", orders=orders)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
