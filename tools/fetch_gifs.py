"""Fetch stable GIF URLs from Giphy public API and update exercise_options.json.
Replaces broken doubaocdn links and local SVG stretch placeholders."""
import json
import urllib.request
import urllib.parse
import time
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"
GIPHY_KEY = "dc6zaTOxFJmzC"  # Giphy public beta key

def giphy_search(query, limit=3):
    """Search Giphy and return list of original GIF URLs."""
    encoded = urllib.parse.quote(query)
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_KEY}&q={encoded}&limit={limit}&rating=g"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            results = []
            for item in data.get("data", []):
                img = item.get("images", {})
                # Prefer downsized (smaller, faster load), fallback original
                for key in ["downsized", "downsized_medium", "original"]:
                    if key in img and img[key].get("url"):
                        results.append(img[key]["url"])
                        break
            return results
    except Exception as e:
        print(f"  Giphy search failed for '{query}': {e}")
        return []

def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except:
        return False

# Search queries for each needed image
searches = {
    # Main exercises (replacing broken doubaocdn links)
    "shoulder_stage_1_main": "kneeling pike push up shoulder",
    "chest_stage_2_main": "standard push up correct form",
    # Stretches (replacing local SVG placeholders)
    "shoulder-deltoid": "cross body shoulder stretch",
    "rear-delt": "rear delt stretch shoulder",
    "chest-doorway": "doorway chest stretch",
    "cat-cow": "cat cow yoga stretch",
    "child-pose": "child pose yoga stretch",
    "cobra": "cobra pose yoga stretch",
    "lat-stretch": "lat stretch back",
    "quad-stretch": "standing quad stretch thigh",
    "glute-stretch": "glute stretch hip",
    "calf-stretch": "calf stretch wall",
    "hamstring-stretch": "hamstring stretch seated",
}

print("=== Searching Giphy for stable GIF URLs ===\n")
gif_urls = {}
for key, query in searches.items():
    print(f"[{key}] searching: '{query}'")
    urls = giphy_search(query, limit=3)
    # Verify each URL is accessible
    valid = []
    for u in urls:
        if check_url(u):
            valid.append(u)
            print(f"  ✅ {u[:80]}")
        else:
            print(f"  ❌ (inaccessible) {u[:80]}")
    if valid:
        gif_urls[key] = valid[0]
    else:
        print(f"  ⚠️ No valid URL found for {key}")
    time.sleep(0.3)  # Rate limit courtesy

print(f"\n=== Found {len(gif_urls)}/{len(searches)} valid GIFs ===\n")

# Now update exercise_options.json
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# 1. Fix main exercise images
if "shoulder_stage_1_main" in gif_urls:
    data["shoulder_stage_1"]["image"] = gif_urls["shoulder_stage_1_main"]
    print(f"✅ Updated shoulder_stage_1 main image")

if "chest_stage_2_main" in gif_urls:
    data["chest_stage_2"]["image"] = gif_urls["chest_stage_2_main"]
    print(f"✅ Updated chest_stage_2 main image")

# 2. Replace stretch SVG references in all exercises
stretch_map = {
    "shoulder-deltoid.svg": gif_urls.get("shoulder-deltoid"),
    "rear-delt.svg": gif_urls.get("rear-delt"),
    "chest-doorway.svg": gif_urls.get("chest-doorway"),
    "cat-cow.svg": gif_urls.get("cat-cow"),
    "child-pose.svg": gif_urls.get("child-pose"),
    "cobra.svg": gif_urls.get("cobra"),
    "lat-stretch.svg": gif_urls.get("lat-stretch"),
    "quad-stretch.svg": gif_urls.get("quad-stretch"),
    "glute-stretch.svg": gif_urls.get("glute-stretch"),
    "calf-stretch.svg": gif_urls.get("calf-stretch"),
    "hamstring-stretch.svg": gif_urls.get("hamstring-stretch"),
}

replaced = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            for svg_name, gif_url in stretch_map.items():
                if svg_name in src and gif_url:
                    old = img["src"]
                    img["src"] = gif_url
                    replaced += 1
                    print(f"  Replaced: {old.split('/')[-1]} -> GIF")

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n=== Done: {replaced} stretch images replaced, 2 main images fixed ===")
print(f"File saved: {DATA_PATH}")
