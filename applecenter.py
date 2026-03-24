@app.route("/product/<int:id>")
def product_detail(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM products WHERE id=%s", (id,))
        row = cur.fetchone()
        cur.close(); conn.close()
        
        if not row: 
            return "Məhsul tapılmadı", 404
        
        # Obyekti lüğətə çeviririk ki,['images'] açarını əlavə edə bilək
        product = dict(row)

        # Şəkilləri emal edirik
        all_images = []
        if product.get('image'):
            all_images.append(product['image'])
        
        # Əgər əlavə şəkillər varsa, onları da siyahıya qatırıq
        if product.get('extra_images'):
            extra = [img.strip() for img in product['extra_images'].split(',') if img.strip()]
            all_images.extend(extra)
        
        # Əgər heç bir şəkil yoxdursa, boş qalmasın deyə placeholder qoyuruq
        product['images'] = all_images if all_images else ["https://via.placeholder.com/600x600?text=No+Image"]

        # Rəng və yaddaş siyahıları
        product['color_list'] = product.get('colors', "").split(',') if product.get('colors') else []
        product['storage_list'] = product.get('storages', "").split(',') if product.get('storages') else []
        
        return render_template("product.html", product=product)
    except Exception as e:
        return f"Məhsul səhifəsi xətası: {str(e)}"
