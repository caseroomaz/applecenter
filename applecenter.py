@app.route("/product/<int:id>")
def product_detail(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id=%s", (id,))
        row = cur.fetchone()
        cur.close(); conn.close()
        
        if not row: return "Məhsul tapılmadı", 404
        
        # RealDictRow-u normal lüğətə (dict) çeviririk ki, xəta verməsin
        product = dict(row)

        # Şəkilləri hazırlayırıq
        img_list = [product['image']]
        if product.get('extra_images'):
            # Vergüllə ayrılmış linkləri listə çeviririk
            img_list.extend([i.strip() for i in product['extra_images'].split(',') if i.strip()])
        
        product['images'] = img_list
        product['color_list'] = product.get('colors', "").split(',') if product.get('colors') else []
        product['storage_list'] = product.get('storages', "").split(',') if product.get('storages') else []
        
        return render_template("product.html", product=product)
    except Exception as e:
        return f"Məhsul səhifəsi xətası: {str(e)}"
