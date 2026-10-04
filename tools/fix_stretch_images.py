"""Extract real stretch GIFs from self.com and other verified sources,
then replace all SVG placeholders and workoutlabs logo images."""
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

def fetch_html(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Fetch failed: {e}")
        return ""

def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except:
        return False

def extract_media_urls(html):
    """Extract all media.self.com and giphy image URLs from HTML."""
    urls = set()
    # media.self.com photos
    for m in re.finditer(r'(https://media\.self\.com/photos/[^"\'\s]+\.(?:gif|jpg|jpeg|png))', html, re.I):
        urls.add(m.group(1))
    # giphy
    for m in re.finditer(r'(https://media\d*\.giphy\.com/media/[^"\'\s]+\.(?:gif|webp))', html, re.I):
        urls.add(m.group(1))
    return urls

# Pages to scrape for stretch GIFs
pages = [
    "https://www.self.com/story/best-stretches",
    "https://www.self.com/gallery/best-stretches-for-soreness",
    "https://www.self.com/story/post-workout-stretches",
    "https://www.self.com/gallery/stretches-for-flexibility",
]

print("=== Scraping self.com for stretch GIFs ===\n")
all_gifs = []
for url in pages:
    print(f"Scraping: {url}")
    html = fetch_html(url)
    if not html:
        print(f"  ⚠️ No content")
        continue
    found = extract_media_urls(html)
    print(f"  Found {len(found)} image URLs")
    # Verify each
    for u in found:
        if check_url(u):
            all_gifs.append(u)
            print(f"    ✅ {u.split('/')[-1][:60]}")

print(f"\nTotal verified GIFs: {len(all_gifs)}")

# Now we need to map GIFs to specific stretch actions.
# Since we can't easily identify which GIF is which, we'll use a keyword-based approach
# by scraping specific exercise pages.

# Scrape specific stretch pages for targeted images
specific_pages = {
    "quad-stretch": ["https://www.self.com/story/standing-quad-stretch", "https://www.self.com/gallery/quad-stretches"],
    "calf-stretch": ["https://www.self.com/story/calf-stretch", "https://www.self.com/gallery/calf-stretches"],
    "hamstring-stretch": ["https://www.self.com/story/hamstring-stretch", "https://www.self.com/gallery/hamstring-stretches"],
    "glute-stretch": ["https://www.self.com/story/glute-stretch", "https://www.self.com/gallery/glute-stretches"],
    "shoulder-deltoid": ["https://www.self.com/story/shoulder-stretch", "https://www.self.com/gallery/shoulder-stretches"],
    "chest-doorway": ["https://www.self.com/story/chest-stretch", "https://www.self.com/gallery/chest-stretches"],
    "cobra": ["https://www.self.com/story/cobra-pose", "https://www.self.com/gallery/yoga-stretches"],
    "child-pose": ["https://www.self.com/story/child-pose", "https://www.self.com/gallery/yoga-stretches"],
    "cat-cow": ["https://www.self.com/story/cat-cow-stretch", "https://www.self.com/gallery/yoga-stretches"],
    "lat-stretch": ["https://www.self.com/story/lat-stretch", "https://www.self.com/gallery/back-stretches"],
    "rear-delt": ["https://www.self.com/story/rear-delt-stretch", "https://www.self.com/gallery/shoulder-stretches"],
}

print("\n=== Scraping specific stretch pages ===\n")
stretch_images = {}
for key, urls in specific_pages.items():
    for url in urls:
        print(f"[{key}] {url}")
        html = fetch_html(url)
        if not html:
            continue
        found = extract_media_urls(html)
        for u in found:
            if check_url(u):
                if key not in stretch_images:
                    stretch_images[key] = u
                    print(f"  ✅ {u.split('/')[-1][:60]}")
                    break
        if key in stretch_images:
            break
    if key not in stretch_images:
        print(f"  ⚠️ No image found for {key}")

print(f"\n=== Found {len(stretch_images)}/{len(specific_pages)} stretch images ===\n")

# Update exercise_options.json
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# Replace ALL stretch images (both SVG and workoutlabs logo) with real images
print("=== Replacing all stretch images ===")
stretch_map = {}
for key, img_url in stretch_images.items():
    stretch_map[key + ".svg"] = img_url

# Also replace workoutlabs logo references
workoutlabs_logo = "og-workoutlabs-main"
replaced = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            # Replace SVG
            for svg_name, img_url in stretch_map.items():
                if svg_name in src:
                    img["src"] = img_url
                    replaced += 1
                    break
            # Replace workoutlabs logo
            if workoutlabs_logo in src:
                # Find matching stretch by action name
                action_name = action.get("name", "")
                for key, img_url in stretch_images.items():
                    key_display = key.replace("-", "")
                    if any(k in action_name for k in [key, key.replace("-", ""), key.replace("-", " ")]):
                        img["src"] = img_url
                        replaced += 1
                        break
                else:
                    # Default to shoulder stretch image
                    if "shoulder-deltoid" in stretch_images:
                        img["src"] = stretch_images["shoulder-deltoid"]
                        replaced += 1

print(f"✅ Replaced {replaced} stretch images")

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n=== Saved ===")

# Final verification: list all stretch image sources
print("\n=== Final stretch image sources ===")
seen = set()
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            if src not in seen:
                seen.add(src)
                is_svg = src.endswith(".svg")
                is_logo = "og-workoutlabs" in src
                mark = "❌ SVG" if is_svg else ("❌ LOGO" if is_logo else "✅")
                print(f"  {mark} {action['name']}: {src[:80]}")
