/* =========================================================================
   case.js — イチ推し採用 導入事例ページ（case.html 専用）
   - 業種フィルタ（aria-pressed 切替 + hidden 属性で表示制御）
   - ナビ・入場アニメは main.js が担当（このファイルはページ固有機能のみ）
   ========================================================================= */

/* ---- 業種フィルタ ---- */
(function () {
  'use strict';

  var group = document.querySelector('[data-case-filter]');
  if (!group) return;
  var buttons = group.querySelectorAll('button[data-filter]');
  var cards = document.querySelectorAll('.rx-ccard[data-category]');

  group.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-filter]');
    if (!btn) return;
    var filter = btn.getAttribute('data-filter');

    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', buttons[i] === btn ? 'true' : 'false');
    }
    for (var j = 0; j < cards.length; j++) {
      cards[j].hidden = (filter !== 'all' && cards[j].getAttribute('data-category') !== filter);
    }
  });
})();
