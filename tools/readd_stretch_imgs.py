"""Re-add stretch images to all stretch actions that lost them."""
import json
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA_PATH = BASE / "data" / "exercise_options.json"

SHOPIFY = "https://cdn.shopify.com/s/files/1/1585/6091/files/"

STRETCH_IMGS = {
    "三角肌": SHOPIFY + "Cross_Arm_Shoulder_Stretch_480x480.png",
    "肩后束": SHOPIFY + "Cross_Arm_Shoulder_Stretch_480x480.png",
    "胸部拉伸": SHOPIFY + "Open_Book_Chest_Stretch_480x480.png",
    "门框拉胸": SHOPIFY + "Open_Book_Chest_Stretch_480x480.png",
    "猫牛": SHOPIFY + "Cat-Cow_480x480.png",
    "婴儿": SHOPIFY + "Child_s_Pose_480x480.png",
    "眼镜蛇": SHOPIFY + "Sphinx_Cobra_480x480.png",
    "背阔肌": SHOPIFY + "Seated_Spinal_Twist_480x480.png",
    "股四头": SHOPIFY + "Prone_Quad_Stretch_480x480.png",
    "臀部": SHOPIFY + "Pigeon_Stretch_837e284a-2010-4ec2-8290-5b1e9b1d4c4b_480x480.png",
    "小腿": SHOPIFY + "Standing_Wall_Calf_Stretch_480x480.png",
    "腘绳": SHOPIFY + "Seated_Forward_Fold_Hamstring_Stretch_480x480.png",
}

data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

added = 0
already = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        name = action.get("name", "")
        # Only process stretch actions (not warmup or main exercise)
        if not any(k in name for k in ["拉伸", "式"]):
            continue
        # Check if already has images
        if action.get("images") and len(action["images"]) > 0:
            already += 1
            continue
        # Find matching image
        for keyword, img_url in STRETCH_IMGS.items():
            if keyword in name:
                action["images"] = [{"src": img_url, "alt": name + "示范图"}]
                added += 1
                print(f"✅ Added: {name} -> {img_url.split('/')[-1][:45]}")
                break

DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n=== Summary ===")
print(f"Added images: {added}")
print(f"Already had images: {already}")

# Final count
total_stretch = 0
with_img = 0
for eid, opt in data.items():
    for action in opt.get("actions", []):
        name = action.get("name", "")
        if any(k in name for k in ["拉伸", "式"]):
            total_stretch += 1
            if action.get("images"):
                with_img += 1
print(f"Stretch actions with images: {with_img}/{total_stretch}")
