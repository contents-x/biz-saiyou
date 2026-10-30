/* =========================================================================
   main.js — イチ推し採用 全ページ共通
   - CTA アンカーのスムーススクロール（scroll-margin-top は CSS §13 で担保）
   - IntersectionObserver による軽い入場アニメ（.rx-anim → .is-in）
   - ヘッダーナビ（スクロール背景 / ハンバーガー / Escで閉じる）
   - ホームのヒーロー: 採用アニメーション・会社紹介動画の埋め込み動画（再生ボタン・同時再生の抑止・縦長再生時の幅の入れ替え）
   - 固定CTA（画面下の2ボタンバー: 電話で相談／無料で相談。<body data-fixcta="off"> で非表示）
   - お問い合わせ → HubSpot Forms API v3 直送（XSS安全: createElement + textContent）
   - prefers-reduced-motion: reduce のときはアニメをスキップ
   ========================================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- CTA / ページ内アンカーのスムーススクロール ---- */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a[href^="#"]');
    if (!link) return;
    var id = link.getAttribute('href').slice(1);
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({
      behavior: reduceMotion ? 'auto' : 'smooth',
      block: 'start'
    });
  });

  /* ---- 入場アニメ ---- */
  function revealAll() {
    var els = document.querySelectorAll('.rx-anim');
    for (var i = 0; i < els.length; i++) els[i].classList.add('is-in');
  }

  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealAll();
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

  function init() {
    var els = document.querySelectorAll('.rx-anim');
    for (var i = 0; i < els.length; i++) io.observe(els[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* ホームのヒーロー: 採用アニメーション（動画2本）・会社紹介動画（1本）
   再生ボタンは JS が動く環境でだけ出し、押すと再生、再生中は消す。どれかを再生したら他は止める。
   縦長を再生したらその入れ物に .is-tall-active（固定エリアの中で右の縦長が広がり左の横長が縮む）、横長を再生したら戻す */
(function () {
  'use strict';

  var wraps = document.querySelectorAll('.rx-home-hero__video');
  if (!wraps.length) return;
  var videos = [];
  Array.prototype.forEach.call(wraps, function (wrap) {
    var v = wrap.querySelector('video');
    var btn = wrap.querySelector('.rx-home-hero__video-play');
    var box = wrap.closest('.rx-home-hero__videos--pair');
    if (!v) return;
    videos.push(v);
    wrap.classList.add('has-js');
    if (btn) btn.addEventListener('click', function () { v.play(); });
    v.addEventListener('play', function () {
      wrap.classList.add('is-playing');
      if (box) box.classList.toggle('is-tall-active', wrap.classList.contains('rx-home-hero__video--tall'));
      videos.forEach(function (o) { if (o !== v && !o.paused) o.pause(); });
    });
    v.addEventListener('pause', function () { wrap.classList.remove('is-playing'); });
    v.addEventListener('ended', function () { wrap.classList.remove('is-playing'); });
  });
})();

/* ヘッダーナビ: スクロールで背景を白くする + SPハンバーガー開閉 */
(function () {
  'use strict';

  var nav = document.getElementById('nav');
  if (!nav) return;
  var menu = nav.querySelector('.rx-nav__menu');
  var ham  = nav.querySelector('.rx-nav__hamburger');

  function onScroll() {
    if (window.scrollY > 16) nav.classList.add('is-scrolled');
    else nav.classList.remove('is-scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (ham && menu) {
    var setOpen = function (open) {
      menu.classList.toggle('is-open', open);
      ham.setAttribute('aria-expanded', open ? 'true' : 'false');
      ham.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
      document.body.style.overflow = open ? 'hidden' : '';
    };
    ham.addEventListener('click', function () {
      setOpen(!menu.classList.contains('is-open'));
    });
    // メニュー内リンクを押したら閉じる
    menu.addEventListener('click', function (e) {
      if (e.target.closest('.rx-nav__link') && menu.classList.contains('is-open')) setOpen(false);
    });
    // Escキーで閉じる（アクセシビリティ）
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) {
        setOpen(false);
        ham.focus();
      }
    });
  }
})();

/* 固定CTA（画面下に追従するバー・全ページ共通）
   - 「電話で相談」「無料で相談」の2ボタン。PCは中央寄せの帯、SPは全幅（資料ダウンロードは 2026-09-29 に取りやめ）
   - お問い合わせページ（#rx-contact-form あり）では出さない。<body data-fixcta="off"> でも出さない
   - DOM生成のみ（innerHTML不使用・ユーザー入力なし）
   - 遷移先は同階層相対パス。case/{slug}/ 等のサブディレクトリでは main.js の src（../../js/main.js）から
     ルートまでの相対プレフィックスを求めて付ける（ルート絶対パス禁止・CLAUDE.md）
   - バーの実高さを --rx-fixcta-h に書き、body の下余白でフッターが隠れないようにする */
(function () {
  'use strict';

  if (document.body.getAttribute('data-fixcta') === 'off') return; // ページ側で無効化
  if (document.getElementById('rx-contact-form')) return; // お問い合わせページ自身では出さない
  if (document.querySelector('.rx-fixcta')) return;       // 二重挿入ガード

  // ルートまでの相対プレフィックス（"" or "../../"）を main.js の src から求める
  var base = '';
  var scripts = document.querySelectorAll('script[src]');
  for (var i = 0; i < scripts.length; i++) {
    var m = /^(.*?)js\/main\.js(?:\?.*)?$/.exec(scripts[i].getAttribute('src'));
    if (m) { base = m[1]; break; }
  }

  var TEL_NUMBER   = '03-6261-0764';
  var TEL_HREF     = 'tel:0362610764';
  var CONSULT_HREF = base + 'contact.html?source=free-consultation';

  var SVGNS = 'http://www.w3.org/2000/svg';
  function svgEl(name, attrs) {
    var el = document.createElementNS(SVGNS, name);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function icon(paths) {
    var svg = svgEl('svg', {
      'class': 'rx-fixcta__icon', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor',
      'stroke-width': '1.9', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': 'true'
    });
    for (var i = 0; i < paths.length; i++) svg.appendChild(svgEl('path', { d: paths[i] }));
    return svg;
  }
  function item(mod, href, paths, label, sub, ariaLabel) {
    var a = document.createElement('a');
    a.className = 'rx-fixcta__item rx-fixcta__item--' + mod;
    a.href = href;
    if (ariaLabel) a.setAttribute('aria-label', ariaLabel);
    a.appendChild(icon(paths));
    var body = document.createElement('span');
    body.className = 'rx-fixcta__body';
    var t = document.createElement('span');
    t.className = 'rx-fixcta__label';
    t.textContent = label;
    body.appendChild(t);
    if (sub) {
      var s = document.createElement('span');
      s.className = 'rx-fixcta__sub';
      s.textContent = sub;
      body.appendChild(s);
    }
    a.appendChild(body);
    return a;
  }

  var bar = document.createElement('nav');
  bar.className = 'rx-fixcta';
  bar.setAttribute('aria-label', 'ご相談');

  var inner = document.createElement('div');
  inner.className = 'rx-fixcta__inner';

  inner.appendChild(item('tel', TEL_HREF,
    ['M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2Z'],
    '電話で相談', TEL_NUMBER, '電話で相談 ' + TEL_NUMBER + '（受付 平日10:00〜19:00）'));
  inner.appendChild(item('consult', CONSULT_HREF,
    ['M4 5h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H8l-4 3V6a1 1 0 0 1 1-1Z', 'M8 10h8', 'M8 14h5'],
    '無料で相談', 'フォームから受付'));

  bar.appendChild(inner);
  document.body.appendChild(bar);
  document.body.classList.add('has-fixcta');

  // バーの高さを CSS 変数へ（body の下余白に使う）。リサイズ時も追従
  function setHeight() {
    document.documentElement.style.setProperty('--rx-fixcta-h', bar.offsetHeight + 'px');
  }
  setHeight();
  window.addEventListener('resize', setHeight, { passive: true });

  // 常時表示（最上部でも・上にスクロールしても消えない）。入場アニメだけ一度再生
  window.requestAnimationFrame(function () { bar.classList.add('is-visible'); });
})();

/* お問い合わせ → HubSpot Forms API v3 直送（XSS安全: createElement + textContent）
   - 入力はtrim + 文字数上限でサニタイズ
   - honeypot（bot対策）: 隠しフィールドが埋まっていたら送信せず成功表示
   - URLパラメータは長さ制限してからトラッキング情報に使用 */
(function () {
  'use strict';

  var HUBSPOT_PORTAL_ID = '48367061';
  var HUBSPOT_FORM_GUID = 'b6da14d0-d60d-4357-89fc-0015ed32b704';
  var SERVICE_NAME      = 'ビズ採用';   // HubSpot へ送るサービス名（2026-09-28 リクルートX から変更。2026-10-31 のイチ推し採用への改名では HubSpot 側の確認待ちのため据え置き。CRM は公開キーで送信元を判別するので送らない）

  var form = document.getElementById('rx-contact-form');
  if (!form) return;
  var PARAMS = new URLSearchParams(window.location.search);

  // 入力上限（HubSpot側と運用に合わせた安全値）
  var LIMITS = { company: 200, department: 100, fullName: 100, email: 254, message: 4000 };

  function readField(fd, name) {
    return String(fd.get(name) || '').trim().slice(0, LIMITS[name] || 200);
  }

  function readParam(key) {
    var v = PARAMS.get(key);
    return v ? v.slice(0, 80) : null;
  }

  function showThanks() {
    var thanks = document.createElement('div');
    thanks.className = 'rx-form__thanks';
    var h = document.createElement('p');
    h.className = 'rx-form__thanks-h';
    h.textContent = 'お問い合わせありがとうございます。';
    var s = document.createElement('p');
    s.className = 'rx-form__thanks-s';
    s.textContent = '3営業日以内にご連絡いたします。';
    thanks.appendChild(h);
    thanks.appendChild(s);
    form.parentNode.insertBefore(thanks, form.nextSibling);
    form.style.display = 'none';
  }

  // 社内CRM（ビズカルテ）の受信箱へ写しを送る。貼り付けコード方式（2026-09-29〜）:
  // contact.html の </body> 直前で読み込む inbound-v1.js（公開キー・data-auto="false"）が送信本体。
  // - 公開キーは秘密ではなく、トークンの管理・同期は不要（旧方式の CRM_TOKEN は廃止）
  // - CRM のドメインを変えるときは contact.html の script の src と CSP（script-src）の2か所を直す
  // - スクリプトは async なので、送信時に未読み込みなら読み込み完了を待って送る
  // - 例外は外へ出さない（CRM 側が壊れていても HubSpot への送信とサンクス表示は止めない）
  function copyToCrm(form) {
    try {
      if (window.BizcarteInbound && typeof window.BizcarteInbound.sendForm === 'function') {
        window.BizcarteInbound.sendForm(form);
        return;
      }
      var s = document.querySelector('script[src*="/embed/inbound-v1.js"]');
      if (s) s.addEventListener('load', function () {
        try { if (window.BizcarteInbound) window.BizcarteInbound.sendForm(form); }
        catch (err) { console.warn('CRM inbound failed (ignored):', err); }
      }, { once: true });
    } catch (err) { console.warn('CRM inbound failed (ignored):', err); }
  }

  function showError(message) {
    var err = form.querySelector('.rx-form__error');
    if (!err) {
      err = document.createElement('p');
      err.className = 'rx-form__error';
      err.setAttribute('role', 'alert');
      var submitBtn = form.querySelector('.rx-form__submit');
      form.insertBefore(err, submitBtn);
    }
    err.textContent = message;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var submitBtn = form.querySelector('.rx-form__submit');
    if (submitBtn.disabled) return; // 二重送信ガード

    var fd = new FormData(form);

    // honeypot: botは隠しフィールドを埋める → 送信せず成功と同じ見た目に
    if (String(fd.get('website') || '') !== '') {
      showThanks();
      return;
    }

    var company    = readField(fd, 'company');
    var department = readField(fd, 'department');
    var fullName   = readField(fd, 'fullName');
    var email      = readField(fd, 'email');
    var message    = readField(fd, 'message');

    // クライアント側の必須・形式チェック（サーバー側検証はHubSpotが実施）。
    // 部署（HubSpot の busyo）は HubSpot 側で必須＝空欄・未送信だと 400 REQUIRED_FIELD で拒否されるため必須にする
    if (!company || !department || !fullName || !email || !message) {
      showError('必須項目が未入力です。ご確認ください。');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showError('メールアドレスの形式をご確認ください。');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.classList.add('is-sending');

    var tracking = ['[' + SERVICE_NAME + '経由のお問い合わせ]'];
    var utmSource   = readParam('utm_source');
    var utmMedium   = readParam('utm_medium');
    var utmCampaign = readParam('utm_campaign');
    var source      = readParam('source');
    if (utmSource)   tracking.push('流入元: ' + utmSource);
    if (utmMedium)   tracking.push('媒体: ' + utmMedium);
    if (utmCampaign) tracking.push('キャンペーン: ' + utmCampaign);
    if (source)      tracking.push('参照ページ: ' + source);
    tracking.push('ページ: ' + window.location.href.slice(0, 300));
    var trackingNote = '\n\n---\n' + tracking.join('\n');

    var payload = {
      fields: [
        { name: 'company',   value: company },
        { name: 'busyo',     value: department },
        { name: 'lastname',  value: fullName },
        { name: 'firstname', value: fullName },
        { name: 'email',     value: email },
        { name: 'message',   value: message + trackingNote }
      ],
      context: {
        pageUri:  window.location.href,
        pageName: SERVICE_NAME + ' - お問い合わせ'
      }
    };

    // CRM の受信箱へも写しを送る（ハニーポットと入力チェックを通った送信だけ）
    copyToCrm(form);

    var url = 'https://api.hsforms.com/submissions/v3/integration/submit/'
      + HUBSPOT_PORTAL_ID + '/' + HUBSPOT_FORM_GUID;

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (res.ok) return res.json();
        return res.text().then(function (t) { throw new Error(t); });
      })
      .then(showThanks)
      .catch(function (err) {
        console.error('HubSpot submission error:', err);
        submitBtn.disabled = false;
        submitBtn.classList.remove('is-sending');
        showError('送信に失敗しました。お手数ですが、もう一度お試しください。');
      });
  });
})();
