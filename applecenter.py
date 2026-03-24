@app.route("/product/<int:id>")
def product_detail(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id=%s", (id,))
        # fetchone() bizə RealDictRow qaytarır, onu dict-ə çeviririk
        row = cur.fetchone()
        cur.close(); conn.close()
        
        if not row: return "Məhsul tapılmadı", 404
        
        product = dict(row) # Xətanın qarşısını alan əsas sətir

        # Şəkilləri list halına salırıq
        img_list = [product['image']]
        if product.get('extra_images'):
            img_list.extend(product['extra_images'].split(','))
        product['images'] = img_list # İndi 'images' açarı mövcuddur

        product['color_list'] = product.get('colors', "").split(',') if product.get('colors') else []
        product['storage_list'] = product.get('storages', "").split(',') if product.get('storages') else []
        
        return render_template("product.html", product=product)
    except Exception as e:
        return f"Məhsul səhifəsi xətası: {str(e)}"
