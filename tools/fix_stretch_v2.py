"""Extract stretch exercise images from multiple verified sources.
Fallback: remove broken/SVG images if no real image found."""
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

def fetch_html(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None

def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = resp.headers.get("Content-Type", "")
            return 200 <= resp.status < 400 and ("image" in ctype or "octet" in ctype)
    except:
        return False

def extract_images(html, source_domain=None):
    """Extract image URLs from HTML, filter for likely exercise images."""
    urls = set()
    # All img src
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            if source_domain:
                u = "https://" + source_domain + u
        # Filter: must be image file, not icon/logo/spacer
        if re.search(r'\.(jpg|jpeg|png|gif|webp)(\?|$)', u, re.I):
            if not re.search(r'(logo|icon|spacer|pixel|avatar|banner|ad-|placeholder)', u, re.I):
                urls.add(u)
    # og:image
    for m in re.finditer(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        if re.search(r'\.(jpg|jpeg|png|gif|webp)', u, re.I):
            urls.add(u)
    return urls

# Sources to scrape: (url, domain_for_relative)
sources = [
    ("https://stretchingworkout.com/exercises/", "stretchingworkout.com"),
    ("https://habitnest.com/pages/stretching-day-12", "habitnest.com"),
    ("https://habitnest.com/pages/stretching-day-1", "habitnest.com"),
    ("https://www.themanual.com/fitness/full-body-stretching-routine/", "www.themanual.com"),
]

print("=== Scraping stretch image sources ===\n")
all_candidates = []
for url, domain in sources:
    print(f"Source: {url}")
    html = fetch_html(url)
    if not html:
        print(f"  ⚠️ Fetch failed")
        continue
    imgs = extract_images(html, domain)
    print(f"  Found {len(imgs)} candidate images")
    for u in sorted(imgs):
        if check_url(u):
            all_candidates.append(u)
            print(f"    ✅ {u[:90]}")

print(f"\nTotal verified candidate images: {len(all_candidates)}")

# Now try to find specific stretch exercise pages on stretchingworkout.com
print("\n=== Searching specific stretch pages ===\n")
specific_stretches = [
    ("standing-quad-stretch", "quad-stretch"),
    ("quad-stretch", "quad-stretch"),
    ("calf-stretch", "calf-stretch"),
    ("hamstring-stretch", "hamstring-stretch"),
    ("glute-stretch", "glute-stretch"),
    ("shoulder-stretch", "shoulder-deltoid"),
    ("cross-body-shoulder-stretch", "shoulder-deltoid"),
    ("chest-stretch", "chest-doorway"),
    ("doorway-chest-stretch", "chest-doorway"),
    ("cobra-stretch", "cobra"),
    ("childs-pose", "child-pose"),
    ("child-pose", "child-pose"),
    ("cat-cow", "cat-cow"),
    ("cat-cow-stretch", "cat-cow"),
    ("lat-stretch", "lat-stretch"),
    ("latissimus-dorsi-stretch", "lat-stretch"),
    ("rear-delt-stretch", "rear-delt"),
]

stretch_images = {}
domains_to_try = [
    "https://stretchingworkout.com/exercises/{slug}/",
    "https://stretchingworkout.com/{slug}/",
    "https://habitnest.com/pages/{slug}",
]

for slug, key in specific_stretches:
    if key in stretch_images:
        continue
    for template in domains_to_try:
        url = template.format(slug=slug)
        html = fetch_html(url)
        if not html:
            continue
        imgs = extract_images(html, url.split("/")[2])
        for u in sorted(imgs):
            if check_url(u):
                stretch_images[key] = u
                print(f"✅ [{key}] {u[:80]}")
                break
        if key in stretch_images:
            break

print(f"\n=== Found {len(stretch_images)} specific stretch images ===\n")

# Update data
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# Map SVG filenames to found images
svg_map = {}
for key, img_url in stretch_images.items():
    svg_map[key + ".svg"] = img_url

# Also map by action name keyword
name_keyword_map = {
    "三角肌": "shoulder-deltoid",
    "肩后束": "rear-delt",
    "胸部拉伸": "chest-doorway",
    "门框拉胸": "chest-doorway",
    "猫牛": "cat-cow",
    "婴儿": "child-pose",
    "眼镜蛇": "cobra",
    "背阔肌": "lat-stretch",
    "股四头": "quad-stretch",
    "臀部": "glute-stretch",
    "小腿": "calf-stretch",
    "腘绳": "hamstring-stretch",
}

replaced = 0
removed = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        new_images = []
        for img in action.get("images", []):
            src = img.get("src", "")
            # Replace SVG
            replaced_flag = False
            for svg_name, img_url in svg_map.items():
                if svg_name in src:
                    img["src"] = img_url
                    new_images.append(img)
                    replaced += 1
                    replaced_flag = True
                    break
            if replaced_flag:
                continue
            # Replace workoutlabs logo
            if "og-workoutlabs" in src:
                action_name = action.get("name", "")
                for keyword, key in name_keyword_map.items():
                    if keyword in action_name and key in stretch_images:
                        img["src"] = stretch_images[key]
                        new_images.append(img)
                        replaced += 1
                        replaced_flag = True
                        break
                if replaced_flag:
                    continue
                # Remove if no match
                removed += 1
                continue
            # Keep other images
            new_images.append(img)
        action["images"] = new_images

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"=== Results ===")
print(f"Replaced: {replaced}")
print(f"Removed (unfixable): {removed}")
print(f"Saved to {DATA_PATH}")

# Final check
print("\n=== Remaining stretch image sources ===")
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            if src.endswith(".svg") or "og-workoutlabs" in src:
                print(f"  ❌ STILL BAD: {action['name']}: {src[:70]}")
print("(no output above = all stretch images are clean)")
