"""Replace all YouTube links with Bilibili search links,
and try to extract Keep exercise images as domestic CDN alternatives."""
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

def fetch_html(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        })
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

data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

# === Step 1: Replace all YouTube links with Bilibili search links ===
print("=== Replacing YouTube links with Bilibili search ===\n")
yt_count = 0

def to_bilibili_search(title):
    """Convert a video title to a Bilibili search URL."""
    encoded = urllib.parse.quote(title)
    return f"https://search.bilibili.com/all?keyword={encoded}"

import urllib.parse

for eid, opt in data.items():
    # Main video_links
    new_links = []
    for link in opt.get("video_links", []):
        url = link.get("url", "")
        if "youtube.com" in url or "youtu.be" in url:
            new_url = to_bilibili_search(link.get("title", opt.get("title", "健身动作")))
            new_links.append({"title": link["title"] + "（B站搜索）", "url": new_url})
            yt_count += 1
            print(f"  ✅ [{eid}] {link['title'][:30]} -> B站搜索")
        else:
            new_links.append(link)
    opt["video_links"] = new_links

    # Action-level video_links
    for action in opt.get("actions", []):
        new_action_links = []
        for link in action.get("video_links", []):
            url = link.get("url", "")
            if "youtube.com" in url or "youtu.be" in url:
                new_url = to_bilibili_search(link.get("title", action.get("name", "拉伸动作")))
                new_action_links.append({"title": link["title"] + "（B站搜索）", "url": new_url})
                yt_count += 1
            else:
                new_action_links.append(link)
        action["video_links"] = new_action_links

print(f"\nTotal YouTube links replaced: {yt_count}")

# === Step 2: Try to extract Keep images for main exercises ===
print("\n=== Extracting Keep exercise images ===\n")
keep_pages = {
    "abs_stage_1": "https://calorietech.com/exercises/55cc42d9fdac76af7fc278a9",  # 平板支撑
    "abs_stage_2": "https://www.calorietech.com/exercises/55cc42cc805a7ec3831d38cd",  # 西西里卷腹
    "abs_stage_3": "https://www.calorietech.com/exercises/57c01c9016d3eacd43d793b8",  # 俯身开合跳
    "chest_stage_1": "https://www.calorietech.com/exercises/62eb96d35361c100019d1c2a",  # 跪姿俯卧撑
}

keep_images = {}
for eid, url in keep_pages.items():
    print(f"[{eid}] fetching Keep page...")
    html = fetch_html(url)
    if not html:
        continue
    # Extract image URLs from HTML
    img_urls = set()
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        if re.search(r'\.(jpg|jpeg|png|gif|webp)', u, re.I):
            if not re.search(r'(logo|icon|spacer|avatar|banner)', u, re.I):
                img_urls.add(u)
    # Also check for background-image
    for m in re.finditer(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', html, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        if re.search(r'\.(jpg|jpeg|png|gif|webp)', u, re.I):
            img_urls.add(u)

    print(f"  Found {len(img_urls)} images")
    for u in sorted(img_urls)[:5]:
        if check_url(u):
            keep_images[eid] = u
            print(f"    ✅ {u[:90]}")
            break
        else:
            print(f"    ❌ (inaccessible) {u[:90]}")

print(f"\nKeep images found: {len(keep_images)}")

# Replace main exercise images with Keep images if found
for eid, img_url in keep_images.items():
    if eid in data:
        old = data[eid].get("image", "")
        data[eid]["image"] = img_url
        print(f"  ✅ Replaced {eid} main image with Keep CDN")

# === Step 3: For stretch images from shopify, add onerror fallback in frontend ===
# (We'll handle this via JS/CSS - if image fails, show a placeholder)
# For now, keep shopify images but also verify they're accessible
print("\n=== Verifying shopify stretch images ===")
shopify_bad = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            if "shopify.com" in img.get("src", ""):
                if not check_url(img["src"]):
                    shopify_bad += 1
                    print(f"  ❌ BAD: {action['name']}: {img['src'][:70]}")

print(f"Shopify images inaccessible: {shopify_bad}")

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n=== Saved to {DATA_PATH} ===")
print(f"Summary: {yt_count} YouTube links -> B站搜索, {len(keep_images)} Keep images extracted")
