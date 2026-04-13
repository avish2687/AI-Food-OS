import os
import requests

downloads = {
    "masala_dosa.jpg": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?q=80&w=600&auto=format&fit=crop",
    "punjabi_samosa.jpg": "https://images.unsplash.com/photo-1601050690597-df0568f70950?q=80&w=600&auto=format&fit=crop",
    "quinoa_salad.jpg": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
    "grilled_chicken.jpg": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?w=800",
    "chicken_tikka.jpg": "https://images.unsplash.com/photo-1599481238640-4c1288750d7a?w=800",
    "tandoori_platter.jpg": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800",
    "dosa_premium.jpg": "https://images.unsplash.com/photo-1668236543090-bc2bf318f0ac?w=800",
    "veg_biryani.jpg": "https://images.unsplash.com/photo-1589302168068-964664d93dc9?w=800",
    "dal_makhani.jpg": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800",
    "butter_chicken.jpg": "https://images.unsplash.com/photo-1603894584104-748956894c50?w=800",
    "malai_kofta.jpg": "https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?w=800",
    "samosa_2pcs.jpg": "https://images.unsplash.com/photo-1601050638917-3f887b4e17d9?w=800",
    "rogan_josh.jpg": "https://images.unsplash.com/photo-1589193153578-3da07d004df1?w=800",
    "garlic_naan.jpg": "https://images.unsplash.com/photo-1533777464539-e339d802e008?w=800",
    "palak_paneer.jpg": "https://images.unsplash.com/photo-1619612844151-24bad858462a?w=800",
    "general_food.jpg": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800"
}

base_dir = os.path.join("frontend", "static", "img", "food")
os.makedirs(base_dir, exist_ok=True)

for name, url in downloads.items():
    print(f"Downloading {name}...")
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(os.path.join(base_dir, name), "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"Successfully saved {name}")
        else:
            print(f"Failed to download {name}: Status {r.status_code}")
    except Exception as e:
        print(f"Error downloading {name}: {e}")
