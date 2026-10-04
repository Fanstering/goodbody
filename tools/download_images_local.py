"""Download all foreign CDN images to local static/images/ directory,
then replace URLs with local paths. This solves domestic accessibility completely."""
import json
import os
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"
IMG_DIR = BASE / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Domestic CDNs that don't need downloading
DOMESTIC_DOMAINS = [
    "keepcdn.com", "gotokeep.com", "calorietech.com",
    "bilibili.com", "hdslb.com", "zhimg.com", "sinaimg.cn",
    "douyin.com", "iesdouyin.com", "baidu.com", "bdstatic.com",
]

def is_domestic(url):
    try:
        domain = urlparse(url).netloc.lower()
        return any(d in domain for d in DOMESTIC_DOMAINS)
    except:
        return False

def sanitize_filename(url, index):
    """Create a safe local filename from URL."""
    # Get extension from URL or content-type
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        ext = '.jpg'  # default
    # Create a short name based on URL hash
    import hashlib
    h = hashlib.md5(url.encode()).hexdigest()[:12]
    return f"img_{index}_{h}{ext}"

def download_image(url, filepath, timeout=15):
    """Download image with proper headers."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            # Detect actual content type
            ct = resp.headers.get('Content-Type', '').lower()
            if 'gif' in ct and not filepath.endswith('.gif'):
                filepath = filepath.rsplit('.', 1)[0] + '.gif'
            elif 'png' in ct and not filepath.endswith('.png'):
                filepath = filepath.rsplit('.', 1)[0] + '.png'
            elif ('jpeg' in ct or 'jpg' in ct) and not filepath.endswith(('.jpg', '.jpeg')):
                filepath = filepath.rsplit('.', 1)[0] + '.jpg'
            elif 'webp' in ct and not filepath.endswith('.webp'):
                filepath = filepath.rsplit('.', 1)[0] + '.webp'

            with open(filepath, 'wb') as f:
                f.write(data)
            return len(data), filepath
    except Exception as e:
        print(f"    ❌ Download failed: {e}")
        return 0, filepath

data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# Collect all unique image URLs that need downloading
all_urls = {}
url_index = 0

def collect_url(url, context):
    global url_index
    if not url or url.startswith('/static/') or url.startswith('data:'):
        return
    if is_domestic(url):
        return
    if url not in all_urls:
        url_index += 1
        all_urls[url] = {"index": url_index, "contexts": [context]}
    else:
        all_urls[url]["contexts"].append(context)

# Collect main exercise images
for eid, opt in data.items():
    collect_url(opt.get("image", ""), f"main:{eid}")
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            collect_url(img.get("src", ""), f"action:{action['name']}")

print(f"=== Found {len(all_urls)} unique foreign images to download ===\n")

# Download each image
url_to_local = {}
success = 0
failed = 0

for url, info in all_urls.items():
    idx = info["index"]
    filename = sanitize_filename(url, idx)
    filepath = IMG_DIR / filename
    print(f"[{idx}/{len(all_urls)}] Downloading...")
    print(f"  URL: {url[:90]}")
    print(f"  Contexts: {', '.join(info['contexts'][:3])}")

    size, actual_path = download_image(url, str(filepath))
    if size > 0:
        actual_filename = os.path.basename(actual_path)
        local_path = f"/static/images/{actual_filename}"
        url_to_local[url] = local_path
        success += 1
        print(f"  ✅ Saved: {actual_filename} ({size//1024}KB)")
    else:
        failed += 1
        print(f"  ❌ FAILED")

print(f"\n=== Download complete: {success} success, {failed} failed ===")

# Replace URLs in JSON with local paths
replaced = 0
for eid, opt in data.items():
    if opt.get("image") in url_to_local:
        opt["image"] = url_to_local[opt["image"]]
        replaced += 1
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            if img.get("src") in url_to_local:
                img["src"] = url_to_local[img["src"]]
                replaced += 1

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"=== Replaced {replaced} image URLs with local paths ===")
print(f"=== Saved to {DATA_PATH} ===")

# List downloaded files
print(f"\n=== Downloaded files in {IMG_DIR} ===")
for f in sorted(IMG_DIR.iterdir()):
    if f.is_file():
        print(f"  {f.name} ({f.stat().st_size//1024}KB)")
