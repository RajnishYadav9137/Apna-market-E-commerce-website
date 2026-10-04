import os
import io
import shutil
import urllib.request
from PIL import Image

# Ensure media/products exists
os.makedirs("media/products", exist_ok=True)

brain_dir = r"C:\Users\rajne\.gemini\antigravity-ide\brain\59525938-ba20-4d55-afb7-407b43254fee"

# 1. Process AI-generated branded images
generated_mappings = {
    "salt.jpg": "tata_salt_pack",
    "atta.jpg": "aashirvaad_atta_pack",
    "oil.jpg": "fortune_oil_pack",
    "rice.jpg": "india_gate_rice_pack",
    "toor_dal.jpg": "tata_toor_dal_pack",
    "masala.jpg": "everest_masala_pack",
    "milk.jpg": "amul_milk_pack",
    "paneer.jpg": "amul_paneer_pack",
    "curd.jpg": "mother_dairy_dahi",
    "butter.jpg": "amul_butter_pack",
    "agarbatti.jpg": "mangaldeep_agarbatti",
    "matka.jpg": "desi_clay_matka",
    "kulhad.jpg": "desi_kulhad_set",
}

for dest_name, prefix in generated_mappings.items():
    matched = [f for f in os.listdir(brain_dir) if f.startswith(prefix) and f.endswith(".jpg")]
    if matched:
        src_path = os.path.join(brain_dir, matched[0])
        dest_path = os.path.join("media/products", dest_name)
        img = Image.open(src_path).convert("RGB")
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        img = img.resize((700, 700), Image.Resampling.LANCZOS)
        img.save(dest_path, "JPEG", quality=92)
        print(f"Processed generated image for {dest_name} from {matched[0]}")

# 2. Download and process high-res authentic photos for the rest
photo_urls = {
    "tomatoes.jpg": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=85",
    "capsicum.jpg": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=800&q=85",
    "palak.jpg": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=800&q=85",
    "apples.jpg": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=85",
    "bananas.jpg": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=800&q=85",
    "diya.jpg": "https://images.unsplash.com/photo-1605371924599-2d0365da1ae0?auto=format&fit=crop&w=800&q=85",
    "puja_thali.jpg": "https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=800&q=85",
    "kurti.jpg": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=85",
    "mens_kurta.jpg": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=800&q=85",
    "kadhai.jpg": "https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&w=800&q=85",
    "charger.jpg": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=85",
    "earbuds.jpg": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=85",
    "noodles.jpg": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=85",
    "biscuits.jpg": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=800&q=85",
    "namkeen.jpg": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=85",
    "chai.jpg": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=85",
    "ghee.jpg": "https://images.unsplash.com/photo-1631451095765-2c91616fc9e6?auto=format&fit=crop&w=800&q=85",
    "onions.jpg": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&w=800&q=85",
    "potatoes.jpg": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=85",
    "soap.jpg": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?auto=format&fit=crop&w=800&q=85",
    "honey.jpg": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=85",
    "pressure_cooker.jpg": "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=85",
}

for dest_name, url in photo_urls.items():
    dest_path = os.path.join("media/products", dest_name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        img = img.resize((700, 700), Image.Resampling.LANCZOS)
        img.save(dest_path, "JPEG", quality=90)
        print(f"Downloaded and saved {dest_name} ({len(data)} bytes)")
    except Exception as e:
        print(f"Error fetching {dest_name}: {e}")

print("All images processed successfully!")
