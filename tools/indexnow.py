"""Tell Bing (and other IndexNow engines) about every page on the site.
Run after each push:  py -3 tools/indexnow.py
Reads docs/urls.txt (written by build.py) and the key from build.py."""
import json, pathlib, re, urllib.request
from urllib.parse import urlparse

site = pathlib.Path(__file__).resolve().parent.parent
src = (site / "build.py").read_text(encoding="utf-8")
key = re.search(r'INDEXNOW_KEY = "([0-9a-f]+)"', src).group(1)
base = re.search(r'BASE_URL = "([^"]+)"', src).group(1)
urls = [u for u in (site / "docs" / "urls.txt").read_text(encoding="utf-8").split() if u]
body = {"host": urlparse(base).netloc, "key": key, "keyLocation": f"{base}{key}.txt", "urlList": urls}
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow:", r.status, f"({len(urls)} urls)")
except urllib.error.HTTPError as err:
    print("IndexNow error:", err.code, err.read().decode()[:200])
