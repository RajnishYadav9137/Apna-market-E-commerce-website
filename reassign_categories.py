import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from store.models import Product
from catalog.models import Category

cat_mapping = {
    1: 23,   # Tata Salt -> Sugar & Salt (Grocery)
    2: 20,   # Atta -> Atta & Flour (Grocery)
    3: 21,   # Oil -> Oil & Ghee (Grocery)
    4: 18,   # Rice -> Rice & Grains (Grocery)
    5: 19,   # Dal -> Dal & Pulses (Grocery)
    6: 22,   # Masala -> Spices & Masala (Grocery)
    7: 38,   # Milk -> Milk (Dairy)
    8: 40,   # Paneer -> Paneer (Dairy)
    9: 39,   # Dahi -> Curd (Dairy)
    10: 41,  # Butter -> Butter (Dairy)
    11: 13,  # Tomatoes -> Vegetables (Fruits & Veg)
    12: 13,  # Capsicum -> Vegetables (Fruits & Veg)
    13: 14,  # Palak -> Leafy Vegetables (Fruits & Veg)
    14: 12,  # Apples -> Fresh Fruits (Fruits & Veg)
    15: 12,  # Bananas -> Fresh Fruits (Fruits & Veg)
    16: 29,  # Matka -> Matka (Desi Mitti)
    17: 31,  # Kulhad -> Kulhad (Desi Mitti)
    18: 32,  # Diya -> Diya (Desi Mitti)
    19: 102, # Agarbatti -> Agarbatti (Puja)
    20: 105, # Puja Thali -> Puja Thali (Puja)
    21: 6,   # Saree -> Saree (Clothes & Fashion)
    22: 7,   # Kurta -> Kurta (Clothes & Fashion)
    23: 46,  # Kadhai -> Steel Utensils (Kitchen)
    24: 72,  # Charger -> Chargers & Cables (Electronics)
    25: 73,  # Earbuds -> Earphones (Electronics)
    26: 25,  # Maggi -> Biscuits & Snacks (Grocery)
    27: 25,  # Parle-G -> Biscuits & Snacks (Grocery)
    28: 25,  # Aloo Bhujia -> Biscuits & Snacks (Grocery)
    29: 24,  # Tata Tea -> Tea & Coffee (Grocery)
    30: 42,  # Ghee -> Ghee (Dairy)
    31: 13,  # Onions -> Vegetables (Fruits & Veg)
    32: 13,  # Potatoes -> Vegetables (Fruits & Veg)
    33: 80,  # Soap -> Soap (Beauty & Personal Care)
    34: 23,  # Honey -> Sugar & Salt (Grocery)
    35: 51,  # Cooker -> Cookware (Kitchen)
}

for pid, cid in cat_mapping.items():
    try:
        p = Product.objects.get(id=pid)
        c = Category.objects.get(id=cid)
        p.category = c
        p.save()
        parent_name = c.parent.name if c.parent else "None"
        print(f"Assigned #{pid} {p.name[:25]} -> {parent_name} > {c.name}")
    except Exception as e:
        print(f"Error for #{pid}: {e}")

extras = [
    {
        "id": 36,
        "name": "Desi Hybrid Kitchen Garden Seeds (Pack of 10 Varieties)",
        "cat_id": 109,
        "description": "High germination desi kitchen garden seeds pack including Tomato, Chilli, Palak, Bhindi, Coriander, Brinjal and Cucumber.",
        "price": Decimal("249.00"),
        "discount": Decimal("40.16"),
        "stock": Decimal("150.00"),
        "unit": "pack",
        "weight": "Pack of 10 Seed Packets",
        "brand": "Kisan Suvidha",
        "image": "products/seeds.jpg",
    },
    {
        "id": 37,
        "name": "Heavy Duty Carbon Steel Gardening Khurpi / Trowel",
        "cat_id": 111,
        "description": "Traditional village forged carbon steel khurpi with smooth wooden handle. Ideal for soil preparation, weeding, and potting plants.",
        "price": Decimal("250.00"),
        "discount": Decimal("28.00"),
        "stock": Decimal("85.00"),
        "unit": "piece",
        "weight": "Heavy Gauge Steel",
        "brand": "Kisan Craft",
        "image": "products/trowel.jpg",
    },
    {
        "id": 38,
        "name": "Dabur Vatika Enriched Coconut Hair Oil (300 ml)",
        "cat_id": 82,
        "description": "Pure coconut hair oil enriched with 7 Ayurvedic herbs including Brahmi, Amla, and Henna for deep root nourishment and strength.",
        "price": Decimal("175.00"),
        "discount": Decimal("17.14"),
        "stock": Decimal("110.00"),
        "unit": "bottle",
        "weight": "300 ml Bottle",
        "brand": "Dabur",
        "image": "products/hair_oil.jpg",
    },
    {
        "id": 39,
        "name": "VoltPro High-Speed Braided USB Type-C Fast Cable",
        "cat_id": 72,
        "description": "Tangle-free military grade nylon braided 65W fast-charging cable with reinforced stress-relief collars. Universal compatibility.",
        "price": Decimal("299.00"),
        "discount": Decimal("50.17"),
        "stock": Decimal("140.00"),
        "unit": "piece",
        "weight": "1.5 Metre Length",
        "brand": "VoltPro",
        "image": "products/cable.jpg",
    },
]

for item in extras:
    pid = item.pop("id")
    cid = item.pop("cat_id")
    cat = Category.objects.get(id=cid)
    item["category"] = cat
    item["is_available"] = True
    prod, created = Product.objects.update_or_create(id=pid, defaults=item)
    status_str = "Created" if created else "Updated"
    print(f"[{status_str}] #{prod.id} {prod.name[:25]} -> {cat.parent.name} > {cat.name}")

print("\nAll products successfully mapped to correct root and sub categories!")
