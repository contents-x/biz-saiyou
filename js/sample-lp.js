/* =========================================================================
   sample-lp.js — 客先ごとの採用LP（制作サンプル /sample/{客先}/）の共通の動き
   - メニュー: ヘッダーの三本線で開閉（Esc・外側を押す・リンクを押すと閉じる）
   - 動画: 中央の再生ボタンで再生。再生中はボタンと再生時間の表示を消す（JS 無効でも標準の操作で再生できる）
   - 漫画: [data-manga-open] を押すと読み画面（<dialog class="slp-mv">）を開く
     閉じる: × / 最後の「閉じる」/ Esc（dialog 標準）/ 左右の暗い所を押す / スマホの「戻る」
     （開くときに履歴を1つ積み、「戻る」でページから離れず読み画面だけを閉じる。ホームの js/works-viewer.js と同じ作り）
   - DOM生成なし（ページ画像は HTML に loading="lazy" で置いてあり、開くまで読み込まれない）
   ========================================================================= */
(function () {
  'use strict';

  document.documentElement.classList.add('slp-js');

  /* ---- メニュー ---- */
  var header = document.querySelector('.slp-header');
  var menuBtn = header && header.querySelector('.slp-header__menu');
  if (header && menuBtn) {
    var setMenu = function (open) {
      header.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menuBtn.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    };
    menuBtn.addEventListener('click', function () {
      setMenu(!header.classList.contains('is-open'));
    });
    header.querySelectorAll('.slp-nav a').forEach(function (a) {
      a.addEventListener('click', function () { setMenu(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) {
        setMenu(false);
        menuBtn.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (header.classList.contains('is-open') && !header.contains(e.target)) setMenu(false);
    });
  }

  /* ---- 動画 ---- */
  document.querySelectorAll('.slp-movie__player').forEach(function (player) {
    var video = player.querySelector('video');
    var play = player.querySelector('.slp-movie__play');
    if (!video) return;
    // 再生前は LP案どおりサムネイルと再生ボタンだけを見せ、再生したら標準の操作バーを出す（JS 無効なら最初から出ている）
    video.controls = false;
    if (play) {
      play.addEventListener('click', function () {
        var p = video.play();
        if (p && p.catch) p.catch(function () {});
      });
    }
    video.addEventListener('play', function () {
      video.controls = true;
      player.classList.add('is-playing');
    });
    video.addEventListener('ended', function () { player.classList.remove('is-playing'); });
  });

  /* ---- 漫画の読み画面 ---- */
  var dialog = document.querySelector('.slp-mv');
  var openers = document.querySelectorAll('[data-manga-open]');
  if (!dialog || !openers.length || typeof dialog.showModal !== 'function') return;

  var scroller = dialog.querySelector('.slp-mv__scroll');
  var opener = null;
  var pushed = false;
  var skipPop = false;

  function open(btn) {
    opener = btn;
    document.documentElement.classList.add('is-mv-open');   // 後ろのページをスクロールさせない
    dialog.showModal();
    scroller.scrollTop = 0;
    scroller.focus({ preventScroll: true });                 // 矢印キー・スペースでそのまま読み進められるように
    try {
      history.pushState({ slpManga: true }, '');
      pushed = true;
    } catch (e) {
      pushed = false;
    }
  }

  dialog.addEventListener('close', function () {
    document.documentElement.classList.remove('is-mv-open');
    if (opener) opener.focus({ preventScroll: true });
    opener = null;
    // ×・Esc などで閉じたときは、開くときに積んだ履歴を戻しておく
    if (pushed) {
      pushed = false;
      skipPop = true;
      history.back();
    }
  });

  window.addEventListener('popstate', function () {
    if (skipPop) { skipPop = false; return; }
    if (!dialog.open) return;
    pushed = false;   // 履歴はもう戻っている
    dialog.close();
  });

  function close() { dialog.close(); }
  dialog.querySelector('.slp-mv__close').addEventListener('click', close);
  dialog.querySelector('.slp-mv__end-close').addEventListener('click', close);
  // ページの左右の暗い所（スクロール領域そのもの）を押したら閉じる。ページの上を押しても閉じない
  scroller.addEventListener('click', function (e) {
    if (e.target === scroller) close();
  });

  openers.forEach(function (btn) {
    btn.addEventListener('click', function () { open(btn); });
  });
})();
