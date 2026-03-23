import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template

app = Flask(__name__)
# Vercel üçün bu vacibdir!
app.debug = True

def get_db_connection():
    url = os.environ.get('POSTGRES_URL')
    if not url: return None
    try:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except:
        return None

@app.route("/")
def index():
    conn = get_db_connection()
    if not conn:
        return "Baza qoşulmayıb! Vercel Storage-da Connect etdiyini yoxla."
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image TEXT)")
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", products=products)
    except Exception as e:
        return f"Səhv: {str(e)}"

# BU HİSSƏ ÇOX VACİBDİR
application = app

if __name__ == "__main__":
    app.run()
