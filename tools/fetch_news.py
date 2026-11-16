"""Pull the latest GTA 6 headlines from public RSS feeds into data/news.json.
Run daily (GitHub Actions does this), then run build.py.  Usage: py -3 tools/fetch_news.py
Stores only headline, source, date and link. No article text: readers click through to the source."""
import email.utils, html, json, pathlib, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / "data" / "news.json"
KEEP_DAYS = 21
MAX_ITEMS = 60

# (source name, feed url). Publisher feeds first: they win over Google News duplicates.
FEEDS = [
    ("IGN", "https://feeds.ign.com/ign/games-all"),
    ("GameSpot", "https://www.gamespot.com/feeds/game-news"),
    ("Eurogamer", "https://www.eurogamer.net/feed"),
    ("PC Gamer", "https://www.pcgamer.com/rss/"),
    ("GamesRadar+", "https://www.gamesradar.com/rss/"),
    ("Google News", "https://news.google.com/rss/search?q=%22GTA+6%22+OR+%22GTA+VI%22+OR+%22Grand+Theft+Auto+VI%22+when:7d&hl=en-US&gl=US&ceid=US:en"),
]
GTA = re.compile(r"\bgta\s*(6|vi)\b|\bgrand theft auto\s*(6|vi)\b|\bgtavi\b", re.I)
ATOM = "{http://www.w3.org/2005/Atom}"
# Google News pulls from everywhere; only keep outlets with real editorial standards.
TRUSTED = {s.lower() for s in [
    "Rockstar Games", "Xbox Wire", "PlayStation Blog", "PlayStation.Blog", "IGN", "GameSpot", "Eurogamer", "Eurogamer.net",
    "PC Gamer", "GamesRadar+", "Polygon", "Polygon.com", "The Verge", "Kotaku", "Video Games Chronicle", "VGC", "Gematsu",
    "Push Square", "Pure Xbox", "Windows Central", "Digital Foundry", "Game Developer", "GamesIndustry.biz", "Engadget",
    "CNET", "Wired", "Bloomberg", "Bloomberg.com", "Reuters", "Associated Press", "AP News", "CNBC", "NBC News", "CBS News",
    "ABC News", "BBC", "The Guardian", "The New York Times", "The Washington Post", "USA Today", "Forbes", "Variety",
    "The Hollywood Reporter", "Rolling Stone", "Axios", "Business Insider", "Time", "TIME", "Yahoo Tech", "VICE",
    "Game Rant", "TheGamer", "Dexerto", "Destructoid", "Rock Paper Shotgun", "Shacknews", "Tom's Guide", "TechRadar",
]}
UA = {"User-Agent": "Mozilla/5.0 (compatible; calluncgta-news/1.0; +https://gta.callunc.com/news/)"}


def clean(t):
    return re.sub(r"\s+", " ", html.unescape(t or "")).strip()


def key(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())[:70]


def parse_date(raw):
    if not raw:
        return None
    try:
        d = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def read_feed(name, url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        title, link = clean(it.findtext("title")), clean(it.findtext("link"))
        source = name
        if name == "Google News":
            src = it.find("source")
            source = clean(src.text) if src is not None and src.text else "Google News"
            if source and title.endswith(" - " + source):
                title = title[: -len(source) - 3].strip()
        out.append((title, link, source, parse_date(it.findtext("pubDate"))))
    for it in root.iter(ATOM + "entry"):
        ln = it.find(ATOM + "link")
        out.append((clean(it.findtext(ATOM + "title")), ln.get("href", "") if ln is not None else "", name,
                    parse_date(it.findtext(ATOM + "updated") or it.findtext(ATOM + "published"))))
    return out


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=KEEP_DAYS)
    items, seen, errors = [], set(), []
    for name, url in FEEDS:
        try:
            rows = read_feed(name, url)
        except Exception as ex:  # one dead feed must not stop the others
            errors.append(f"{name}: {type(ex).__name__}")
            continue
        for title, link, source, when in rows:
            if not title or not link.startswith("https://") or not GTA.search(title):
                continue
            if when is None or when < cutoff or when > now + timedelta(hours=2):
                continue
            if name == "Google News" and source.lower() not in TRUSTED:
                continue
            k = key(title)
            if k in seen:
                continue
            seen.add(k)
            items.append({"title": title, "url": link, "source": source, "date": when.strftime("%Y-%m-%dT%H:%M:%SZ")})

    old = []
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8")).get("items", [])
        except ValueError:
            old = []
    for o in old:  # keep earlier headlines that have dropped out of the feeds
        if key(o["title"]) not in seen and parse_date(o["date"]) and parse_date(o["date"]) >= cutoff:
            seen.add(key(o["title"]))
            items.append(o)

    items.sort(key=lambda o: o["date"], reverse=True)
    items = items[:MAX_ITEMS]
    if not items and old:
        print("No headlines fetched; keeping the old file.", errors)
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"{len(items)} headlines saved", ("| feed errors: " + ", ".join(errors)) if errors else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
