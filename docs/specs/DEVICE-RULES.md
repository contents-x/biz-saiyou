# DEVICE-RULES — 全デバイスで美しく表示する絶対ルール

> 「機種で表示が変わらないように統一する」ための普遍ルール（Contents X 系共通・**ブランドが変わっても継承・原則改変しない**）。新規ページ・既存修正・コンポーネント設計のすべてで遵守。

## TL;DR

「PCではキレイなのにスマホで崩れる」「Mac↔Win↔スマホで文字がずれる」を恒久的に防ぐ17ルール。**コミット前に 320/768/1024/1440/1920px の5幅 + 実機OS（§16）で確認**し、§17のチェックリストを通す。

## 1. 画像HTML属性は実ファイル寸法と一致必須
`<img width height>` は実寸法と同じアスペクト比で書く（誤った比は画像が歪む＝ロゴ潰れの主因）。不安なら CSS `aspect-ratio: 実W / 実H` を併用。実寸確認: `python3 -c "from PIL import Image; print(Image.open('path').size)"`。

## 2. 最低5デバイス幅で確認
コミット前に **320 / 768 / 1024 / 1440 / 1920px** で表示崩れ・動的UI開閉を目視。
**幅だけ変えてもOSのフォント差（→§16）は出ない**。Mac / Win / iOS / Android の実機 or 実機クラウド（BrowserStack / LambdaTest）をリリース前に最低1回通す。DevToolsのレスポンシブ表示は自分のOS上で描画するため、Win ClearTypeや本物のSafariの文字描画は再現できない（検出不可）。

## 3. ブレークポイント統一
```css
@media (max-width: 768px) { /* モバイル */ }
@media (max-width: 1024px) and (min-width: 769px) { /* タブレット */ }
```

## 4. Flexbox 安全ルール
親に `min-width:0`、潰したくない要素（ロゴ/アイコン/CTA）に `flex-shrink:0`、可変要素に `flex:1`。

## 5. 流動サイジング
見出し・ヒーロー・重要CTAは固定px禁止、`clamp(min, fluid, max)`。本文・キャプションは固定14-16px可。

## 6. ホバーUIはタッチ代替必須
PCの `:hover` 情報（ツールチップ/ドロップダウン）はSPでタップ or 常時可視 or 別UIで提供。

## 7. ハンバーガー最低要件
`order` 指定 + `flex-shrink:0` + `min 48×48px` + 最上位z-index。320pxで押せる位置。`touchend` を `click` と併用（iOS Safari対策）。

## 8. 横スクロール禁止
`overflow-x:hidden` は応急処置。根本原因（超過する固定幅要素）を修正。確認: `document.body.scrollWidth > window.innerWidth` が `true` ならNG。

## 9. ワイド画面（1440px超）の余白対策
コンテナは段階的に max-width 拡大、padding は `clamp()`/vw で画面比に追従。長文本文だけ可読性のため max-width 720-820px 維持。
```css
.rx-container { width: min(100%, 1200px); margin: 0 auto; padding: 0 clamp(16px, 3vw, 32px); }
@media (min-width: 1440px) { .rx-container { max-width: 1340px; } }
@media (min-width: 1920px) { .rx-container { max-width: 1560px; } }
section { padding: clamp(48px, 8vw, 160px) 0; }
```

## 10. 意図的な重なりは距離感を保つ
重ねたUIは「グループ親 + 全子要素 % or cqw 配置」、グループ親に `aspect-ratio` をlock。SPは別フレームとして再設計。「重なりは座標(%)、レイアウトは比率(grid/flex)、文字は流動(clamp)」の3層で考える。

## 11. Z-index 階層表（生数字を増やさない）
```css
:root {
  --z-base:0; --z-elevated:10; --z-sticky:100; --z-header:1000;
  --z-fab:1500; --z-dropdown:2000; --z-modal:9000; --z-toast:9500;
  --z-hamburger:10000; --z-tooltip:10500;
}
```
モーダル中にFABが透ける等は `body:has(.modal.open) .fab{display:none}` で抑止（z-indexで戦わない）。

## 12. タッチターゲット最低 44×44px
タップUIは `min-width/height:44px`。視覚的に小さくても padding か擬似要素でタップ領域確保。隣接要素間に最低8pxギャップ。

## 13. 固定ヘッダーの重なり対策（最初のセクション＋アンカーオフセット）

固定ヘッダー `.rx-nav` は `position: fixed`・半透明グラスで本文の上に重なる。実高さは
`max(64px, ロゴ clamp(42→54px) + 上下padding clamp(12→18px))` で**ワイド画面では約90px**まで伸びる。
これを 1 箇所のトークン `--rx-header-h: clamp(68px, 4.2vw + 34px, 92px)`（[DESIGN.md](DESIGN.md) レイアウト・トークン）に集約し、ハードコードの `72px`/`64px` 等を散らさない。

- **各ページ最初のセクション（ヒーロー）は `padding-top` に `--rx-header-h`（＋デザイン余白）を必ず確保する。** 特に2カラムヒーローの画像側カラムや、SPで画像が上に来る（`order:-1`）構成は余白を忘れやすく、ヘッダーと画像が重なる（2026-06-14 事例詳細 `.rx-cdtl-hero` で発生・修正、BUGS.md）。
- 既存の妥当値を尊重しつつ最低限を保証したい場合は `padding-top: max(var(--rx-header-h), <従来値>)`（例: 旧 price.html `.rx-phero2`）。
- ページ内アンカーは `scroll-margin-top: calc(var(--rx-header-h) + 16px)` で見出しがヘッダー下に隠れないようにする。

```css
html { scroll-behavior: smooth; }
/* 最初のセクション */
.first-section { padding-top: var(--rx-header-h); }
/* アンカー */
h1,h2,h3,h4,[id]:not(html,body){ scroll-margin-top: calc(var(--rx-header-h) + 16px); }
```

現状の各ページ最初のセクション（いずれも `--rx-header-h`≈最大92px を満たす。共通ヘッダーの実高さは 58〜90px＝2026-09-28 統一時に padding を調整）:
| ページ | セクション | 上余白（最小〜） |
|---|---|---|
| index.html | `.rx-home-hero` | `calc(var(--rx-header-h) + clamp(20→36px))`（PC `+clamp(8→14px)`）。高さは内容なり（`min-height` 指定なし・2026-09-28） |
| case.html | `.rx-chero` | `calc(64px + clamp(40→80px))`＝104px〜 |
| contact.html | `.rx-contact` | `clamp(80→200px)` |
| price.html | `.rx-price-hero` | `calc(var(--rx-header-h) + clamp(16→32px))`（PC `+clamp(24→56px)`、背の低い画面は `+20px` / `+12px`）。人物は右カラム内に置くのでヘッダーに重ならない（2026-10-23） |
| case/{slug}/ | `.rx-cdtl-hero` | `var(--rx-header-h)`（＋inner余白） |
| company.html / privacy.html | `.rx-lhero`（`css/legal.css`） | `calc(var(--rx-header-h) + clamp(36→64px))` |

## 14. i18n: EN は日本語より約30%長い（多言語化する場合）
ナビ/ボタンの最小幅はENを基準に。`html[lang="en"]` 専用にgap/font-sizeを詰める。翻訳は `data-ja`/`data-en` で明示。

## 15. 画像読込アトリビュート使い分け
| 場所 | loading | fetchpriority |
|---|---|---|
| ヒーロー/LCP | eager | high（`<link rel="preload" as="image">` 併用） |
| ATF内 | eager | auto |
| ATF外/モーダル内 | lazy | — |

全 `<img>` に `src/alt/width/height/loading/decoding` を明示。WebPデフォルト（80KB超は AVIF をフォールバック付き）、kebab-case 命名 + `images/{用途}/`。

## 16. クロスOSフォント統一・日本語組版（表記ズレ防止）

「Mac/Win/iPhone/Androidで文字幅・改行・行高がずれる」恒久対策。**原因は独立した3層**で、混同すると対策がチグハグになる。

| 層 | 原因 | 対処 |
|---|---|---|
| ① フォント置換 | 未指定/未読込時、OSが別フォントへ（Mac=ヒラギノ / Win=游ゴシック・メイリオ / Android=Noto）。字幅・改行・行高が全部変わる | **下記でほぼ消せる（主因）** |
| ② メトリクス読取差 | 同一フォントでも縦メトリクスの読み元がOSで違う（macOS=`hhea` / Win・Android=`OS/2 Win`）→ 行高・縦位置ズレ | フォールバックのメトリクス上書きで緩和 |
| ③ ラスタライズ差 | Win=ClearType（サブピクセル）/ Mac=グレースケール / Linux=FreeType。太さ・シャープさが変わる | **CSSで統一不可** → §2の実機確認で担保 |

### フォントを固定（主因①をほぼ消す・最優先）
- **Webフォントを1〜2書体に固定し自前ホスト（WOFF2のみ）**。OS標準フォントへフォールバックさせない。書体・値は [DESIGN.md](DESIGN.md)。
- **和文は必ずサブセット**（フル字形は1万字超・数MB）。`glyphhanger` / `pyftsubset`（fonttools）で使用文字に絞るか `unicode-range` 分割（90%超削減可）。
- 読込最適化:
  - ヒーローの本番フォントは `<link rel="preload" as="font" type="font/woff2" crossorigin>`（`crossorigin` 必須・無いと2重DL）
  - `@font-face { font-display: swap; }`（CLSを厳格にゼロにするなら `optional`）
  - フォールバックに `size-adjust` 等のメトリクス上書きで入替時のガタつき（CLS）を消す。**※和文は字面が揃うため効果は限定的・Safariは `size-adjust` のみ対応 → 和文の本丸は「固定すること」そのもの**。

### 描画・日本語組版
```css
html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; /* macOSのみ有効・Winは変わらない */
       -webkit-text-size-adjust: 100%; text-size-adjust: 100%; } /* iOSの勝手な文字拡大を止める */
.rx-jp-body { word-break: keep-all; line-break: strict; overflow-wrap: anywhere; line-height: 1.8; } /* 半角空白なし日本語の改行 */
.rx-stat-num { font-variant-numeric: tabular-nums; } /* 大きな数字(9割/360万円)の桁ブレ防止・要フォントtnum対応 */
```
- 見出しは `word-break: auto-phrase`（文節改行・要 `lang="ja"`）＋ `text-wrap: balance` を `@supports` でロケール限定（素の `balance` は和文で不自然に割れる）。
- `line-height` は unitless（和文1.7〜1.9 / 見出し1.2〜1.4）。`<html lang="ja">` を明示。
- `100vh` は使わず `svh` / `dvh`（モバイルでアドレスバーに切られるのを防ぐ）。`env(safe-area-inset-*)` は `<meta viewport ... viewport-fit=cover>` 必須。

## 17. コミット前チェックリスト
- [ ] 画像 width/height が実比と一致 + loading/decoding 指定
- [ ] 320/768/1024/1440/1920px で崩れなし
- [ ] ハンバーガー押せる・ドロップダウン開ける・CTAタップできる
- [ ] タップ要素 44×44px・隣接8pxギャップ
- [ ] 横スクロール出ない
- [ ] 見出しは vw含む clamp（固定px地獄なし）
- [ ] ホバー専用UIにタッチ代替
- [ ] 1920px で左右が真っ白に間延びしない
- [ ] 重なりUIの距離感が全幅で崩れない
- [ ] z-index は §11 の変数を使用
- [ ] アンカー先に scroll-margin-top
- [ ] （多言語なら）ENで破綻しない
- [ ] LCP画像のみ eager+high、他は lazy
- [ ] Webフォントを自前ホストで固定（OS標準任せにしない）+ 和文サブセット済み
- [ ] 主要フォントに preload(crossorigin) + font-display 指定、CLS < 0.1
- [ ] 大きな数字に tabular-nums / 日本語に word-break・line-break・overflow-wrap
- [ ] Mac / Win / iOS / Android の実機（or 実機クラウド）で文字幅・改行を確認（§2・§16）
