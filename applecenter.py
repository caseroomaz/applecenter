# 🔥 FULL PROFESSIONAL PHONE STORE (ALL FEATURES INCLUDED)

from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DB =================

def db():
    return sqlite3.connect("shop.db")

conn = db()
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,name TEXT,price TEXT,image TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT,password TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS wishlist(id INTEGER PRIMARY KEY,user TEXT,product_id INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,product TEXT,user TEXT,status TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS admin(id INTEGER PRIMARY KEY,username TEXT,password TEXT)")

cur.execute("SELECT * FROM admin WHERE username='admin'")
if not cur.fetchone():
    cur.execute("INSERT INTO admin(username,password) VALUES('admin','1234')")

conn.commit()
conn.close()

# ================= AUTH =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        conn = db()
        conn.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        conn = db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
        if cur.fetchone():
            session["user"] = u
            return redirect("/")
    return render_template("login.html")

# ================= HOME + SEARCH =================
@app.route("/")
def home():
    q = request.args.get("q")
    conn = db()
    cur = conn.cursor()

    if q:
        cur.execute("SELECT * FROM products WHERE name LIKE ?",('%'+q+'%',))
    else:
        cur.execute("SELECT * FROM products")

    products = cur.fetchall()
    conn.close()
    return render_template("index.html", products=products)

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        file = request.files["image"]
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        conn = db()
        conn.execute("INSERT INTO products(name,price,image) VALUES(?,?,?)",
                     (name,price,filename))
        conn.commit()
        conn.close()

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    conn.close()

    return render_template("admin.html", products=products, orders=orders, users=users)

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u=="admin" and p=="1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("admin_login.html")

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    conn.execute("DELETE FROM products WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# EDIT
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn = db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        conn.execute("UPDATE products SET name=?,price=? WHERE id=?",(name,price,id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    cur.execute("SELECT * FROM products WHERE id=?",(id,))
    product = cur.fetchone()
    conn.close()
    return render_template("edit.html", product=product)

# ================= WISHLIST =================
@app.route("/wishlist/<int:id>")
def wishlist(id):
    if "user" not in session:
        return redirect("/login")
    conn = db()
    conn.execute("INSERT INTO wishlist(user,product_id) VALUES(?,?)",
                 (session["user"],id))
    conn.commit()
    conn.close()
    return redirect("/")

# ================= ORDER =================
@app.route("/order/<int:id>")
def order(id):
    if "user" not in session:
        return redirect("/login")

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM products WHERE id=?",(id,))
    p = cur.fetchone()

    conn.execute("INSERT INTO orders(product,user,status) VALUES(?,?,?)",
                 (p[0],session["user"],"Hazırlanır"))
    conn.commit()
    conn.close()

    return redirect("/my_orders")

@app.route("/my_orders")
def my_orders():
    if "user" not in session:
        return redirect("/login")

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT product,status FROM orders WHERE user=?",(session["user"],))
    orders = cur.fetchall()
    conn.close()

    return render_template("orders.html", orders=orders)

# UPDATE STATUS
@app.route("/status/<int:id>/<s>")
def status(id,s):
    conn = db()
    conn.execute("UPDATE orders SET status=? WHERE id=?",(s,id))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ================= CHATBOT =================
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("msg","").lower()

    if "salam" in msg:
        r="Salam!"
    elif "qiymət" in msg:
        r="Qiymətlər məhsullarda var"
    else:
        r="Başqa sual verin"

    return jsonify({"reply":r})

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)

# ================= FRONTEND (SHORT) =================

# index.html
"""
<meta name=viewport content="width=device-width, initial-scale=1">
<style>
body{background:black;color:white}
.card{display:inline-block;margin:10px;transition:.3s}
.card:hover{transform:scale(1.1)}
</style>

<form>
<input name=q placeholder="Axtar">
</form>

{% for p in products %}
<div class=card>
<h3>{{p[1]}}</h3>
<p>{{p[2]}}</p>
<img src="/static/uploads/{{p[3]}}" width=120>
<br>
<a href="/order/{{p[0]}}">Al</a>
<a href="/wishlist/{{p[0]}}">❤️</a>
</div>
{% endfor %}

<a href="/my_orders">Sifarişlərim</a>
"""
