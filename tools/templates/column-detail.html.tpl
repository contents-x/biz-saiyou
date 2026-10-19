<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <link rel="icon" type="image/png" sizes="32x32" href="../../images/favicon/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="../../images/favicon/favicon-16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="../../images/favicon/apple-touch-icon.png">
  <title>{{seo_title}}</title>
  <meta name="description" content="{{seo_description}}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{{page_url}}">
  <!-- OGP -->
  <meta property="og:title" content="{{seo_title}}">
  <meta property="og:description" content="{{seo_description}}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{{page_url}}">
  <meta property="og:site_name" content="ビズ採用">
  <meta property="og:locale" content="ja_JP">
  {{og_image}}
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{seo_title}}">
  <meta name="twitter:description" content="{{seo_description}}">
  <!-- Structured Data -->
  <script type="application/ld+json">{{article_jsonld}}</script>
  <script type="application/ld+json">{{breadcrumb_jsonld}}</script>
  <!-- CSP -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://*.clarity.ms; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https:; object-src 'none'; base-uri 'self'; form-action 'self'">
  <!-- Google tag (gtag.js) — GA4 G-S2RDKPM1LE -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-S2RDKPM1LE"></script>
  <script src="../../js/ga4.js"></script>
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+Antique:wght@400;500;700&family=Inter:wght@500;700&display=swap">
  <link rel="stylesheet" href="../../css/tokens.css">
  <link rel="stylesheet" href="../../css/style.css">
  <link rel="stylesheet" href="../../css/column.css">
</head>
<body class="rx-jp-body">

  <!-- ===================== 共通ヘッダー（全ページ同一・ホーム基準で 2026-09-28 に統一）
       ロゴ画像＋タグライン＋メニュー3項目（サービス／料金プラン／コラム。事例は非表示）＋CTA2つ（無料診断／お問い合わせ）＋SPハンバーガー。
       スタイルは css/style.css の .rx-nav、開閉は js/main.js。共通コンポーネント化していないため、
       変更するときは全HTMLと tools/templates/*.tpl を同時に直す（テンプレを直さないと再生成で巻き戻る） ===================== -->
  <header class="rx-nav" id="nav">
    <div class="rx-nav__inner">
      <a class="rx-nav__brand" href="../../index.html" aria-label="ビズ採用 トップへ">
        <img class="rx-nav__logo" src="../../images/logo/biz-saiyo-logo.webp" alt="ビズ採用" width="540" height="191" decoding="async">
      </a>
      <p class="rx-nav__tag">好きがはたらく、をつくる。</p>
      <nav class="rx-nav__menu" id="navMenu" aria-label="メインナビゲーション">
        <a class="rx-nav__link" href="../../service.html">サービス</a>
        <a class="rx-nav__link" href="../../price.html">料金プラン</a>
        <a class="rx-nav__link" href="../../column.html" aria-current="true">コラム</a>
        <!-- 事例は 2026-09-28 から非表示（case.html 自体は残置。再表示時はここに <a> を戻す）。コラムは 2026-10-19 に再表示 -->
      </nav>
      <div class="rx-nav__ctas">
        <a class="rx-nav__cta rx-nav__cta--line" href="../../contact.html?source=free-diagnosis">無料診断を申し込む</a>
        <a class="rx-nav__cta rx-nav__cta--fill" href="../../contact.html">お問い合わせ</a>
      </div>
      <button class="rx-nav__hamburger" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="navMenu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <main>

    <article class="rx-cold">
      <div class="rx-cold__inner">
        <nav class="rx-cold__bread" aria-label="パンくず">
          <ol>
            <li><a href="../../">トップ</a></li>
            <li><a href="../../column.html">コラム</a></li>
            <li aria-current="page">{{title}}</li>
          </ol>
        </nav>

        <header class="rx-cold__head">
          <p class="rx-cold__meta">{{category}}<time class="rx-cold__date" datetime="{{date_ymd}}">{{date}}</time></p>
          <h1 class="rx-cold__title">{{title}}</h1>
        </header>

        <figure class="rx-cold__hero">{{hero_image}}</figure>

        <div class="rx-cold__body">
          {{content_html}}
        </div>
      </div>
    </article>

    <!-- 関連するコラム（他の記事が無いときは build-columns.py がこの枠ごと消す） -->
<!-- RELATED -->
    <section class="rx-colrel" aria-labelledby="relHeading">
      <div class="rx-colrel__inner">
        <h2 class="rx-colrel__heading" id="relHeading">関連するコラム</h2>
        <ul class="rx-colrel__grid">{{related}}</ul>
      </div>
    </section>
<!-- /RELATED -->

    <!-- CTA バナー（ホームの最後のCTA＝提案書 最終版 p26 と同じ文言・2026-10-19） -->
    <section class="rx-colcta" aria-labelledby="colCtaHeading">
      <div class="rx-colcta__inner rx-anim">
        <div class="rx-colcta__art" aria-hidden="true">
          <svg viewBox="0 0 200 140" fill="none" xmlns="http://www.w3.org/2000/svg" role="img">
            <rect x="14" y="34" width="172" height="78" rx="10" fill="#fff" stroke="#f7c6dd" stroke-width="2"/>
            <circle cx="62" cy="58" r="15" fill="#fbe0ec"/><rect x="44" y="76" width="36" height="26" rx="8" fill="#f7c6dd"/>
            <circle cx="132" cy="58" r="15" fill="#fbe0ec"/><rect x="114" y="76" width="36" height="26" rx="8" fill="#f7c6dd"/>
            <path d="M86 64h28M86 74h20" stroke="#ec2d87" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="rx-colcta__text">
          <h2 class="rx-colcta__heading" id="colCtaHeading">まずは、無料の採用力診断から。</h2>
          <p class="rx-colcta__lead">御社の仕事の中身や職場の空気が、候補者からどう見えているかをお伝えします。</p>
          <ul class="rx-colcta__points">
            <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 5"/></svg>採用課題の整理</li>
            <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 5"/></svg>既存施策の確認</li>
            <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 5"/></svg>候補者へ伝えるテーマの選定</li>
          </ul>
        </div>
        <div class="rx-colcta__action">
          <span class="rx-colcta__badge">診断は<b>無料</b></span>
          <a class="rx-colcta__btn" href="../../contact.html?source=free-consultation">無料相談はこちら<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10h14M11 4l6 6-6 6"/></svg></a>
          <p class="rx-colcta__note">相談内容に「採用力診断希望」とご記入ください</p>
        </div>
      </div>
    </section>

    <div class="rx-cold__back">
      <a href="../../column.html"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 10H3M9 16l-6-6 6-6"/></svg>コラム一覧へ戻る</a>
    </div>

  </main>

  <footer class="rx-footer" role="contentinfo">
    <div class="rx-footer__inner">
      <div class="rx-footer__top">
        <div class="rx-footer__brand">
          <a class="rx-footer__logo" href="../../index.html" aria-label="ビズ採用 トップへ">
            <span class="rx-footer__logo-text">ビズ採用</span>
          </a>
          <p class="rx-footer__tagline">求人広告に頼らない、SNS時代の採用へ。</p>
        </div>
        <nav class="rx-footer__nav" aria-label="フッターナビゲーション">
          <ul class="rx-footer__links">
            <li><a class="rx-footer__link" href="../../service.html">サービス</a></li>
            <li><a class="rx-footer__link" href="../../price.html">料金プラン</a></li>
            <li><a class="rx-footer__link" href="../../column.html">コラム</a></li>
            <li><a class="rx-footer__link" href="../../contact.html">お問い合わせ</a></li>
            <li><a class="rx-footer__link" href="../../company.html">会社概要</a></li>
            <li><a class="rx-footer__link" href="../../privacy.html">プライバシーポリシー</a></li>
          </ul>
        </nav>
      </div>
      <div class="rx-footer__bottom">
        <div class="rx-footer__company">
          <p class="rx-footer__company-service">ビズ採用</p>
          <p class="rx-footer__company-name">運営：コンテンツエックス株式会社 ／ Contents X Co., Ltd.</p>
        </div>
        <p class="rx-footer__copyright"><small>&#169; 2026 Contents X Co., Ltd.</small></p>
      </div>
    </div>
  </footer>

  <script src="../../js/main.js" defer></script>

</body>
</html>
