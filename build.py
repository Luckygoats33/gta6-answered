"""Build calluncgta: static pages from ANSWERS below. Run: py -3 build.py"""
import json, html, pathlib, re

ROOT = pathlib.Path(__file__).parent / "docs"
SITE = "calluncgta"
BASE_URL = "https://callunc.com/"
CHECKED = "Nov 16, 2026"
ISO_DATE = "2026-11-16"
# Fill these in once you have them (Search Console / Bing Webmaster "HTML tag" content value, GA4 "G-..." id).
GSC_TOKEN = ""
BING_TOKEN = ""
GA4_ID = ""
# Ask Unc bot endpoint (the Cloudflare Worker URL + "/ask"). Empty = no chat widget.
ASK_API = ""  # live bot: https://calluncgta-ask.calluncgta-ask.workers.dev/ask (turn on once API credits are added)
INDEXNOW_KEY = "2e328537071e6178a684d7abb373f4eb"

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

S_FORBES = ("Forbes: what the $20 Ultimate upgrade buys you",
            "https://www.forbes.com/sites/brianmazique/2026/10/30/what-gta-vis-20-ultimate-edition-upgrade-actually-buys-you/")
S_STEVIVOR = ("Stevivor: PS5 unlock schedule", "https://stevivor.com/news/gta-6-ps5-unlock-schedule-shows-australia-among-the-first-in-hours-before-north/")
S_WINCENTRAL = ("Windows Central: the New Zealand region switch", "https://www.windowscentral.com/gaming/xbox/grand-theft-auto-6-launch-new-zealand-changing-region")
S_GAMESPOT = ("GameSpot: GTA 6 buying guide", "https://www.gamespot.com/articles/gta-6-buying-guide-get-ready-for-sticker-shock/")
S_VICE_ONLINE = ("Vice: GTA 6 Online release window report", "https://www.vice.com/en/article/gta-6-online-release-window-bloomberg/")
S_MAP = ("Guru3D: Rockstar on the map size", "https://www.guru3d.com/story/gta-vi-map-will-be-twice-the-size-of-gta-v-rockstar-says/")
S_PC = ("GGRecon: GTA 6 isn’t confirmed for PC", "https://www.ggrecon.com/guides/gta-6-pc/")
S_ROME = ("TweakTown: Project ROME rumor", "https://www.tweaktown.com/news/107895/rockstar-games-rumored-to-unveil-project-rome-modding-engine-for-gta-6-very-soon/index.html")

ANSWERS += [
    {"slug": "upgrade-to-ultimate", "short": "Yes, any time", "q": "Can I upgrade GTA 6 to Ultimate later?",
     "a": "Yes. Standard owners can buy the upgrade any time.",
     "detail": ["Buy it from the PlayStation Store or Microsoft Store after the game is on your console.",
                "Xbox lists the upgrade at $20. On PlayStation the price only shows once you own the Standard Edition."],
     "sources": [R_ED, S_FORBES]},
    {"slug": "play-early", "short": "No early access", "q": "Can you play GTA 6 early?",
     "a": "No. There’s no early access.",
     "detail": ["The game goes live at midnight in your own time zone. Pre-load it now so it’s ready.",
                "The 'New Zealand trick' isn’t official. On PS5 it needs a separate New Zealand account and a second purchase. The Xbox region switch is unproven, so don’t buy the game twice on a rumor."],
     "sources": [R_TIMES, S_STEVIVOR, S_WINCENTRAL]},
    {"slug": "consoles", "short": "Series S yes, PS4 and Xbox One no", "q": "Is GTA 6 on PS4, Xbox One or Series S?",
     "a": "Series S yes. PS4 and Xbox One no.",
     "detail": ["Rockstar lists two platforms: PlayStation 5 and Xbox Series X|S. That covers the Series S.",
                "The Series S has the smallest drive of the three, so check your free space against the 212 GB download first."],
     "sources": [R_ED, R_NEWS]},
    {"slug": "price", "short": "$79.99 or $99.99", "status": "reported", "q": "How much is GTA 6?",
     "a": "$79.99 Standard, $99.99 Ultimate.",
     "detail": ["Those are US prices, and every major outlet reports the same two.",
                "Buying digitally before launch adds the Vintage Vice City Pack. Sources differ on whether the cutoff is November 19 or 20."],
     "sources": [S_FORBES, R_ED]},
    {"slug": "standard-vs-ultimate", "short": "$20 more, 16 extras", "status": "reported",
     "q": "What’s the difference between Standard and Ultimate?",
     "a": "$20 more for 16 extra items.",
     "detail": ["The extras are vehicles, weapons, clothing, special locations and activities, all in the single-player game.",
                "Ultimate is digital only. The boxed Standard copy has a download code inside."],
     "sources": [S_FORBES, R_ED]},
    {"slug": "online", "short": "Not at launch", "status": "reported", "q": "Does GTA 6 have online?",
     "a": "Not at launch. It starts single-player.",
     "detail": ["Rockstar hasn’t announced a date for GTA 6 Online.",
                "'Late 2027' comes from a Bloomberg report, not from Rockstar."],
     "sources": [S_VICE_ONLINE]},
    {"slug": "game-pass", "short": "Not at launch", "status": "reported", "q": "Is GTA 6 on Game Pass?",
     "a": "Not at launch.",
     "detail": ["You buy the game outright on Xbox or PlayStation.",
                "You don’t need Game Pass or PlayStation Plus to play the single-player story."],
     "sources": [S_GAMESPOT]},
    {"slug": "map-size", "short": "About twice GTA V", "status": "reported", "q": "How big is the GTA 6 map?",
     "a": "About twice the size of GTA V.",
     "detail": ["Rockstar compares the state of Leonida to the maps of GTA IV, GTA V and Red Dead Redemption 2 put together.",
                "It has six regions: Vice City, the Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga National Park. Rockstar hasn’t published a full map."],
     "sources": [S_MAP]},
]

LAUNCH = [  # (place, zone, local unlock, UTC ISO)
    ("New Zealand", "NZDT, UTC+13", "2026-11-18T11:00:00Z"),
    ("Sydney", "AEDT, UTC+11", "2026-11-18T13:00:00Z"),
    ("Tokyo", "JST, UTC+9", "2026-11-18T15:00:00Z"),
    ("India", "IST, UTC+5:30", "2026-11-18T18:30:00Z"),
    ("Paris, Berlin, Madrid", "CET, UTC+1", "2026-11-18T23:00:00Z"),
    ("London", "GMT, UTC+0", "2026-11-19T00:00:00Z"),
    ("São Paulo", "BRT, UTC−3", "2026-11-19T03:00:00Z"),
    ("New York", "EST, UTC−5", "2026-11-19T05:00:00Z"),
    ("Chicago", "CST, UTC−6", "2026-11-19T06:00:00Z"),
    ("Denver", "MST, UTC−7", "2026-11-19T07:00:00Z"),
    ("Los Angeles", "PST, UTC−8", "2026-11-19T08:00:00Z"),
    ("Hawaii", "HST, UTC−10", "2026-11-19T10:00:00Z"),
]

FACTS = [  # (group, rows of (label, value, status, source))
    ("Editions", [
        ("Standard Edition", "$79.99. Digital, or boxed with a download code (no disc).", "Price reported", S_FORBES),
        ("Ultimate Edition", "$99.99. Digital only. Adds 16 items: vehicles, weapons, clothing, locations, activities.", "Reported", S_FORBES),
        ("Ultimate upgrade", "Sold separately to Standard owners, any time.", "Confirmed", R_ED),
        ("Pre-order bonus", "Vintage Vice City Pack for digital orders before launch.", "Cutoff date unclear", S_FORBES),
    ]),
    ("Platforms", [
        ("PlayStation 5", "Yes, including PS5 Pro.", "Confirmed", R_ED),
        ("Xbox Series X|S", "Yes, both consoles.", "Confirmed", R_ED),
        ("PC", "Not announced.", "Confirmed", S_PC),
        ("PS4, Xbox One, mobile", "No.", "Confirmed", R_ED),
    ]),
    ("Dates", [
        ("Pre-load opened", "November 10, 2026.", "Confirmed", R_NEWS),
        ("Boxed copies in stores", "November 12, 2026.", "Confirmed", R_NEWS),
        ("Release", "November 19, 2026, midnight local time.", "Confirmed", R_TIMES),
        ("GTA 6 Online", "No date. Single-player at launch.", "Reported", S_VICE_ONLINE),
    ]),
    ("Size and map", [
        ("Download", "Up to 212 GB depending on console.", "Confirmed", R_NEWS),
        ("Setting", "Leonida, a fictional state based on Florida, with Vice City.", "Confirmed", S_MAP),
        ("Map size", "About twice GTA V.", "Reported", S_MAP),
        ("Regions", "Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia, Mount Kalaga National Park.", "Reported", S_MAP),
    ]),
]

RUMORS = [  # (claim, verdict, what we know, source)
    ("GTA 6 has been delayed again", "False", "Rockstar’s support page still lists November 19 at midnight local time.", R_TIMES),
    ("GTA 6 comes on a disc", "False", "The boxed copy holds a download code, not a disc.", R_NEWS),
    ("You can play GTA 6 on Netflix", "False", "Netflix showed a gameplay video. The game is only on PS5 and Xbox Series X|S.", ("Netflix Tudum", "https://www.netflix.com/tudum/articles/grand-theft-auto-6-extended-first-look")),
    ("GTA 6 is on Android or iPhone", "False", "Not on mobile. 'Mobile downloads' are scams.", R_ED),
    ("New Zealand players get it first", "True", "Every region goes live at its own midnight, and New Zealand hits midnight first.", R_TIMES),
    ("Switching your Xbox region gets you in early", "Unproven", "Reported as a trick, but nobody has confirmed it works for GTA 6.", S_WINCENTRAL),
    ("GTA 6 Online launches in late 2027", "Reported", "From a Bloomberg report. Rockstar hasn’t given a date.", S_VICE_ONLINE),
    ("GTA 6 is on Game Pass day one", "Reported false", "Reported as not coming to Game Pass at launch.", S_GAMESPOT),
    ("A PC version arrives in early 2027", "Unconfirmed", "Outlets are guessing. Rockstar hasn’t announced PC.", S_PC),
    ("Rockstar is launching a mod tool called Project ROME", "Unconfirmed", "From a fan account. No announcement from Rockstar.", S_ROME),
]

NOT_YET = [
    "When GTA 6 Online launches",
    "PS5 Pro graphics modes and frame rate",
    "A PC release date",
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600;800&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">')

def smart(t):
    t = re.sub(r"(^|\s)'(.+?)'(?=[\s.,]|$)", lambda m: m.group(1) + "“" + m.group(2) + "”", t)
    return t.replace("'", "’")


def e(t):
    return html.escape(smart(t), quote=True)


def verify_tags():
    out = ""
    if GSC_TOKEN:
        out += f'\n<meta name="google-site-verification" content="{GSC_TOKEN}">'
    if BING_TOKEN:
        out += f'\n<meta name="msvalidate.01" content="{BING_TOKEN}">'
    return out


def ga4_tag():
    if not GA4_ID:
        return ""
    return (f'\n<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
            f"\n<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>")


def crumbs(trail):
    """trail: list of (name, path) from home; returns (schema dict, visible html)."""
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE_URL + pth} for i, (n, pth) in enumerate(trail)]
    links = " <span aria-hidden=\"true\">/</span> ".join(
        f'<a href="../{pth}">{e(n)}</a>' if i < len(trail) - 1 else f'<span aria-current="page">{e(n)}</span>'
        for i, (n, pth) in enumerate(trail))
    return ({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
            f'<nav class="crumbs" aria-label="Breadcrumb">{links}</nav>')


def updated_line():
    return f'<p class="updated">Updated <time datetime="{ISO_DATE}">{CHECKED}</time></p>'


UNC_MARK = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', (pathlib.Path(__file__).parent / "unc.svg").read_text(encoding="utf-8").strip()).replace('"#000"', '"currentColor"')


def unc_svg(cls="wm-mark-svg"):
    return f'<svg class="{cls}" viewBox="0 0 256 256" aria-hidden="true" focusable="false">{UNC_MARK}</svg>'


def head(title, desc, path, prefix, schema):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">{verify_tags()}
<link rel="canonical" href="{BASE_URL}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE}">
<meta property="og:image" content="{BASE_URL}img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:url" content="{BASE_URL}{path}">
<meta name="theme-color" content="#0b0b0d">
<link rel="icon" href="{prefix}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{prefix}img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{prefix}img/apple-touch-icon.png">
<script>document.documentElement.classList.add("js")</script>
{FONTS}
<link rel="stylesheet" href="{prefix}styles.css">
<script type="application/ld+json">{json.dumps(schema)}</script>{ga4_tag()}
</head>
<body>
<div class="rain" aria-hidden="true"></div>
<a class="skip btn btn--primary" href="#main">Skip to the answer</a>
<header class="masthead container">
  <a class="wordmark" href="{prefix}" aria-label="{SITE} home"><span class="wm-mark">{unc_svg()}</span><span class="wm-1">call</span><span class="wm-2">unc</span><span class="wm-3">gta</span></a>
  <nav class="topnav" aria-label="Main">
    <a href="{prefix}#questions">Answers</a>
    <a href="{prefix}launch-times/">Launch times</a>
    <a href="{prefix}facts/">Facts</a>
    <a href="{prefix}rumors/">Rumors</a>
    <a href="{prefix}news/">News</a>
  </nav>
</header>
"""


def foot():
    return f"""<footer class="footer container">
  <p class="statement">Unc knows. <span class="splash">Just ask.</span></p>
  <p class="foot-note">Every answer here matches Rockstar’s own pages, or says it hasn’t been confirmed yet.</p>
  <p class="small">Fan-made. Not affiliated with Rockstar Games or Take-Two Interactive. Last checked {CHECKED}.</p>
</footer>
<script>
(function () {{
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    document.querySelectorAll('video').forEach(function (v) {{ v.removeAttribute('autoplay'); v.pause(); }});
  }}
  var hv = document.querySelector('.stage-video');
  var slow = navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType || ''));
  if (hv && (window.innerWidth < 700 || slow)) {{ hv.remove(); }}
  var lazy = document.querySelectorAll('video[data-lazy]');
  if ('IntersectionObserver' in window && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) {{
    var vo = new IntersectionObserver(function (es) {{
      es.forEach(function (en) {{ var v = en.target; if (en.isIntersecting) {{ v.preload = 'auto'; var pr = v.play(); if (pr && pr.catch) pr.catch(function () {{}}); }} else {{ v.pause(); }} }});
    }}, {{ rootMargin: '200px 0px' }});
    lazy.forEach(function (v) {{ vo.observe(v); }});
  }}
  var els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {{ els.forEach(function (el) {{ el.classList.add('in'); }}); return; }}
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (en) {{ if (en.isIntersecting) {{ en.target.classList.add('in'); io.unobserve(en.target); }} }});
  }}, {{ rootMargin: '0px 0px -8% 0px' }});
  els.forEach(function (el) {{ io.observe(el); }});
}})();
</script>{ask_tag()}
</body>
</html>
"""


def answer_page(item):
    prefix = "../"
    bc_schema, bc_html = crumbs([("Home", ""), (item["short"] if len(item["q"]) > 60 else item["q"], item["slug"] + "/")])
    schema = [{
        "@context": "https://schema.org", "@type": "FAQPage", "dateModified": ISO_DATE, "inLanguage": "en",
        "mainEntity": [{"@type": "Question", "name": item["q"],
                        "acceptedAnswer": {"@type": "Answer",
                                           "text": item["a"] + " " + " ".join(item["detail"])}}],
    }, bc_schema]
    desc = item["a"] + " " + item["detail"][0]
    out = head(f'{item["q"]} | {SITE}', desc[:155], f'{item["slug"]}/', prefix, schema)
    detail = "\n".join(f"    <p>{e(d)}</p>" for d in item["detail"])
    srcs = "\n".join(f'      <li><a href="{e(u)}" rel="noopener">{e(n)}</a></li>' for n, u in item["sources"])
    others = "\n".join(
        f'      <li><a href="../{o["slug"]}/">{e(o["q"])}</a></li>' for o in ANSWERS if o["slug"] != item["slug"])
    out += f"""<main id="main">
  <section class="container q-head">
    {bc_html}
    <h1 class="question">{e(item["q"])}</h1>
    {updated_line()}
  </section>
  <section class="field answer-band">
    <div class="container">
      <p class="answer">{e(item["a"])}</p>
      {'<p class="status-note">Reported by press. Rockstar hasn’t confirmed this on its own pages.</p>' if item.get("status") == "reported" else ''}
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


def home_news():
    items = NEWS["items"][:5]
    if not items:
        return ""
    rows = NL.join("      " + news_item(o) for o in items)
    return f"""  <section class="reveal container news-home" aria-labelledby="news-h">
    <div class="news-home-head"><h2 id="news-h">Latest news</h2><a class="news-more" href="news/">All headlines</a></div>
    <ol class="news-list">
{rows}
    </ol>
  </section>
"""


def index_page():
    schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE_URL, "inLanguage": "en",
               "description": "Straight, sourced answers to GTA 6 questions for launch week."},
              {"@context": "https://schema.org", "@type": "Organization", "name": SITE, "url": BASE_URL,
               "logo": BASE_URL + "img/og.jpg"}]
    out = head(f"{SITE}: straight answers for launch week",
               "What time GTA 6 comes out, how big it is, and what it's on. Every answer checked against Rockstar, with sources.",
               "", "", schema)
    def row(o):
        return f'      <li><a href="{o["slug"]}/"><span class="q">{e(o["q"])}</span><span class="a">{e(o["short"])}</span></a></li>'
    qs = "\n".join(row(o) for o in ANSWERS if o.get("status") != "reported")
    rqs = "\n".join(row(o) for o in ANSWERS if o.get("status") == "reported")
    nots = "\n".join(f"      <li>{e(n)}</li>" for n in NOT_YET)
    out += f"""<main id="main">
  <section class="stage">
    <div class="stage-media" aria-hidden="true">
      <img class="stage-img" src="img/hero.webp" srcset="img/hero-960.webp 960w, img/hero.webp 1920w" sizes="100vw" alt="" fetchpriority="high">
      <video class="stage-video" autoplay muted loop playsinline preload="metadata" poster="img/hero.webp"><source src="img/hero.mp4" type="video/mp4"></video>
    </div>
    <div class="container stage-inner">
      <div class="panel panel--title">
        <p class="caption">Leonida. Launch week. Everybody’s got questions.</p>
        <h1><span class="h-line">You got questions.</span> <span class="h-line splash">Unc got answers.</span></h1>
        <p class="lead">Every GTA 6 answer checked against Rockstar. No BS.</p>
        <div class="cta"><a class="btn btn--primary" href="release-time/">See the launch time</a><a class="btn btn--secondary" href="#questions">Browse answers</a></div>
      </div>
      <div class="panel panel--count" aria-live="polite">
        <p class="caption">Goes live in</p>
        <p class="counter-num num" id="count">Nov 19</p>
        <p class="counter-label" id="count-label">Midnight your local time, on PS5 and Xbox Series X|S.</p>
      </div>
    </div>
  </section>
  <div class="ticker" aria-hidden="true"><div class="ticker-track"><span>Unc knows. Just ask. ✦ Every answer sourced ✦ No leaks, no BS ✦ Nov 19, midnight local ✦ 212 GB, clear your space ✦&nbsp;</span><span>Unc knows. Just ask. ✦ Every answer sourced ✦ No leaks, no BS ✦ Nov 19, midnight local ✦ 212 GB, clear your space ✦&nbsp;</span></div></div>
  <section class="reveal container index" id="questions" aria-labelledby="q-h">
    <h2 id="q-h">Confirmed answers</h2>
    <ul class="q-list">
{qs}
    </ul>
  </section>
  <section class="reveal container index index--reported" aria-labelledby="r-h">
    <h2 id="r-h">Reported, not yet confirmed</h2>
    <ul class="q-list">
{rqs}
    </ul>
  </section>
{home_news()}  <section class="reveal field hubs" aria-labelledby="hub-h">
    <div class="container hub-grid">
      <h2 id="hub-h" class="visually-hidden">More</h2>
      <a class="hub" href="launch-times/"><video class="hub-img" data-lazy muted loop playsinline preload="none" poster="img/clock2.webp" aria-label="A sunset clock tower near midnight over a neon beach boulevard"><source src="img/clock2.mp4" type="video/mp4"></video><span class="hub-n">01</span><span class="hub-t">Launch times</span><span class="hub-d">Every region, in your time zone.</span></a>
      <a class="hub" href="facts/"><video class="hub-img" data-lazy muted loop playsinline preload="none" poster="img/shop2.webp" aria-label="A neon game and electronics shop on a Florida strip at dusk"><source src="img/shop2.mp4" type="video/mp4"></video><span class="hub-n">02</span><span class="hub-t">Facts</span><span class="hub-d">Editions, platforms, dates, the map.</span></a>
      <a class="hub" href="rumors/"><video class="hub-img" data-lazy muted loop playsinline preload="none" poster="img/cruise2.webp" aria-label="A convertible cruising a causeway toward a glowing skyline"><source src="img/cruise2.mp4" type="video/mp4"></video><span class="hub-n">03</span><span class="hub-t">Rumors</span><span class="hub-d">What’s true, what’s reported, what’s false.</span></a>
    </div>
  </section>
  <section class="reveal container storage" aria-labelledby="st-h">
    <p class="storage-num num">212 GB</p>
    <div class="storage-text">
      <h2 id="st-h">Check your free space tonight.</h2>
      <p>That’s how much GTA 6 can take, depending on your console.</p>
      <a class="btn btn--secondary" href="file-size/">How to check on PS5 and Xbox</a>
    </div>
  </section>
  <section class="reveal field not-yet" aria-labelledby="ny-h">
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


def src_link(s, short=False):
    label = s[0].split(":")[0] if short else s[0]
    return f'<a href="{e(s[1])}" rel="noopener">{e(label)}</a>'


NL = chr(10)
HUB_ART = {"launch-times": ("clock2", "A sunset clock tower near midnight over a neon beach boulevard"), "facts": ("shop2", "A neon game and electronics shop on a Florida strip at dusk"), "rumors": ("cruise2", "A convertible cruising a causeway toward a glowing skyline")}


def load_news():
    f = pathlib.Path(__file__).parent / "data" / "news.json"
    if not f.exists():
        return {"fetched_at": "", "items": []}
    return json.loads(f.read_text(encoding="utf-8"))


NEWS = load_news()


def news_source(name):
    return re.sub(r"\.(com|net|org)$", "", name)


def news_when(iso, with_time=False):
    from datetime import datetime
    d = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    out = d.strftime("%b ") + str(d.day)
    return out + d.strftime(", %H:%M UTC") if with_time else out


def news_item(o):
    return (f'<li class="news-item"><time class="news-date" datetime="{e(o["date"])}">{news_when(o["date"])}</time>'
            f'<span class="news-src">{e(news_source(o["source"]))}</span>'
            f'<a class="news-link" href="{e(o["url"])}" target="_blank" rel="noopener nofollow">{e(o["title"])}</a></li>')


def news_page():
    out = hub_head("news", "GTA 6 news: latest headlines",
                   "The latest GTA 6 headlines from Rockstar and the gaming press, refreshed every day. Click through to read each story at its source.",
                   "Latest GTA 6 news",
                   "Headlines from Rockstar, the gaming press and major news outlets, refreshed every day. Each one links to the full story at its source.")
    items = NEWS["items"]
    if not items:
        out += '  <section class="container more"><p>No headlines yet. Check back tomorrow.</p></section>' + NL
    else:
        out += '  <section class="container news-wrap" aria-label="Headlines">' + NL + '    <ol class="news-list">' + NL
        out += NL.join("      " + news_item(o) for o in items) + NL + "    </ol>" + NL + "  </section>" + NL
    stamp = news_when(NEWS["fetched_at"], True) if NEWS["fetched_at"] else CHECKED
    out += (f'  <section class="container more"><p class="small">Headlines last pulled {stamp}. Reports and leaks are the outlets’ claims, not Rockstar’s. '
            'For what Rockstar has actually confirmed, see <a href="../facts/">Facts</a>.</p></section>' + NL + "</main>" + NL)
    return out + foot()


def hub_head(slug, title, desc, h1, lead, schema_type="WebPage"):
    bc_schema, bc_html = crumbs([("Home", ""), (title.split(":")[0].replace("GTA 6 ", "").capitalize(), slug + "/")])
    schema = [{"@context": "https://schema.org", "@type": schema_type, "name": title, "url": f"{BASE_URL}{slug}/",
               "dateModified": ISO_DATE, "inLanguage": "en"}, bc_schema]
    out = head(f"{title} | {SITE}", desc, f"{slug}/", "../", schema)
    out += f"""<main id="main">
  <section class="container q-head">
    {bc_html}
    <h1 class="question">{e(h1)}</h1>
    {updated_line()}
    <p class="lead hub-lead">{e(lead)}</p>
  </section>
""" + (f'  <figure class="container hub-banner"><video data-lazy muted loop playsinline preload="none" poster="../img/{HUB_ART[slug][0]}.webp" aria-label="{e(HUB_ART[slug][1])}"><source src="../img/{HUB_ART[slug][0]}.mp4" type="video/mp4"></video></figure>' + NL if slug in HUB_ART else "")
    return out


def launch_page():
    out = hub_head("launch-times", "GTA 6 launch times by region",
                   "GTA 6 goes live at midnight local time on November 19. Every region's unlock time, converted to yours.",
                   "When does GTA 6 go live where you are?",
                   "Midnight local time on November 19, everywhere. So New Zealand plays first and Hawaii plays 23 hours later.")
    rows = "\n".join(
        f'      <tr><th scope="row">{e(p)}</th><td>{e(z)}</td><td class="num" data-utc="{u}">{u[:10]} {u[11:16]} UTC</td></tr>'
        for p, z, u in LAUNCH)
    out += f"""  <section class="field answer-band">
    <div class="container you-grid">
      <p class="answer" id="you-time">Midnight, Nov 19</p>
      <p class="status-note" id="you-note">That’s when it goes live in your own time zone.</p>
    </div>
  </section>
  <section class="container table-wrap" aria-labelledby="t-h">
    <h2 id="t-h">Every region, in your time</h2>
    <table class="facts-table">
      <thead><tr><th scope="col">Region</th><th scope="col">Time zone</th><th scope="col">Goes live (your time)</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
    <p class="small">Rule from {src_link(R_TIMES)}. Times are the rule converted to each zone. Checked {CHECKED}.</p>
  </section>
</main>
<script>
(function () {{
  var fmt = {{ weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }};
  document.querySelectorAll('[data-utc]').forEach(function (td) {{
    td.textContent = new Date(td.dataset.utc).toLocaleString(undefined, fmt);
  }});
  var nz = new Date('2026-11-18T11:00:00Z');
  var tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'your time zone';
  document.getElementById('you-note').textContent = 'Midnight, Nov 19 in ' + tz + '. New Zealand starts at ' + nz.toLocaleString(undefined, fmt) + ' your time.';
}})();
</script>
"""
    return out + foot()


def facts_page():
    out = hub_head("facts", "GTA 6 facts: editions, platforms, dates, map",
                   "Every confirmed GTA 6 fact in one place, each with its source and whether Rockstar confirmed it.",
                   "Everything confirmed about GTA 6",
                   "One line per fact. Each one is marked as confirmed by Rockstar or reported by the press, with a source.")
    for group, rows in FACTS:
        body = "\n".join(
            f'      <tr><th scope="row">{e(l)}</th><td>{e(v)}</td><td class="st st--{"ok" if s == "Confirmed" else "rep"}">{e(s)}</td><td>{src_link(src, True)}</td></tr>'
            for l, v, s, src in rows)
        out += f"""  <section class="container table-wrap" aria-label="{e(group)}">
    <h2>{e(group)}</h2>
    <table class="facts-table">
      <thead><tr><th scope="col">Fact</th><th scope="col">Detail</th><th scope="col">Status</th><th scope="col">Source</th></tr></thead>
      <tbody>
{body}
      </tbody>
    </table>
  </section>
"""
    out += f'  <section class="container more"><p class="small">Checked {CHECKED}.</p></section>\n</main>\n'
    return out + foot()


def rumors_page():
    out = hub_head("rumors", "GTA 6 rumor tracker",
                   "GTA 6 rumors checked: delays, discs, early access, Online, PC, Game Pass, mods. True, false or unconfirmed, with sources.",
                   "GTA 6 rumors, checked",
                   "Each rumor gets a plain verdict and the source behind it. Updated as Rockstar confirms things.")
    def cls(v):
        return "no" if v.startswith(("False", "Reported false")) else "ok" if v == "True" else "rep"
    rows = "\n".join(
        f'      <li class="rumor"><p class="rumor-claim">{e(c)}</p><div class="rumor-body"><p class="st st--{cls(v)} rumor-verdict">{e(v)}</p><p>{e(w)} {src_link(s, True)}</p></div></li>'
        for c, v, w, s in RUMORS)
    out += f"""  <section class="container">
    <ol class="rumor-list">
{rows}
    </ol>
    <p class="small">Checked {CHECKED}.</p>
  </section>
</main>
"""
    return out + foot()


HUBS = {"launch-times": launch_page, "facts": facts_page, "rumors": rumors_page, "news": news_page}


def ask_tag():
    if not ASK_API:
        return ""
    return NL + f'<script src="/ask.js" data-api="{e(ASK_API)}" defer></script>'


def src_text(s):
    return f"{s[0]} ({s[1]})"


def kb_text():
    """Plain-text knowledge base for the Ask Unc bot, built from the same data as the pages."""
    out = [f"Last checked: {CHECKED}.", "", "## Answer pages"]
    for a in ANSWERS:
        status = a.get("status", "confirmed")
        out.append(f"Q: {a['q']}")
        out.append(f"A ({status}): {a['a']} " + " ".join(a["detail"]))
        out.append(f"Page: {BASE_URL}{a['slug']}/")
        out.append("Sources: " + "; ".join(src_text(x) for x in a["sources"]))
        out.append("")
    out.append(f"## Launch unlock times (page: {BASE_URL}launch-times/)")
    out.append("Every region unlocks at midnight local time on November 19, 2026. In UTC:")
    for place, zone, utc in LAUNCH:
        out.append(f"- {place} ({zone}): {utc}")
    out.append("")
    out.append(f"## Facts sheet (page: {BASE_URL}facts/)")
    for group, rows in FACTS:
        for label, value, status, src in rows:
            out.append(f"- {group} / {label}: {value} [{status}; {src_text(src)}]")
    out.append("")
    out.append(f"## Rumor checks (page: {BASE_URL}rumors/)")
    for claim, verdict, know, src in RUMORS:
        out.append(f'- "{claim}": {verdict}. {know} [{src_text(src)}]')
    out.append("")
    out.append("## Not announced yet")
    out.extend(f"- {x}" for x in NOT_YET)
    return NL.join(out)


def main():
    ROOT.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for item in ANSWERS:
        d = ROOT / item["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(answer_page(item), encoding="utf-8")
    for slug, fn in HUBS.items():
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(fn(), encoding="utf-8")
    urls = [BASE_URL] + [f'{BASE_URL}{o["slug"]}/' for o in ANSWERS] + [f"{BASE_URL}{s}/" for s in HUBS]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{ISO_DATE}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (ROOT / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    (ROOT / "news.json").write_text(json.dumps({"fetched_at": NEWS["fetched_at"], "items": [
        {k: o[k] for k in ("title", "source", "date", "url")} for o in NEWS["items"][:20]]}, ensure_ascii=False), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    worker_src = ROOT.parent / "worker" / "src"
    if worker_src.exists():
        (worker_src / "kb.ts").write_text("// Generated by build.py from the site data. Do not edit." + NL + "export const KB = " + json.dumps(kb_text(), ensure_ascii=False) + ";" + NL, encoding="utf-8")
    for f in ("tokens.css", "base.css", "ask.js"):
        (ROOT / f).write_text((ROOT.parent / f).read_text(encoding="utf-8"), encoding="utf-8")
    print("built", len(ANSWERS) + 1 + len(HUBS), "pages")


if __name__ == "__main__":
    main()
