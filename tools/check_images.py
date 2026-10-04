"""Check all image URLs in exercise_options.json for accessibility."""
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
DATA = json.loads((BASE / "data" / "exercise_options.json").read_text(encoding="utf-8"))

def check_url(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.headers.get("Content-Type", "?")
    except Exception as e:
        return f"ERR: {type(e).__name__}", str(e)[:80]

# Collect all unique image URLs
urls = set()
for eid, opt in DATA.items():
    if opt.get("image"):
        urls.add(opt["image"])
    for img in opt.get("images", []):
        if img.get("src") and not img["src"].startswith("/static/"):
            urls.add(img["src"])
    for action in opt.get("actions", []):
        for img in action.get("images", []):
            if img.get("src") and not img["src"].startswith("/static/"):
                urls.add(img["src"])

print(f"Checking {len(urls)} unique external image URLs...\n")
results = []
for url in sorted(urls):
    status, ctype = check_url(url)
    ok = isinstance(status, int) and 200 <= status < 400
    results.append((ok, url, status, ctype))
    mark = "✅" if ok else "❌"
    print(f"{mark} [{status}] {url[:90]}")

print(f"\n--- Summary ---")
print(f"OK: {sum(1 for r in results if r[0])}")
print(f"FAIL: {sum(1 for r in results if not r[0])}")
print("\nFailed URLs:")
for ok, url, status, ctype in results:
    if not ok:
        print(f"  [{status}] {url}")
