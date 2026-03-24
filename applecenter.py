<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{product.name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background:#fff; font-family:-apple-system, system-ui, sans-serif; }
        .color-option { width:30px; height:30px; border-radius:50%; border:2px solid #eee; cursor:pointer; }
        .color-option.active { border-color:#007aff; transform:scale(1.2); }
        .storage-card { border:2px solid #f5f5f7; border-radius:12px; padding:15px; cursor:pointer; text-align:center; transition:0.2s; }
        .storage-card.active { border-color:#007aff; background:#f5faff; }
    </style>
</head>
<body class="p-6 md:p-12">

<div class="max-w-6xl mx-auto flex flex-col md:flex-row gap-12">
    <div class="w-full md:w-1/2 bg-[#f5f5f7] rounded-3xl p-10 flex items-center justify-center sticky top-5 h-[500px]">
        <img src="{{product.image}}" class="max-h-full object-contain drop-shadow-xl" id="mainImg">
    </div>

    <div class="w-full md:w-1/2 space-y-8">
        <a href="/" class="text-blue-600 text-sm">← Mağazaya qayıt</a>
        <h1 class="text-5xl font-bold tracking-tight">{{product.name}}</h1>
        <p class="text-3xl font-light" id="priceTag">{{product.price}} AZN</p>

        {% if product.color_list %}
        <div>
            <p class="text-xs font-bold text-gray-400 mb-3 uppercase">Rəng seçin</p>
            <div class="flex gap-4">
                {% for c in product.color_list %}
                <div class="color-option" style="background:{{c}};" onclick="setActive(this, 'color-option')"></div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% if product.storage_list %}
        <div>
            <p class="text-xs font-bold text-gray-400 mb-3 uppercase">Yaddaş seçin</p>
            <div class="grid grid-cols-2 gap-4">
                {% for s in product.storage_list %}
                <div class="storage-card" onclick="updatePrice(this, {{loop.index0}})">
                    <p class="font-bold">{{s}}</p>
                    <p class="text-xs text-gray-400">+{{loop.index0 * 200}} AZN</p>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <button class="w-full bg-[#007aff] text-white py-5 rounded-2xl text-xl font-bold shadow-lg shadow-blue-200">
            Sifariş et
        </button>
    </div>
</div>

<script>
    let base = parseInt("{{product.price}}");
    function setActive(el, cls) {
        document.querySelectorAll('.'+cls).forEach(i => i.classList.remove('active', 'border-blue-500'));
        el.classList.add('active', 'border-blue-500');
    }
    function updatePrice(el, idx) {
        setActive(el, 'storage-card');
        document.getElementById('priceTag').innerText = (base + (idx * 200)) + " AZN";
    }
</script>
</body>
</html>
