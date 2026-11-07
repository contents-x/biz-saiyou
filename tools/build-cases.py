#!/usr/bin/env python3
"""
tools/build-cases.py  —  イチ推し採用 (recruitx) case studies builder
Fetch rx_case posts from WP REST API:
  1. case.html のカードグリッドを更新（BUILD markers 間を差し替え）
  2. /case/{slug}/index.html を静的生成
  3. sitemap.xml の /case/ エントリを更新（存在する場合）
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

ROOT = Path(__file__).parent.parent
CASE_HTML = ROOT / "case.html"
CASE_DIR = ROOT / "case"
TEMPLATE_PATH = ROOT / "tools" / "templates" / "case-detail.html.tpl"
SITEMAP_PATH = ROOT / "sitemap.xml"

SITE_URL = "https://ichioshi.contentsx.jp"
API_BASE = "https://cms.contentsx.jp/wp-json/contentsx/v1"

# ---- XSS sanitizer (allowlist-based HTMLParser) ----

ALLOWED_TAGS = {
    "p", "br", "strong", "em", "b", "i", "u", "s", "del",
    "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "figcaption",
    "blockquote", "cite",
    "dl", "dt", "dd",
    "small", "sup", "sub",
}

ALLOWED_ATTRS = {
    "a": {"href", "title", "rel"},
    "img": {"src", "alt", "width", "height", "loading", "decoding"},
    "th": {"scope"},
    "td": {"colspan", "rowspan"},
}

VOID_TAGS = {"br", "img"}


class _Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out: list = []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            return
        allowed = ALLOWED_ATTRS.get(tag, set())
        safe_attrs = ""
        for name, val in attrs:
            if name not in allowed:
                continue
            val = (val or "").replace('"', "&quot;")
            if name == "href" and not re.match(r"^(https?://|/|#)", val):
                continue
            if name == "src" and not re.match(r"^https?://", val):
                continue
            safe_attrs += f' {name}="{val}"'
        if tag in VOID_TAGS:
            self.out.append(f"<{tag}{safe_attrs}>")
        else:
            self.out.append(f"<{tag}{safe_attrs}>")

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        self.out.append(
            data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    def handle_entityref(self, name):
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")


def sanitize_html(raw: str) -> str:
    s = _Sanitizer()
    s.feed(raw or "")
    return "".join(s.out)


# ---- SVG helpers ----

SVG_ARROW_UP = (
    '<svg class="rx-ccard__stat-arrow" viewBox="0 0 16 16" fill="none"'
    ' stroke="currentColor" stroke-width="1.8" stroke-linecap="round"'
    ' stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 13 13 3M6 3h7v7"/></svg>'
)
SVG_ARROW_DOWN = (
    '<svg class="rx-ccard__stat-arrow" viewBox="0 0 16 16" fill="none"'
    ' stroke="currentColor" stroke-width="1.8" stroke-linecap="round"'
    ' stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 3l10 10M13 6v7H6"/></svg>'
)
SVG_MORE = (
    '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor"'
    ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    ' aria-hidden="true"><path d="M3 10h14M11 4l6 6-6 6"/></svg>'
)


def _arrow_svg(arrow: str) -> str:
    if arrow == "up":
        return SVG_ARROW_UP
    if arrow == "down":
        return SVG_ARROW_DOWN
    return ""


def _norm_stat(s: dict) -> dict:
    """カード/詳細タイル用に stat を「ラベル / 数字 / 短い単位」へ正規化する。
    WP側の数値はラベルに括弧補足や before→after が混ざっていてカードからはみ出すため、
    表示直前にここで整える（WPデータは変更しない）。
      - 括弧（…）/(…) の補足を除去（81%減・15日・2店舗・沖縄 等は詳細ページに残る）
      - before→after（A→B）は到達値 B を採用
      - 先頭の数値（1,234 / 5.3 / 10〜15 等）を value、残りを unit に分離
    """
    full = f"{s.get('label','')} {s.get('value','')} {s.get('unit','')}".strip()
    arrow = str(s.get("arrow", "none"))
    full = re.sub(r"[（(][^）)]*[）)]", "", full)          # 括弧補足を除去
    full = re.sub(r"\s+", " ", full).strip()
    m = re.match(r"^([^\d，,]+?)\s*(?=[\d，,])", full)      # 先頭の非数値=ラベル
    label = m.group(1).strip() if m else ""
    rem = full[m.end():].strip() if m else full
    if "→" in rem:                                          # before→after は後者を採用
        rem = rem.split("→")[-1].strip()
    nm = re.search(r"[\d][\d,\.，〜~]*", rem)               # 数値（範囲含む）
    if not nm:
        return {"label": label, "value": rem, "unit": "", "arrow": arrow}
    value = nm.group(0).rstrip(".,，")
    unit = (rem[:nm.start()] + rem[nm.end():]).strip()
    # カード幅対策: 採用単価等の "/名" はラベルで自明なので落とす
    unit = re.sub(r"\s*/\s*名$", "", unit)
    # 「名/4か月」「名応募/月」など期間付きの長い名-単位は「名」に簡略化（期間は説明文に残る）
    if unit.startswith("名") and len(unit) > 3:
        unit = "名"
    # 6桁以上の「円」は万円に丸めて桁幅を抑える（例 142,881円 → 14.3万円）
    if unit.startswith("円"):
        digits = value.replace(",", "").replace("，", "")
        if digits.isdigit() and int(digits) >= 100000:
            value = f"{int(digits) / 10000:.1f}".rstrip("0").rstrip(".")
            unit = "万" + unit
    return {"label": label, "value": value, "unit": unit, "arrow": arrow}


def _build_stats_items(stats: list) -> str:
    items = []
    for s in stats[:3]:
        n = _norm_stat(s)
        label = n["label"]
        value = n["value"]
        unit = n["unit"]
        arrow_svg = _arrow_svg(n["arrow"])
        label_html = f'<span class="rx-ccard__stat-label">{label}</span>' if label else ''
        items.append(
            f'              <li>'
            f'{label_html}'
            f'<span class="rx-ccard__stat-value">'
            f'<span class="rx-ccard__stat-fig"><b class="rx-stat-num">{value}</b><small>{unit}</small></span>'
            f'{arrow_svg}'
            f'</span></li>'
        )
    return "\n".join(items)


def build_card(case: dict) -> str:
    slug = case.get("slug", "")
    company = case.get("company", "")
    tags = case.get("tags", [])
    tag_slugs = case.get("tag_slugs", [])
    summary = case.get("summary", "")
    image = case.get("image", "")
    stats = case.get("stats", [])

    category = tag_slugs[0] if tag_slugs else "other"

    # "業種 / 採用種別" 形式
    if len(tags) >= 2:
        cat_text = f'{tags[0]} <span>/</span> {"・".join(tags[1:])}'
    elif tags:
        cat_text = tags[0]
    else:
        cat_text = ""

    img_html = (
        f'<img src="{image}" alt="{company}の採用成功事例"'
        f' width="724" height="543" loading="lazy" decoding="async">'
        if image else ""
    )

    stats_items = _build_stats_items(stats)

    return (
        f'\n          <li class="rx-ccard rx-anim" data-category="{category}">'
        f'\n            <figure class="rx-ccard__media">'
        f'\n              {img_html}'
        f'\n            </figure>'
        f'\n            <div class="rx-ccard__body">'
        f'\n              <p class="rx-ccard__cat">{cat_text}</p>'
        f'\n              <h3 class="rx-ccard__company">{company}</h3>'
        f'\n              <p class="rx-ccard__desc">{summary}</p>'
        f'\n            </div>'
        f'\n            <ul class="rx-ccard__stats">'
        f'\n{stats_items}'
        f'\n            </ul>'
        f'\n            <a class="rx-ccard__more" href="case/{slug}/">詳しく見る{SVG_MORE}</a>'
        f'\n          </li>'
    )


def _cat_text(tags: list) -> str:
    if len(tags) >= 2:
        return f'{tags[0]} <span>/</span> {"・".join(tags[1:])}'
    return tags[0] if tags else ""


def build_related(case: dict, all_cases: list, limit: int = 6) -> str:
    """同じ業態タグを多く共有する事例を上位 limit 件選び、関連カードHTMLを返す。
    詳細ページ間リンクは相対パス ../{slug}/ で出力する。"""
    me = case.get("slug", "")
    my_tags = set(case.get("tag_slugs") or [])
    my_cat = (case.get("tag_slugs") or ["other"])[0]

    scored = []
    for c in all_cases:
        if c.get("slug") == me:
            continue
        ctags = set(c.get("tag_slugs") or [])
        cat = (c.get("tag_slugs") or ["other"])[0]
        score = len(my_tags & ctags) * 10 + (1 if cat == my_cat else 0)
        scored.append((score, c))
    # スコア降順・同点は元の並び（API=新着順）を維持（Pythonのソートは安定）
    scored.sort(key=lambda x: -x[0])
    picks = [c for _, c in scored[:limit]]

    items = []
    for c in picks:
        slug = c.get("slug", "")
        company = c.get("company", "")
        summary = c.get("summary", "")
        image = c.get("image", "")
        cat_text = _cat_text(c.get("tags", []))
        img_html = (
            f'<img src="{image}" alt="{company}の採用成功事例"'
            f' width="724" height="543" loading="lazy" decoding="async">'
            if image else ""
        )
        items.append(
            f'\n          <li class="rx-rel__item">'
            f'\n            <a class="rx-rel__link" href="../{slug}/" aria-label="{company}の採用成功事例を見る">'
            f'\n              <figure class="rx-rel__media">{img_html}</figure>'
            f'\n              <div class="rx-rel__body">'
            f'\n                <p class="rx-rel__cat">{cat_text}</p>'
            f'\n                <h3 class="rx-rel__company">{company}</h3>'
            f'\n                <p class="rx-rel__desc">{summary}</p>'
            f'\n                <span class="rx-rel__more">詳しく見る{SVG_MORE}</span>'
            f'\n              </div>'
            f'\n            </a>'
            f'\n          </li>'
        )
    return "".join(items)


# ---- API fetching ----

# キャッシュバスター: 公開API(/contentsx/v1/cases)はNginx/CDNキャッシュ(max-age=300,
# s-maxage=600)が効くため、固定URLだと直前に公開した事例が反映されない。毎回ユニークな
# クエリを付けてキャッシュをすり抜け、常に最新の公開状態でビルドする。
_CB = str(int(time.time()))


def _fetch_json(url: str, timeout: int = 20) -> object:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_cases() -> list:
    url = f"{API_BASE}/cases?per_page=100&orderby=date&order=desc&_cb={_CB}"
    try:
        data = _fetch_json(url)
        if not isinstance(data, list):
            raise ValueError(f"Expected list, got {type(data)}")
        return data
    except Exception as e:
        print(f"[ERROR] API fetch failed: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_case_detail(case_id: int) -> Optional[dict]:
    url = f"{API_BASE}/cases/{case_id}?_cb={_CB}"
    try:
        data = _fetch_json(url)
        return data if isinstance(data, dict) else None
    except Exception as e:
        print(f"[WARN] Detail fetch failed for id={case_id}: {e}", file=sys.stderr)
        return None


# ---- HTML update ----

def update_case_html(cases: list) -> None:
    src = CASE_HTML.read_text(encoding="utf-8")
    cards_html = "".join(build_card(c) for c in cases)
    new_block = f"<!-- BUILD:CASE_GRID -->{cards_html}\n          <!-- /BUILD:CASE_GRID -->"
    result = re.sub(
        r"<!-- BUILD:CASE_GRID -->.*?<!-- /BUILD:CASE_GRID -->",
        new_block,
        src,
        flags=re.DOTALL,
    )
    if result == src:
        print("[WARN] BUILD markers not found in case.html — skipped", file=sys.stderr)
        return
    CASE_HTML.write_text(result, encoding="utf-8")
    print(f"[OK] case.html updated ({len(cases)} cards)")


# ---- Detail page generation ----

def _make_jsonld(detail: dict, page_url: str) -> tuple:
    company = detail.get("company", "")
    seo_title = detail.get("seo_title") or f"{company}の採用成功事例｜イチ推し採用"
    seo_desc = detail.get("seo_description") or detail.get("summary", "")
    image = detail.get("image", "")

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": seo_title,
        "description": seo_desc,
        "url": page_url,
        "publisher": {
            "@type": "Organization",
            "name": "イチ推し採用",
            "url": SITE_URL,
        },
    }
    if image:
        article["image"] = image

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "トップ", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "事例一覧",
             "item": f"{SITE_URL}/case.html"},
            {"@type": "ListItem", "position": 3, "name": company, "item": page_url},
        ],
    }
    return (
        json.dumps(article, ensure_ascii=False, indent=None),
        json.dumps(breadcrumb, ensure_ascii=False, indent=None),
    )


def _generate_one(case: dict, template: str, all_cases: list) -> str:
    slug = case.get("slug", "")
    detail = fetch_case_detail(case.get("id", 0))
    if detail is None:
        return f"[SKIP] {slug}: detail fetch failed"
    related_html = build_related(case, all_cases)

    company = detail.get("company", "")
    tags = detail.get("tags", [])
    image = detail.get("image", "")
    stats = detail.get("stats", [])
    content_html = sanitize_html(detail.get("content", ""))

    seo_title = detail.get("seo_title") or f"{company}の採用成功事例｜イチ推し採用"
    seo_desc = detail.get("seo_description") or detail.get("summary", "")
    page_url = f"{SITE_URL}/case/{slug}/"

    tags_display = " / ".join(tags)

    # stats for detail hero
    stats_items_html = ""
    for s in stats[:3]:
        n = _norm_stat(s)
        label = n["label"]
        value = n["value"]
        unit = n["unit"]
        arrow_svg = _arrow_svg(n["arrow"])
        label_html = f'<span class="rx-ccard__stat-label">{label}</span>' if label else ''
        stats_items_html += (
            f'<li>'
            f'{label_html}'
            f'<span class="rx-ccard__stat-value">'
            f'<span class="rx-ccard__stat-fig"><b class="rx-stat-num">{value}</b><small>{unit}</small></span>'
            f'{arrow_svg}'
            f'</span></li>\n              '
        )

    article_jsonld, breadcrumb_jsonld = _make_jsonld(detail, page_url)

    html = (
        template
        .replace("{{seo_title}}", seo_title)
        .replace("{{seo_description}}", seo_desc)
        .replace("{{company}}", company)
        .replace("{{slug}}", slug)
        .replace("{{tags_display}}", tags_display)
        .replace("{{image}}", image)
        .replace("{{image_alt}}", f"{company}の採用成功事例")
        .replace("{{stats_items}}", stats_items_html)
        .replace("{{content_html}}", content_html)
        .replace("{{page_url}}", page_url)
        .replace("{{article_jsonld}}", article_jsonld)
        .replace("{{breadcrumb_jsonld}}", breadcrumb_jsonld)
        .replace("{{related_cases}}", related_html)
    )

    out_dir = CASE_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    return f"[OK] /case/{slug}/"


def generate_details(cases: list) -> None:
    if not TEMPLATE_PATH.exists():
        print(f"[ERROR] Template not found: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    CASE_DIR.mkdir(exist_ok=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_generate_one, c, template, cases): c.get("slug") for c in cases}
        for f in as_completed(futures):
            print(f.result())


# ---- Sitemap ----

def update_sitemap(cases: list) -> None:
    if not SITEMAP_PATH.exists():
        print("[INFO] sitemap.xml not found — skipping sitemap update")
        return
    src = SITEMAP_PATH.read_text(encoding="utf-8")
    # 既存の /case/ エントリを削除
    cleaned = re.sub(
        r"\s*<url>\s*<loc>[^<]*/case/[^<]*</loc>.*?</url>",
        "",
        src,
        flags=re.DOTALL,
    )
    entries = "".join(
        f'\n  <url>'
        f'<loc>{SITE_URL}/case/{c.get("slug", "")}/</loc>'
        f'<changefreq>monthly</changefreq>'
        f'<priority>0.7</priority>'
        f'</url>'
        for c in cases
    )
    result = cleaned.replace("</urlset>", f"{entries}\n</urlset>")
    SITEMAP_PATH.write_text(result, encoding="utf-8")
    print(f"[OK] sitemap.xml updated ({len(cases)} case entries)")


# ---- Main ----

def main():
    print("=== build-cases.py ===")
    cases = fetch_cases()
    print(f"Fetched {len(cases)} cases from API")
    if not cases:
        print("[WARN] No cases returned — aborting")
        sys.exit(0)

    update_case_html(cases)
    generate_details(cases)
    update_sitemap(cases)
    print("=== Done ===")


if __name__ == "__main__":
    main()
