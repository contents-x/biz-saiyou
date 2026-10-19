/* =========================================================================
   column.js — ビズ採用 コラムページ（column.html 専用）
   - カテゴリタブ絞り込み（aria-pressed 切替）
   - キーワード検索（タイトル＋説明文＋カテゴリの部分一致。説明文はカードの data-desc）
   - よく検索されるタグ → 検索ボックスに流し込んで実行
   - カテゴリ × 検索 は AND 条件。ナビ・入場アニメは main.js が担当。
   ========================================================================= */
(function () {
  'use strict';

  var filterGroup = document.querySelector('[data-column-filter]');
  var grid = document.querySelector('[data-column-grid]');
  var searchForm = document.querySelector('[data-column-search]');
  var emptyMsg = document.querySelector('[data-column-empty]');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.rx-colcard'));
  var state = { category: 'all', query: '' };

  function normalize(s) {
    return (s || '').toLowerCase().replace(/\s+/g, '');
  }

  function apply() {
    var q = normalize(state.query);
    var visible = 0;
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var cat = card.getAttribute('data-category') || '';
      var title = card.getAttribute('data-title') || '';
      var desc = card.getAttribute('data-desc') || '';
      var catOk = (state.category === 'all' || cat === state.category);
      var qOk = (!q || normalize(title).indexOf(q) !== -1 || normalize(desc).indexOf(q) !== -1 || normalize(cat).indexOf(q) !== -1);
      var show = catOk && qOk;
      card.hidden = !show;
      if (show) visible++;
    }
    if (emptyMsg) emptyMsg.hidden = (visible !== 0);
  }

  /* ---- カテゴリタブ ---- */
  if (filterGroup) {
    var buttons = filterGroup.querySelectorAll('button[data-filter]');
    filterGroup.addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-filter]');
      if (!btn) return;
      state.category = btn.getAttribute('data-filter');
      for (var i = 0; i < buttons.length; i++) {
        buttons[i].setAttribute('aria-pressed', buttons[i] === btn ? 'true' : 'false');
      }
      apply();
    });
  }

  /* ---- キーワード検索 ---- */
  if (searchForm) {
    var input = searchForm.querySelector('input[type="search"], input[name="q"]');
    searchForm.addEventListener('submit', function (e) {
      e.preventDefault();
      state.query = input ? input.value : '';
      apply();
    });
    if (input) {
      input.addEventListener('input', function () {
        // 入力が空に戻ったら即リセット（送信を待たない）
        if (input.value === '') { state.query = ''; apply(); }
      });
    }
  }

  /* ---- よく検索されるタグ ---- */
  var tagButtons = document.querySelectorAll('.rx-colsearch__tag[data-query]');
  for (var t = 0; t < tagButtons.length; t++) {
    tagButtons[t].addEventListener('click', function (e) {
      var q = e.currentTarget.getAttribute('data-query') || '';
      state.query = q;
      var input2 = searchForm && searchForm.querySelector('input[type="search"], input[name="q"]');
      if (input2) input2.value = q;
      apply();
      if (grid.scrollIntoView) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
