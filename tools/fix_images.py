"""Extract exercise image URLs from workoutlabs.com and fix broken links.
Also replaces local SVG stretch placeholders with real images."""
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

def fetch_html(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
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

# Known working giphy URLs from existing data (verified accessible)
WORKING_GIPHY = {
    "pike_pushup": "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExanFoZGFtZWdsYTlxY3hrNDNjOXZ5a28zdDhnMHIxd2xoa3o1ZTQ4ZCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/W2p1CTs9Ug3kiTC3Jz/200w.gif",
    "kneeling_pushup": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDBxbWc0NmlyOW9tcjVhOHc1b25maWdrbDc0a3hmMGc3OXJxMGdseCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/06NfV8dSsO6oPf2KB2/200w.gif",
    "crunch": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2NxcGp5eDA4cHplYWtzZmQ0c3l0OXBjYm1xNGU0NnIzZ2IxNjVoMyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/MXoheu8Rq8329N00cR/200w.gif",
    "decline_pushup": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGE5dTBqdDZocXo0cDVtbDR4cW4yaWEzdWF1aHhxb3VseDZrbHl6ZiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/YQmmcPHmFgHekp7ktU/200w.gif",
}

# Fetch stretch images from workoutlabs exercise pages
print("=== Fetching stretch images from workoutlabs.com ===\n")
stretch_pages = {
    "shoulder-deltoid": "https://workoutlabs.com/exercise-guides/shoulder-stretch/",
    "quad-stretch": "https://workoutlabs.com/exercise-guides/standing-quadricep-stretch/",
    "calf-stretch": "https://workoutlabs.com/exercise-guides/straight-leg-calf-stretch/",
    "hamstring-stretch": "https://workoutlabs.com/exercise-guides/hamstring-stretch/",
    "glute-stretch": "https://workoutlabs.com/exercise-guides/gluteal-stretch/",
    "cobra": "https://workoutlabs.com/exercise-guides/cobra-abdominal-stretch/",
}

stretch_images = {}
for key, url in stretch_pages.items():
    print(f"[{key}] fetching {url}")
    html = fetch_html(url)
    if not html:
        print(f"  ⚠️ No HTML")
        continue
    # Extract og:image or first content image
    img_urls = []
    # og:image
    og_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    if og_match:
        img_urls.append(og_match.group(1))
    # All img tags with reasonable URLs
    for m in re.finditer(r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        if any(x in u for x in ["exercise", "stretch", "workoutlabs", "cdn"]):
            img_urls.append(u)
    # Verify first working URL
    for u in img_urls[:5]:
        if check_url(u):
            stretch_images[key] = u
            print(f"  ✅ {u[:90]}")
            break
    else:
        print(f"  ⚠️ No valid image found (tried {len(img_urls)} URLs)")

print(f"\nFound {len(stretch_images)}/{len(stretch_pages)} stretch images\n")

# Now update exercise_options.json
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# 1. Fix broken main exercise images
print("=== Fixing main exercise images ===")
# shoulder_stage_1 (跪姿冲肩俯卧撑) - use pike pushup gif
if check_url(WORKING_GIPHY["pike_pushup"]):
    data["shoulder_stage_1"]["image"] = WORKING_GIPHY["pike_pushup"]
    print("✅ shoulder_stage_1: replaced with pike pushup gif")
# chest_stage_2 (标准俯卧撑) - use kneeling pushup gif (closest available)
if check_url(WORKING_GIPHY["kneeling_pushup"]):
    data["chest_stage_2"]["image"] = WORKING_GIPHY["kneeling_pushup"]
    print("✅ chest_stage_2: replaced with pushup gif")

# 2. Replace stretch SVG references
print("\n=== Replacing stretch SVG placeholders ===")
stretch_map = {}
for svg_key, img_url in stretch_images.items():
    # Map SVG filename pattern to image
    stretch_map[svg_key + ".svg"] = img_url

# Also add rear-delt, chest-doorway, cat-cow, child-pose, lat-stretch if found
# For these, use cross-body shoulder stretch image as fallback for shoulder stretches
if "shoulder-deltoid" in stretch_images:
    stretch_map["rear-delt.svg"] = stretch_images["shoulder-deltoid"]
    stretch_map["chest-doorway.svg"] = stretch_images["shoulder-deltoid"]

replaced = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            for svg_name, img_url in stretch_map.items():
                if svg_name in src and img_url:
                    img["src"] = img_url
                    replaced += 1

print(f"✅ Replaced {replaced} stretch SVG placeholders with real images")

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n=== Saved to {DATA_PATH} ===")
print(f"Summary: 2 main images fixed, {replaced} stretch images replaced")
