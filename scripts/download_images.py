import os
import requests
import time
from db import get_db

# Constants
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "PixelPastMuseumApp/1.0 (contact@pixelpast.com)" # Reliable User-Agent is required by Wikimedia

def download_museum_images():
    db = get_db()
    museums = list(db.museums.find({}))
    
    print(f"Found {len(museums)} museums. Starting download process via Wikimedia API...")
    
    # Base directory for static uploads
    base_upload_path = os.path.join("static", "uploads", "museums")
    if not os.path.exists(base_upload_path):
        os.makedirs(base_upload_path)

    for index, museum in enumerate(museums):
        museum_name = museum.get("museum_name", "Unknown")
        city = museum.get("city", "")
        m_id = str(museum["_id"])
        
        print(f"[{index+1}/{len(museums)}] Processing: {museum_name}...")
        
        # Create folder for this museum
        save_dir = os.path.join(base_upload_path, m_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Check if we already have images
        existing_files = [f for f in os.listdir(save_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if len(existing_files) >= 5: # Reduced threshold for Wiki as results might be fewer
            print(f"   -> Skipping. Already has {len(existing_files)} images.")
            update_db_paths(db, museum["_id"], m_id, existing_files)
            continue
            
        # Search Query
        search_query = f"{museum_name} {city}"
        
        # Fetch Image URLs from Wikimedia
        image_urls = search_wikimedia_images(search_query, limit=15)
        
        if not image_urls:
            # Fallback: Try just museum name without city
            image_urls = search_wikimedia_images(museum_name, limit=15)
            
        print(f"   -> Found {len(image_urls)} images on Wikimedia.")
        
        # Download images
        download_count = 0
        for i, url in enumerate(image_urls):
            try:
                # Extension
                ext = url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    continue
                    
                filename = f"wiki_{i}.{ext}"
                file_path = os.path.join(save_dir, filename)
                
                # Check if file exists (redundant check but safe)
                if os.path.exists(file_path):
                    download_count += 1
                    continue
                
                # Download
                headers = {'User-Agent': USER_AGENT}
                img_data = requests.get(url, headers=headers, timeout=10).content
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                    
                download_count += 1
                
                # Be nice to the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"      X Failed to download {url}: {e}")
                
        # Final update
        all_files = [f for f in os.listdir(save_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if all_files:
            update_db_paths(db, museum["_id"], m_id, all_files)
        else:
            print("   -> No images available to link.")

def search_wikimedia_images(query, limit=10):
    """
    Searches Wikimedia Commons for images.
    """
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": "6", # Namespace 6 is File:
        "gsrsearch": query,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|mime",
    }
    
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(WIKIMEDIA_API_URL, params=params, headers=headers, timeout=10)
        data = response.json()
        
        image_urls = []
        if "query" in data and "pages" in data["query"]:
            for page_id, page_info in data["query"]["pages"].items():
                if "imageinfo" in page_info:
                    for info in page_info["imageinfo"]:
                        if info["mime"] in ["image/jpeg", "image/png"]:
                            image_urls.append(info["url"])
                            
        return image_urls
        
    except Exception as e:
        print(f"   Error querying Wikimedia: {e}")
        return []

def update_db_paths(db, raw_id, folder_name, files):
    if not files:
        return

    files.sort()
    web_paths = [f"uploads/museums/{folder_name}/{f}" for f in files]
    
    cover_image = web_paths[0]
    
    db.museums.update_one(
        {"_id": raw_id},
        {
            "$set": {
                "cover_image": cover_image,
                "gallery_images": web_paths
            }
        }
    )

if __name__ == "__main__":
    download_museum_images()
