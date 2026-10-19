#!/usr/bin/env python3
"""
tools/build-columns.py  —  ビズ採用 (recruitx) コラムビルダー
共有コラム cx_column の掲載先=recruitx（/contentsx/v1/columns?site=recruitx）を取得し:
  1. column.html の新着 / 検索キーワード / PICK UP / カテゴリタブ / カード一覧を更新（BUILD markers 間を差し替え）
  2. /column/{slug}/index.html を静的生成（WP で非公開にした記事のページは削除）
  3. sitemap.xml の /column/ エントリを更新（存在する場合）

GitHub Actions（.github/workflows/build-columns.yml）が1時間ごとに実行し、差分があれば main に push する。
全記事の本文が取れたときだけファイルを書き換える（途中で失敗したら何も書かずに exit 1）。

⚠️ 公開コラムが 0 件のときは column.html を今のまま保持して終了する
   （WP の一時的な不調で一覧が空になっても、公開中のページを消さない）。
"""
import html as _html
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
COLUMN_HTML = ROOT / "column.html"
COLUMN_DIR = ROOT / "column"
TEMPLATE_PATH = ROOT / "tools" / "templates" / "column-detail.html.tpl"
SITEMAP_PATH = ROOT / "sitemap.xml"

SITE_URL = "https://ichioshi.contentsx.jp"
API_BASE = "https://cms.contentsx.jp/wp-json/contentsx/v1"
USER_AGENT = "recruitx-build-columns/1.0 (+https://ichioshi.contentsx.jp/)"

# slug はそのままフォルダ名・URL になるため英数字とハイフン・アンダースコアだけ受け付ける
SLUG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")

# ヒーローの「よく検索されるキーワード」候補（表示名, 検索語）。
# 検索語がどの記事にも当たらない候補は出さない（押して0件になるボタンを置かない）。
SEARCH_TAGS = [
    ("応募が来ない", "応募"),
    ("広告費が高い", "費用"),
    ("SNSを始めたい", "SNS"),
    ("採用LPを改善したい", "採用LP"),
    ("求人広告を見直したい", "求人広告"),
]

# ---- XSS sanitizer (allowlist-based HTMLParser、build-cases.py と同方針) ----
ALLOWED_TAGS = {
    "p", "br", "strong", "em", "b", "i", "u", "s", "del", "mark",
    "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "figcaption", "blockquote", "cite", "dl", "dt", "dd",
    "small", "sup", "sub", "hr",
}
ALLOWED_ATTRS = {
    "a": {"href", "title", "rel"},
    "img": {"src", "alt", "width", "height", "loading", "decoding"},
    "th": {"scope"},
    "td": {"colspan", "rowspan"},
}
VOID_TAGS = {"br", "img", "hr"}


class _Sanitizer(HTMLParser):
    """許可タグ・属性だけを残す。dead_hrefs に入っているリンクは <a> を外して文字だけ残す。
    表は <div class="rx-cold__table"> で包み、本体の各セルに見出し行の列名を data-label で持たせる
    （スマホでは行ごとのカードに組み替えて列名を添える。多列の表を横スクロールで逃がさない → BUGS.md 2026-09-28）。"""

    def __init__(self, dead_hrefs: frozenset = frozenset()):
        super().__init__(convert_charrefs=False)
        self.out: list = []
        self.dead_hrefs = dead_hrefs
        self._a_kept: list = []  # <a> ごとに出力したかどうか（閉じタグの対応用）
        self._in_thead = False
        self._th_buf: Optional[list] = None  # 見出し行の <th> の文字を集める
        self._labels: list = []              # 見出し行の列名
        self._col = 0                        # 本体の行で今いる列

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            return
        if tag == "a":
            href = dict(attrs).get("href") or ""
            keep = href not in self.dead_hrefs
            self._a_kept.append(keep)
            if not keep:
                return
        label = ""
        if tag == "table":
            self._labels = []
        elif tag == "thead":
            self._in_thead = True
        elif tag == "tr" and not self._in_thead:
            self._col = 0
        elif tag == "th" and self._in_thead:
            self._th_buf = []
        elif tag in ("td", "th") and self._labels:
            if self._col < len(self._labels):
                label = self._labels[self._col]
            span = dict(attrs).get("colspan") or "1"
            self._col += int(span) if span.isdigit() else 1
        allowed = ALLOWED_ATTRS.get(tag, set())
        safe = ""
        for name, val in attrs:
            if name not in allowed:
                continue
            val = (val or "").replace('"', "&quot;")
            if name == "href" and not re.match(r"^(https?://|/|#)", val):
                continue
            if name == "src" and not re.match(r"^https?://", val):
                continue
            safe += f' {name}="{val}"'
        if label:
            safe += f' data-label="{esc(label)}"'
        if tag == "table":
            self.out.append('<div class="rx-cold__table">')
        self.out.append(f"<{tag}{safe}>")

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        if tag == "a" and self._a_kept and not self._a_kept.pop():
            return
        if tag == "th" and self._th_buf is not None:
            self._labels.append(re.sub(r"\s+", " ", "".join(self._th_buf)).strip())
            self._th_buf = None
        elif tag == "thead":
            self._in_thead = False
        self.out.append(f"</{tag}>")
        if tag == "table":
            self.out.append("</div>")

    def handle_data(self, data):
        if self._th_buf is not None:
            self._th_buf.append(data)
        self.out.append(data.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def handle_entityref(self, name):
        if self._th_buf is not None:
            self._th_buf.append(_html.unescape(f"&{name};"))
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        if self._th_buf is not None:
            self._th_buf.append(_html.unescape(f"&#{name};"))
        self.out.append(f"&#{name};")


def sanitize_html(raw: str, dead_hrefs: frozenset = frozenset()) -> str:
    s = _Sanitizer(dead_hrefs)
    s.feed(raw or "")
    out = "".join(s.out)
    # WP のブロックエディタが残す空段落（<p></p>）は余白になるだけなので消す
    return re.sub(r"<p>(?:\s|&nbsp;|<br>)*</p>", "", out)


def _truthy(v) -> bool:
    """WP APIは真偽値を文字列 "True"/"False" で返すため、文字列も正しく判定する。
    素の bool() だと "False" が真になり PICK UP 指定が効かなくなる。"""
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(v)


def esc(s: str) -> str:
    """属性・テキスト用の最小エスケープ。"""
    return _html.escape(str(s or ""), quote=True)


def _normalize(s: str) -> str:
    """js/column.js の normalize() と同じ（小文字化＋空白除去）。検索キーワードの当たり判定に使う。"""
    return re.sub(r"\s+", "", (s or "").lower())


# ---- SVG helpers ----
SVG_CAL = (
    '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"'
    ' aria-hidden="true"><rect x="2.5" y="3.5" width="11" height="10" rx="1.5"/>'
    '<path d="M2.5 6.5h11M5.5 2v3M10.5 2v3" stroke-linecap="round"/></svg>'
)
SVG_ARROW = (
    '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round"><path d="M6 3l5 5-5 5"/></svg>'
)
SVG_TAG = (
    '<svg class="rx-colsearch__tagic" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
    '<circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3"/>'
    '<path d="M5.2 8.2l1.9 1.9 3.7-3.9" stroke="currentColor" stroke-width="1.5"'
    ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


# ---- API ----
_CB = str(int(time.time()))


def _fetch_json(url: str, timeout: int = 20) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _norm(c: dict) -> dict:
    """共有コラム(cx_column)のフィールド名をrecruitXフロントの内部名へ写像。
    title_ja→title / excerpt_ja→excerpt（他キー: category/thumbnail/date/slug/id/
    pickup/seo_title/seo_description/content はそのまま使える）。"""
    if not isinstance(c, dict):
        return c
    c = dict(c)
    c["title"] = c.get("title_ja", "") or c.get("title", "")
    c["excerpt"] = c.get("excerpt_ja", "") or c.get("excerpt", "")
    return c


def fetch_columns() -> list:
    # 共有コラムから掲載先=recruitx のみ取得（cx_column 相乗り）
    url = f"{API_BASE}/columns?site=recruitx&per_page=100&_cb={_CB}"
    try:
        data = _fetch_json(url)
        if not isinstance(data, list):
            raise ValueError(f"Expected list, got {type(data)}")
    except Exception as e:
        print(f"[ERROR] API fetch failed: {e}", file=sys.stderr)
        sys.exit(1)
    columns = []
    for c in (_norm(c) for c in data):
        slug = str(c.get("slug", ""))
        if not SLUG_RE.fullmatch(slug):
            # 日本語スラッグ等はフォルダ名にできないので載せない（WP でスラッグを英数字にすれば次回から載る）
            print(f"::warning::slug が英数字ではないため掲載を見送り: id={c.get('id')} slug={slug!r}"
                  f" title={c.get('title','')!r}")
            continue
        columns.append(c)
    return columns


def fetch_column_detail(col_id) -> Optional[dict]:
    url = f"{API_BASE}/columns/{col_id}?_cb={_CB}"
    try:
        data = _fetch_json(url)
        return _norm(data) if isinstance(data, dict) else None
    except Exception as e:
        print(f"[ERROR] Detail fetch failed for id={col_id}: {e}", file=sys.stderr)
        return None


# ---- 本文リンクの行き先確認 ----
_LINK_CACHE: dict = {}


def _external_link_is_dead(url: str) -> bool:
    """404 / 410 が返るリンクだけ「行き先なし」とみなす。
    タイムアウトや 5xx などの一時的な失敗ではリンクを外さない（たまたま落ちていただけで消さない）。"""
    if url in _LINK_CACHE:
        return _LINK_CACHE[url]
    dead = False
    try:
        quoted = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~")
        req = urllib.request.Request(quoted, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15):
            pass
    except urllib.error.HTTPError as e:
        dead = e.code in (404, 410)
    except Exception:
        dead = False
    _LINK_CACHE[url] = dead
    return dead


def _own_link_is_dead(url: str, slugs: set) -> bool:
    """自サイト（ichioshi.contentsx.jp）へのリンクは、今回のビルドで作るページか、リポにあるファイルなら生きている。
    （同じビルドで公開する別記事へのリンクは本番にまだ無いので、HTTP で確かめると誤って外してしまう）"""
    path = urllib.parse.urlsplit(url).path.lstrip("/")
    m = re.fullmatch(r"column/([^/]+)/?(?:index\.html)?", path)
    if m:
        return m.group(1) not in slugs
    target = ROOT / urllib.parse.unquote(path)
    return not (target.is_file() or (target / "index.html").is_file())


def find_dead_links(raw_html: str, slugs: set) -> frozenset:
    """本文の <a href> のうち行き先が無いものを返す（HTMLParser と同じくエスケープ解除した表記で返す）。"""
    dead = set()
    for href in {_html.unescape(h) for h in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', raw_html or "")}:
        if href.startswith(SITE_URL):
            if _own_link_is_dead(href, slugs):
                dead.add(href)
        elif re.match(r"^https?://", href):
            if _external_link_is_dead(href):
                dead.add(href)
    return frozenset(dead)


# ---- 一覧ページの部品 ----
def _media_html(thumb: str, alt: str, cls: str) -> str:
    if thumb:
        cls_attr = f' class="{cls}"' if cls else ""
        return (f'<img{cls_attr} src="{esc(thumb)}" alt="{esc(alt)}"'
                f' loading="lazy" decoding="async">')
    return ""  # 画像未設定はCSSのプレースホルダ背景に任せる


def _categories(columns: list) -> list:
    # 出現順を保ちつつ重複排除（API=新着順）
    cats = []
    for c in columns:
        cat = c.get("category") or ""
        if cat and cat not in cats:
            cats.append(cat)
    return cats


def build_featured(columns: list) -> str:
    """ヒーロー右の新着 = 最新の公開3件。件数で並べ方を変える（rx-colfeat--n1〜n3）。"""
    picks = columns[:3]
    items = []
    for c in picks:
        slug = c.get("slug", "")
        badge = c.get("category") or "新着"
        media = _media_html(c.get("thumbnail", ""), "", "")
        ph = "" if c.get("thumbnail") else " is-placeholder"
        items.append(
            f'              <li class="rx-colfeat__item{ph}">\n'
            f'                <a class="rx-colfeat__link" href="column/{esc(slug)}/">\n'
            f'                  <div class="rx-colfeat__text">\n'
            f'                    <span class="rx-colfeat__badge">{esc(badge)}</span>\n'
            f'                    <p class="rx-colfeat__title">{esc(c.get("title",""))}</p>\n'
            f'                    <span class="rx-colfeat__date">{esc(c.get("date",""))}</span>\n'
            f'                  </div>\n'
            f'                  <figure class="rx-colfeat__media">{media}</figure>\n'
            f'                </a>\n'
            f'              </li>'
        )
    return (
        f'          <div class="rx-colhero__featured">\n'
        f'            <ul class="rx-colfeat rx-colfeat--n{len(picks)}" aria-label="新着コラム">\n'
        + "\n".join(items) + "\n"
        f'            </ul>\n'
        f'          </div>'
    )


def build_search_tags(columns: list) -> str:
    haystack = [_normalize(f'{c.get("title","")}{c.get("excerpt","")}{c.get("category") or ""}') for c in columns]
    tags = [(label, q) for label, q in SEARCH_TAGS if any(_normalize(q) in h for h in haystack)]
    if not tags:
        return ""
    lis = "\n".join(
        f'            <li><button type="button" class="rx-colsearch__tag" data-query="{esc(q)}">{SVG_TAG}{esc(label)}</button></li>'
        for label, q in tags
    )
    return (
        '          <ul class="rx-colsearch__tags" aria-label="よく検索されるキーワード">\n'
        f'{lis}\n'
        '          </ul>'
    )


def build_tabs(columns: list) -> str:
    cats = _categories(columns)
    if len(cats) < 2:
        return ""  # 「すべて」しか無いタブは出さない
    out = ['          <button type="button" class="rx-collist__filter-btn" data-filter="all" aria-pressed="true">すべて</button>']
    for cat in cats:
        out.append(
            f'          <button type="button" class="rx-collist__filter-btn"'
            f' data-filter="{esc(cat)}" aria-pressed="false">{esc(cat)}</button>'
        )
    return (
        '        <div class="rx-collist__filter" role="group" aria-label="カテゴリで絞り込み" data-column-filter>\n'
        + "\n".join(out) + "\n"
        '        </div>'
    )


def build_pickup(columns: list) -> str:
    """WP で「ピックアップ」にした記事があるときだけ PICK UP 枠を出す（無指定なら枠ごと出さない）。"""
    pick = next((c for c in columns if _truthy(c.get("pickup"))), None)
    if pick is None:
        return ""
    slug = pick.get("slug", "")
    cat = pick.get("category") or ""
    cat_html = f'<span class="rx-pickup__cat">{esc(cat)}</span>' if cat else ""
    media = _media_html(pick.get("thumbnail", ""), pick.get("title", ""), "rx-pickup__media")
    if not media:
        media = '<span class="rx-pickup__media" aria-hidden="true"></span>'
    ph = "" if pick.get("thumbnail") else " is-placeholder"
    return (
        f'    <section class="rx-pickup" aria-labelledby="pickupHeading">\n'
        f'      <div class="rx-pickup__inner">\n'
        f'        <p class="rx-pickup__label" id="pickupHeading">PICK UP</p>\n'
        f'        <div class="rx-pickup__body">\n'
        f'          <a class="rx-pickup__card{ph}" href="column/{esc(slug)}/">\n'
        f'            {media}\n'
        f'            <span class="rx-pickup__content">\n'
        f'              {cat_html}\n'
        f'              <span class="rx-pickup__title">{esc(pick.get("title",""))}</span>\n'
        f'              <span class="rx-pickup__desc">{esc(pick.get("excerpt",""))}</span>\n'
        f'              <span class="rx-pickup__date">{esc(pick.get("date",""))}</span>\n'
        f'            </span>\n'
        f'          </a>\n'
        f'        </div>\n'
        f'      </div>\n'
        f'    </section>'
    )


def build_card(c: dict, href_prefix: str = "column/", anim: bool = True, indent: str = "          ") -> str:
    """画像左・テキスト右の横型カード（バッジ→タイトル→説明→日付/矢印）。一覧と関連コラムで共用。"""
    slug = c.get("slug", "")
    cat = c.get("category") or ""
    title = c.get("title", "")
    desc = c.get("excerpt", "")
    media = _media_html(c.get("thumbnail", ""), title, "")  # img は figure 内、class無し
    cat_badge = f'<span class="rx-colcard__cat">{esc(cat)}</span>' if cat else ""
    desc_html = f'<p class="rx-colcard__desc">{esc(desc)}</p>' if desc else ""
    cls = "rx-colcard" + (" rx-anim" if anim else "") + ("" if c.get("thumbnail") else " is-placeholder")
    i = indent
    return (
        f'\n{i}<li class="{cls}" data-category="{esc(cat)}" data-title="{esc(title)}" data-desc="{esc(desc)}">'
        f'\n{i}  <a class="rx-colcard__link" href="{href_prefix}{esc(slug)}/">'
        f'\n{i}    <figure class="rx-colcard__media">{media}</figure>'
        f'\n{i}    <div class="rx-colcard__body">'
        f'\n{i}      {cat_badge}'
        f'\n{i}      <h3 class="rx-colcard__title">{esc(title)}</h3>'
        f'\n{i}      {desc_html}'
        f'\n{i}      <div class="rx-colcard__foot">'
        f'\n{i}        <span class="rx-colcard__date">{SVG_CAL}{esc(c.get("date",""))}</span>'
        f'\n{i}        <span class="rx-colcard__arrow" aria-hidden="true">{SVG_ARROW}</span>'
        f'\n{i}      </div>'
        f'\n{i}    </div>'
        f'\n{i}  </a>'
        f'\n{i}</li>'
    )


def _replace_block(src: str, marker: str, inner: str) -> str:
    pat = re.compile(rf"<!-- BUILD:{marker} -->.*?<!-- /BUILD:{marker} -->", re.DOTALL)
    body = f"\n{inner}\n" if inner else "\n"
    repl = f"<!-- BUILD:{marker} -->{body}<!-- /BUILD:{marker} -->"
    new, n = pat.subn(lambda _m: repl, src)
    if n == 0:
        print(f"[WARN] BUILD:{marker} markers not found — skipped", file=sys.stderr)
    return new


def render_column_html(columns: list) -> str:
    src = COLUMN_HTML.read_text(encoding="utf-8")
    src = _replace_block(src, "COLUMN_FEATURED", build_featured(columns))
    src = _replace_block(src, "COLUMN_SEARCH_TAGS", build_search_tags(columns))
    src = _replace_block(src, "COLUMN_PICKUP", build_pickup(columns))
    src = _replace_block(src, "COLUMN_TABS", build_tabs(columns))
    src = _replace_block(src, "COLUMN_GRID", "".join(build_card(c) for c in columns).lstrip("\n"))
    return src


# ---- 詳細ページ生成 ----
def _make_jsonld(d: dict, page_url: str) -> tuple:
    title = d.get("title", "")
    seo_title = d.get("seo_title") or f"{title}｜ビズ採用 コラム"
    seo_desc = d.get("seo_description") or d.get("excerpt", "")
    image = d.get("thumbnail", "")
    article = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": seo_title, "description": seo_desc, "url": page_url,
        "datePublished": d.get("date_ymd", ""),
        "dateModified": d.get("modified_ymd", "") or d.get("date_ymd", ""),
        "publisher": {"@type": "Organization", "name": "ビズ採用", "url": SITE_URL},
    }
    if image:
        article["image"] = image
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "トップ", "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": "コラム", "item": f"{SITE_URL}/column.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
        ],
    }
    # </script> で JSON-LD の外に出られないよう "<" をエスケープ
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("<", "\\u003c")
    return (dump(article), dump(breadcrumb))


def build_related(me: dict, all_cols: list, limit: int = 3) -> str:
    my_cat = me.get("category") or ""
    others = [c for c in all_cols if c.get("slug") != me.get("slug")]
    picks = [c for c in others if my_cat and (c.get("category") or "") == my_cat]
    picks += [c for c in others if c not in picks]
    return "".join(build_card(c, href_prefix="../", anim=False, indent="            ") for c in picks[:limit])


def render_detail(c: dict, detail: dict, template: str, all_cols: list, slugs: set) -> str:
    slug = c.get("slug", "")
    title = detail.get("title", "")
    cat = detail.get("category") or ""
    image = detail.get("thumbnail", "")
    raw = detail.get("content", "")
    dead = find_dead_links(raw, slugs)
    for h in sorted(dead):
        print(f"[INFO] {slug}: 行き先が無いリンクを外しました → {h}")
    content_html = sanitize_html(raw, dead)
    seo_title = detail.get("seo_title") or f"{title}｜ビズ採用 コラム"
    seo_desc = detail.get("seo_description") or detail.get("excerpt", "")
    page_url = f"{SITE_URL}/column/{slug}/"
    article_jsonld, breadcrumb_jsonld = _make_jsonld(detail, page_url)

    hero_img = (
        f'<img class="rx-cold__hero-img" src="{esc(image)}" alt="{esc(title)}"'
        f' width="1200" height="630" loading="eager" fetchpriority="high" decoding="async">'
        if image else ""
    )
    # SNS のクローラ向けに日本語ファイル名は URL エンコードしておく
    image_url = urllib.parse.quote(image, safe=":/?#[]@!$&'()*+,;=%~") if image else ""
    og_image = (
        f'<meta property="og:image" content="{esc(image_url)}">\n'
        f'  <meta name="twitter:image" content="{esc(image_url)}">'
        if image else ""
    )
    cat_html = f'<span class="rx-cold__cat">{esc(cat)}</span>' if cat else ""

    related = build_related(c, all_cols)
    tpl = template
    if related:
        tpl = tpl.replace("<!-- RELATED -->\n", "").replace("<!-- /RELATED -->\n", "")
    else:
        # 他に記事が無いときは「関連するコラム」の枠ごと出さない
        tpl = re.sub(r"\s*<!-- 関連するコラム[^\n]*-->\n<!-- RELATED -->.*?<!-- /RELATED -->\n", "\n", tpl, flags=re.DOTALL)

    return (
        tpl
        .replace("{{seo_title}}", esc(seo_title))
        .replace("{{seo_description}}", esc(seo_desc))
        .replace("{{og_image}}", og_image)
        .replace("{{title}}", esc(title))
        .replace("{{slug}}", esc(slug))
        .replace("{{category}}", cat_html)
        .replace("{{date}}", esc(detail.get("date", "")))
        .replace("{{date_ymd}}", esc(detail.get("date_ymd", "")))
        .replace("{{modified_ymd}}", esc(detail.get("modified_ymd", "") or detail.get("date_ymd", "")))
        .replace("{{hero_image}}", hero_img)
        .replace("{{content_html}}", content_html)
        .replace("{{page_url}}", page_url)
        .replace("{{article_jsonld}}", article_jsonld)
        .replace("{{breadcrumb_jsonld}}", breadcrumb_jsonld)
        .replace("{{related}}", related)
    )


def render_details(columns: list) -> dict:
    """全記事の本文を取得して詳細ページを組み立てる。1件でも失敗したら exit 1（一部だけ更新しない）。"""
    if not TEMPLATE_PATH.exists():
        print(f"[ERROR] Template not found: {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    slugs = {c.get("slug", "") for c in columns}

    def work(c):
        detail = fetch_column_detail(c.get("id", 0))
        if detail is None:
            return c.get("slug", ""), None
        return c.get("slug", ""), render_detail(c, detail, template, columns, slugs)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(pool.map(work, columns))
    failed = [s for s, html in results.items() if html is None]
    if failed:
        print(f"[ERROR] 本文を取得できなかった記事があるため、何も書き換えずに終了します: {failed}", file=sys.stderr)
        sys.exit(1)
    return results


def write_details(pages: dict) -> None:
    COLUMN_DIR.mkdir(exist_ok=True)
    for slug, html in pages.items():
        out_dir = COLUMN_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"[OK] /column/{slug}/")
    # WP で非公開・削除した記事のページを消す（ビルドが作ったフォルダ＝index.html だけのものに限る）
    for d in sorted(COLUMN_DIR.iterdir()):
        if d.is_dir() and d.name not in pages and [p.name for p in d.iterdir()] == ["index.html"]:
            shutil.rmtree(d)
            print(f"[OK] /column/{d.name}/ を削除（WP で非公開）")


def update_sitemap(columns: list) -> None:
    if not SITEMAP_PATH.exists():
        print("[INFO] sitemap.xml not found — skipping")
        return
    src = SITEMAP_PATH.read_text(encoding="utf-8")
    cleaned = re.sub(r"\s*<url>\s*<loc>[^<]*/column/[^<]*</loc>.*?</url>", "", src, flags=re.DOTALL)
    entries = ""
    for c in columns:
        lastmod = c.get("modified_ymd", "")
        lm = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        entries += (
            f'\n  <url><loc>{SITE_URL}/column/{c.get("slug","")}/</loc>'
            f'{lm}<changefreq>monthly</changefreq><priority>0.6</priority></url>'
        )
    result = cleaned.replace("</urlset>", f"{entries}\n</urlset>")
    SITEMAP_PATH.write_text(result, encoding="utf-8")
    print(f"[OK] sitemap.xml updated ({len(columns)} column entries)")


def main():
    print("=== build-columns.py ===")
    columns = fetch_columns()
    print(f"Fetched {len(columns)} columns from API")
    if not columns:
        print("[WARN] 公開コラムが0件です。column.html を今のまま保持して終了します。")
        print("       WP管理画面でコラムを公開してから再実行してください。")
        sys.exit(0)
    # 先に全部組み立て、全記事そろってから書き込む
    pages = render_details(columns)
    list_html = render_column_html(columns)
    COLUMN_HTML.write_text(list_html, encoding="utf-8")
    print(f"[OK] column.html updated ({len(columns)} cards)")
    write_details(pages)
    update_sitemap(columns)
    print("=== Done ===")


if __name__ == "__main__":
    main()
