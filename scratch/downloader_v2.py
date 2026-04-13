import os
import requests

downloads = {
    "masala_dosa.jpg": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?q=80&w=1000&auto=format&fit=crop",
    "veg_biryani.jpg": "https://images.unsplash.com/photo-1589302168068-964664d93dc9?q=80&w=1000&auto=format&fit=crop",
    "butter_chicken.jpg": "https://images.unsplash.com/photo-1603894584104-748956894c50?q=80&w=1000&auto=format&fit=crop",
    "garlic_naan.jpg": "https://images.unsplash.com/photo-1533777464539-e339d802e008?q=80&w=1000&auto=format&fit=crop",
    "palak_paneer.jpg": "https://images.unsplash.com/photo-1617692855027-33b14f061079?q=80&w=1000&auto=format&fit=crop",
    "rogan_josh.jpg": "https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?q=80&w=1000&auto=format&fit=crop",
    "dosa_premium.jpg": "https://images.unsplash.com/photo-1668236543090-bc2bf318f0ac?q=80&w=1000&auto=format&fit=crop"
}

base_dir = os.path.join("frontend", "static", "img", "food")
os.makedirs(base_dir, exist_ok=True)

for name, url in downloads.items():
    print(f"Retrying download: {name}...")
    try:
        r = requests.get(url, stream=True, timeout=15)
        if r.status_code == 200:
            with open(os.path.join(base_dir, name), "wb") as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)
            print(f"Successfully saved {name}")
        else:
            print(f"Still failing {name}: Status {r.status_code}")
    except Exception as e:
        print(f"Error {name}: {e}")
