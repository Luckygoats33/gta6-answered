"""Build GTA 6 Answered: static pages from ANSWERS below. Run: py -3 build.py"""
import json, html, pathlib, re

ROOT = pathlib.Path(__file__).parent / "docs"
SITE = "GTA 6 Answered"
BASE_URL = "https://luckygoats33.github.io/gta6-answered/"
CHECKED = "Nov 15, 2026"

R_TIMES = ("Rockstar Support: regional pre-load and release times",
           "https://support.rockstargames.com/articles/29jV3Cv2cCgvwM1XgtMO5o/grand-theft-auto-vi-regional-pre-load-and-release-times-on-playstation-5-and-xbox-series-x-or-s")
R_NEWS = ("Rockstar Newswire: pre-load begins on November 10",
          "https://www.rockstargames.com/newswire/article/k4ak9okk485712/grand-theft-auto-vi-pre-load-begins-on-november-10")
R_FAQ = ("Rockstar Support: pre-load FAQ",
         "https://support.rockstargames.com/articles/7nPqOA2uCbpEQHXx7KVrYd/grand-theft-auto-vi-pre-load-faq")
R_ED = ("Rockstar Support: platforms, editions and versions",
        "https://support.rockstargames.com/articles/4QfG4FmZCf5W1gS8jy4UVT/grand-theft-auto-vi-platform-editions-and-versions")

ANSWERS = [
    {
        "slug": "release-time",
        "short": "Midnight local, Nov 19",
        "q": "What time does GTA 6 come out?",
        "a": "Midnight, your local time, on November 19.",
        "detail": [
            "It's the same rule on PS5 and Xbox Series X|S, in every region.",
            "New Zealand reaches midnight first, so players there start about 19 hours before the US East Coast.",
        ],
        "sources": [R_TIMES],
    },
    {
        "slug": "pre-load",
        "short": "Yes, since Nov 10",
        "q": "Can I pre-load GTA 6?",
        "a": "Yes. Pre-load opened November 10.",
        "detail": [
            "PS5 opened at midnight local time. Xbox opened at midnight GMT, which was the evening of November 9 in the US.",
            "Pre-load now so the game is ready the moment your midnight hits.",
        ],
        "sources": [R_NEWS, R_FAQ],
    },
    {
        "slug": "file-size",
        "short": "Up to 212 GB",
        "q": "How many GB is GTA 6?",
        "a": "Up to 212 GB, depending on your console.",
        "detail": [
            "Check your free space before launch night. On PS5: Settings, Storage, Console Storage. On Xbox: Settings, System, Storage devices.",
            "Updates after launch usually make games bigger, so leave some room on top.",
        ],
        "sources": [R_NEWS],
    },
    {
        "slug": "pc",
        "short": "No",
        "q": "Is GTA 6 on PC?",
        "a": "No. Rockstar hasn't announced a PC version.",
        "detail": [
            "At launch it's PS5 and Xbox Series X|S only. That also means no Steam Deck.",
            "Any 'GTA 6 PC download' you see right now is fake.",
        ],
        "sources": [R_ED],
    },
    {
        "slug": "mobile",
        "short": "No, scams only",
        "q": "Can you play GTA 6 on mobile?",
        "a": "No. GTA 6 isn't on phones or tablets.",
        "detail": [
            "Rockstar lists two platforms: PS5 and Xbox Series X|S.",
            "Sites and videos offering a 'GTA 6 Android' or 'iOS' download are scams. Don't install them and don't type in your account details.",
        ],
        "sources": [R_ED],
    },
    {
        "slug": "disc",
        "short": "No, a download code",
        "q": "Does GTA 6 come on a disc?",
        "a": "No. The boxed copy holds a download code.",
        "detail": [
            "The boxed Standard Edition hit stores November 12 with a code inside, not a disc. You redeem it on your console and download the game.",
            "The Ultimate Edition is digital only.",
        ],
        "sources": [R_NEWS],
    },
    {
        "slug": "netflix",
        "short": "No, only a video",
        "q": "Can you play GTA 6 on Netflix?",
        "a": "No. Netflix only showed a gameplay video.",
        "detail": [
            "Netflix premiered 'Grand Theft Auto VI: An Extended Look', a gameplay video captured on PS5, before it went up on Rockstar's YouTube.",
            "The game itself is only on PS5 and Xbox Series X|S.",
        ],
        "sources": [("Netflix Tudum: the Extended Look",
                     "https://www.netflix.com/tudum/articles/grand-theft-auto-6-extended-first-look"), R_ED],
    },
]

NOT_YET = [
    "When GTA 6 Online launches",
    "PS5 Pro graphics modes and frame rate",
    "A PC release date",
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Radio+Canada+Big:wght@400;700&family=Radio+Canada:wght@400;500&display=swap" rel="stylesheet">')

def smart(t):
    t = re.sub(r"(^|\s)'(.+?)'(?=[\s.,]|$)", lambda m: m.group(1) + "“" + m.group(2) + "”", t)
    return t.replace("'", "’")


def e(t):
    return html.escape(smart(t), quote=True)


def head(title, desc, path, prefix, schema):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE_URL}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE_URL}{path}">
<meta name="theme-color" content="#f6f5f1">
{FONTS}
<link rel="stylesheet" href="{prefix}styles.css">
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
<a class="skip btn btn--primary" href="#main">Skip to the answer</a>
<header class="masthead container">
  <a class="wordmark" href="{prefix}" aria-label="{SITE} home"><span>GTA 6</span><span class="wm-2">Answered</span></a>
  <a class="btn btn--secondary" href="{prefix}#questions">All questions</a>
</header>
"""


def foot():
    return f"""<footer class="footer container">
  <p class="statement">Every answer here matches Rockstar’s own pages, or says it hasn’t been confirmed yet.</p>
  <p class="small">Fan-made. Not affiliated with Rockstar Games or Take-Two Interactive. Last checked {CHECKED}.</p>
</footer>
</body>
</html>
"""


def answer_page(item):
    prefix = "../"
    schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": item["q"],
                        "acceptedAnswer": {"@type": "Answer",
                                           "text": item["a"] + " " + " ".join(item["detail"])}}],
    }
    desc = item["a"] + " " + item["detail"][0]
    out = head(f'{item["q"]} | {SITE}', desc[:155], f'{item["slug"]}/', prefix, schema)
    detail = "\n".join(f"    <p>{e(d)}</p>" for d in item["detail"])
    srcs = "\n".join(f'      <li><a href="{e(u)}" rel="noopener">{e(n)}</a></li>' for n, u in item["sources"])
    others = "\n".join(
        f'      <li><a href="../{o["slug"]}/">{e(o["q"])}</a></li>' for o in ANSWERS if o["slug"] != item["slug"])
    out += f"""<main id="main">
  <section class="container q-head">
    <h1 class="question">{e(item["q"])}</h1>
  </section>
  <section class="field answer-band">
    <div class="container">
      <p class="answer">{e(item["a"])}</p>
    </div>
  </section>
  <section class="container detail">
    <div class="detail-text">
{detail}
    </div>
    <div class="sources">
      <p class="label-head">Source</p>
      <ul>
{srcs}
      </ul>
      <p class="small">Checked {CHECKED}</p>
    </div>
  </section>
  <section class="container more" aria-labelledby="more-h">
    <h2 id="more-h">More questions</h2>
    <ul class="q-list q-list--small">
{others}
    </ul>
  </section>
</main>
"""
    return out + foot()


def index_page():
    schema = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL}
    out = head(f"{SITE}: straight answers for launch week",
               "What time GTA 6 comes out, how big it is, and what it's on. Every answer checked against Rockstar, with sources.",
               "", "", schema)
    qs = "\n".join(
        f'      <li><a href="{o["slug"]}/"><span class="q">{e(o["q"])}</span><span class="a">{e(o["short"])}</span></a></li>'
        for o in ANSWERS)
    nots = "\n".join(f"      <li>{e(n)}</li>" for n in NOT_YET)
    out += f"""<main id="main">
  <section class="container hero">
    <div class="hero-text">
      <h1>GTA 6 questions, answered straight.</h1>
      <p class="lead">One question per page, each answer checked against Rockstar’s own pages.</p>
      <a class="btn btn--primary" href="release-time/">See the launch time</a>
    </div>
    <div class="counter" aria-live="polite">
      <p class="counter-num num" id="count">Nov 19</p>
      <p class="counter-label" id="count-label">Midnight your local time, on PS5 and Xbox Series X|S.</p>
    </div>
  </section>
  <section class="container index" id="questions" aria-labelledby="q-h">
    <h2 id="q-h">Confirmed answers</h2>
    <ul class="q-list">
{qs}
    </ul>
  </section>
  <section class="container storage" aria-labelledby="st-h">
    <p class="storage-num num">212 GB</p>
    <div class="storage-text">
      <h2 id="st-h">Check your free space tonight.</h2>
      <p>That’s how much GTA 6 can take, depending on your console.</p>
      <a class="btn btn--secondary" href="file-size/">How to check on PS5 and Xbox</a>
    </div>
  </section>
  <section class="field not-yet" aria-labelledby="ny-h">
    <div class="container ny-grid">
      <h2 id="ny-h">Not confirmed yet</h2>
      <div>
        <ul class="ny-list">
{nots}
        </ul>
        <p class="small">We’ll post these once Rockstar does, not before.</p>
      </div>
    </div>
  </section>
</main>
<script>
(function () {{
  var target = new Date(2026, 10, 19, 0, 0, 0); // local midnight Nov 19
  var num = document.getElementById('count'), lab = document.getElementById('count-label');
  function tick() {{
    var ms = target - new Date();
    if (ms <= 0) {{ num.textContent = 'It\\'s out'; lab.textContent = 'GTA 6 is live where you are.'; return; }}
    var h = Math.floor(ms / 3.6e6), d = Math.floor(h / 24);
    num.textContent = d > 0 ? d + 'd ' + (h % 24) + 'h' : h + 'h ' + Math.floor(ms / 6e4) % 60 + 'm';
    lab.textContent = 'until GTA 6 goes live at your local midnight, Nov 19.';
  }}
  tick(); setInterval(tick, 30000);
}})();
</script>
"""
    return out + foot()


def main():
    ROOT.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for item in ANSWERS:
        d = ROOT / item["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(answer_page(item), encoding="utf-8")
    urls = [BASE_URL] + [f'{BASE_URL}{o["slug"]}/' for o in ANSWERS]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    for f in ("tokens.css", "base.css"):
        (ROOT / f).write_text((ROOT.parent / f).read_text(encoding="utf-8"), encoding="utf-8")
    print("built", len(ANSWERS) + 1, "pages")


if __name__ == "__main__":
    main()
