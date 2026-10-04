"""Final fix: use verified habitnest/shopify CDN images for all stretches.
Maps specific stretch images by filename, removes any remaining SVG/bad images."""
import json
import urllib.request
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

SHOPIFY_BASE = "https://cdn.shopify.com/s/files/1/1585/6091/files/"

# Verified image filenames from habitnest.com (all checked accessible)
STRETCH_IMAGES = {
    "shoulder-deltoid": SHOPIFY_BASE + "Cross_Arm_Shoulder_Stretch_480x480.png",
    "rear-delt": SHOPIFY_BASE + "Cross_Arm_Shoulder_Stretch_480x480.png",
    "chest-doorway": SHOPIFY_BASE + "Open_Book_Chest_Stretch_480x480.png",
    "cat-cow": SHOPIFY_BASE + "Cat-Cow_480x480.png",
    "child-pose": SHOPIFY_BASE + "Child_s_Pose_480x480.png",
    "cobra": SHOPIFY_BASE + "Sphinx_Cobra_480x480.png",
    "lat-stretch": SHOPIFY_BASE + "Seated_Spinal_Twist_480x480.png",  # closest available back stretch
    "quad-stretch": SHOPIFY_BASE + "Prone_Quad_Stretch_480x480.png",
    "glute-stretch": SHOPIFY_BASE + "Pigeon_Stretch_837e284a-2010-4ec2-8290-5b1e9b1d4c4b_480x480.png",
    "calf-stretch": SHOPIFY_BASE + "Standing_Wall_Calf_Stretch_480x480.png",
    "hamstring-stretch": SHOPIFY_BASE + "Seated_Forward_Fold_Hamstring_Stretch_480x480.png",
}

def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except:
        return False

# Verify all URLs first
print("=== Verifying stretch image URLs ===\n")
valid_images = {}
for key, url in STRETCH_IMAGES.items():
    ok = check_url(url)
    mark = "✅" if ok else "❌"
    print(f"{mark} [{key}] {url.split('/')[-1][:50]}")
    if ok:
        valid_images[key] = url

print(f"\nValid: {len(valid_images)}/{len(STRETCH_IMAGES)}")

# Map action name keywords to image keys
NAME_TO_KEY = {
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

# SVG filename to key mapping
SVG_TO_KEY = {
    "shoulder-deltoid.svg": "shoulder-deltoid",
    "rear-delt.svg": "rear-delt",
    "chest-doorway.svg": "chest-doorway",
    "cat-cow.svg": "cat-cow",
    "child-pose.svg": "child-pose",
    "cobra.svg": "cobra",
    "lat-stretch.svg": "lat-stretch",
    "quad-stretch.svg": "quad-stretch",
    "glute-stretch.svg": "glute-stretch",
    "calf-stretch.svg": "calf-stretch",
    "hamstring-stretch.svg": "hamstring-stretch",
}

# Update data
data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

replaced = 0
removed = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        new_images = []
        for img in action.get("images", []):
            src = img.get("src", "")
            target_key = None

            # Check SVG filename
            for svg_name, key in SVG_TO_KEY.items():
                if svg_name in src:
                    target_key = key
                    break

            # Check by action name if no SVG match
            if not target_key:
                action_name = action.get("name", "")
                for keyword, key in NAME_TO_KEY.items():
                    if keyword in action_name:
                        target_key = key
                        break

            # Replace if we have a valid image
            if target_key and target_key in valid_images:
                img["src"] = valid_images[target_key]
                new_images.append(img)
                replaced += 1
            elif src.endswith(".svg") or "og-workoutlabs" in src:
                # Remove bad images that can't be fixed
                removed += 1
            else:
                # Keep other valid images
                new_images.append(img)

        action["images"] = new_images

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n=== Results ===")
print(f"Replaced with real images: {replaced}")
print(f"Removed (unfixable): {removed}")
print(f"Saved to {DATA_PATH}")

# Final verification
print("\n=== Final stretch image check ===")
bad_count = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            src = img.get("src", "")
            if src.endswith(".svg") or "og-workoutlabs" in src or "doubaocdn" in src:
                print(f"  ❌ BAD: {action['name']}: {src[:70]}")
                bad_count += 1
if bad_count == 0:
    print("  ✅ ALL CLEAN - no SVG, logo, or broken doubaocdn images remain")
