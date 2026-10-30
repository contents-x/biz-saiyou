# DESIGN — イチ推し採用 デザイントークン

> 本サービス独自のデザイン値。表示崩れ防止の普遍ルールは [DEVICE-RULES.md](DEVICE-RULES.md)。

## TL;DR

イチ推し採用のデザイン方針は **Apple/Stripe風の「洗練されたSNS」**。

- **白基調 × 明朝＋ゴシック2書体**（編集者的・「モーメントを“品”で語る」）
- **大きな余白 × 大きい見出し**（量より密度）
- **ピンク〜マゼンタのグラデは“点”でだけ使う**（CTA・1語の色変え・細い帯のみ）
- 副アクセントの青は廃止し、**色は黒系＋ピンク1色軸**

つまり Instagram/TikTok の派手さは捨てず、**使用面積を激減**させて品とBtoB信頼感を両立させる。クラスは `.rx-` / CSS変数は `--rx-*`。

## カラーパレット

ブランドの署名は **ピンク〜マゼンタ〜紫のグラデ**。テキスト・背景は **Apple/Stripe基準のニュートラル**で、グラデを“1点豪華”に効かせる構造。

| 用途 | 変数 | 値 |
|------|------|-----|
| 主アクセント（ピンク） | `--rx-accent` | `#ec2d87` |
| アクセントRGB | `--rx-accent-rgb` | `236, 45, 135` |
| アクセントhover | `--rx-accent-hover` | `#d61f76` |
| **ブランドグラデ**（CTA・極小アクセントのみ） | `--rx-grad` | `linear-gradient(95deg, #a32bbf 0%, #e6268d 55%, #ff3d87 100%)` |
| テキスト主 | `--rx-text` | `#0a0a0c` |
| テキスト副 | `--rx-text-muted` | `#6e7280` |
| 背景 | `--rx-bg` | `#ffffff` |
| 背景薄（節の差し色） | `--rx-bg-light` | `#fafafa` |
| ボーダー | `--rx-border` | `#e7e7eb` |
| カード背景 | `--rx-card-bg` | `#ffffff` |
| カード影（極弱） | `--rx-shadow` | `0 1px 2px rgba(15,23,42,.04), 0 8px 28px rgba(15,23,42,.06)` |
| 角丸（カード） | `--rx-radius` | `20px` |
| 角丸（小要素・セカンダリーボタン） | `--rx-radius-sm` | `12px` |
| 角丸（大カード・モーダル） | `--rx-radius-lg` | `28px` |
| 角丸（pill・主CTA） | `--rx-radius-pill` | `999px` |

旧 `--rx-accent-2`（ブルー）と `--rx-accent-3`（スカイ）は**廃止**（色軸を1本化）。

## レイアウト・トークン

| 用途 | 変数 | 値 |
|------|------|-----|
| 固定ヘッダー高さ（安全値） | `--rx-header-h` | `clamp(68px, 4.2vw + 34px, 92px)` |

固定ヘッダー `.rx-nav` の実高さ＝ `max(64px, ロゴ clamp(42→54px) + 上下padding clamp(12→18px))` で、**ワイド画面では約90px**まで伸びる。`--rx-header-h` はこれに数pxの余裕を足した安全値。**各ページ最初のセクション（ヒーロー等）は、ヘッダーとの重なりを防ぐため `padding-top` にこの値（＋デザイン上の余白）を必ず確保する**こと。詳細ルールと既存ページの状況は [DEVICE-RULES.md](DEVICE-RULES.md) を参照。

## グラデ使用ルール（最重要）

「派手 → 洗練」の決定打。**面積を絞り、1点豪華**で使う。

| 用途 | 許可 |
|---|---|
| Primary CTAボタン背景 | OK（pill形・主CTA1〜2個まで） |
| アイブロウ等の **1語だけ** 色変え（例: 「**SNS**」） | OK |
| セクション仕切りの**細い水平帯**（高さ 2〜4px）・小アイコンの単色塗り | OK |
| **セクション全体の背景塗り** | NG |
| 見出し本体（h1/h2）への適用 | NG |
| 大面積の装飾（ヒーロー背景・帯） | NG |
| 本文テキスト | NG |

## フォント

参照: [Moments of HAYAMA](https://sumai.es-conjapan.co.jp/hayama24/moments/) の **筑紫明朝＋筑紫ゴシック＋Helvetica Now Display**（編集者的スタック）を、Google Fontsの**無料近似**で実装する。

| 役割 | 書体（採用） | ウェイト | letter-spacing | line-height | 元想定（参照） |
|------|------|---------|---|---|---|
| 見出し（h1〜h3）・リード | **Shippori Mincho** | 500 / 600 | `.02em` | 1.3 | 筑紫明朝の代替（最も近い） |
| 本文・ナビ・補足 | **Zen Kaku Gothic Antique** | 400 / 500 / 700 | 0 | 1.85 | 筑紫ゴシックの代替（上品な丸み） |
| 英字・数字 | **Inter** | 500 / 700 | `-.01em` | 1.4 | Helvetica Now Display の代替 |
| ホームの見出し全般（h1 / 各セクションの h2・h3・カード見出し） | **Zen Kaku Gothic Antique 900** | 900 | `.01em` | 1.12〜1.4 | 2026-09-28 のデザイン案が太ゴシック基調のため、**ホームだけ明朝を使わない**（`.rx-home-hero__title` / `.rx-hs__title` / 各カード見出し）。他ページの h1〜h3 は引き続き Shippori Mincho |
| 手書き風の一言 | **Zen Kurenaido** | 400 | `.02em` | 1.4 | ホームの `.rx-hs__hand`（「伝え方を変えるだけで、出会える人が変わる。」等）・02 のラベル・04 の注釈・10 の「想いが伝わる。採用が変わる。」専用。ペン書き風でデザイン案の筆致に近い。旧 Yuji Syuku（筆ペン風）は 2026-09-28 に廃止 |

```css
/* 見出し（明朝でモーメントを） */
font-family: 'Shippori Mincho', 'Hiragino Mincho ProN', 'Yu Mincho', 'Noto Serif JP', serif;
/* 本文（ゴシックで読み心地） */
font-family: 'Zen Kaku Gothic Antique', 'Hiragino Sans', 'Yu Gothic', Meiryo, sans-serif;
/* 英字・数字（クリスプ） */
font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
```

- 旧 `Zen Kaku Gothic New` `Noto Sans JP` は**廃止**。
- 本番は自前ホスト(WOFF2)＋和文サブセット（[DEVICE-RULES.md](DEVICE-RULES.md) §16）。**明朝は字形が多いのでサブセット必須**（フル字形は数MB）。
- 読込ウェイトを絞る — Shippori=500/600、Zen Kaku Gothic Antique=400/500/700（**index.html のみ 900 を追加**＝ヒーロー見出し用）、Inter=500/700。Zen Kurenaido（400のみ）は index.html のみ読み込む（Yuji Syuku は 2026-09-28 に廃止）。

## タイポスケール / ボタン / コンテナ幅

**大きな見出し × 大きな余白**（Apple/Stripe基準）。clamp は rem+vw 混在、最大は最小の2.5倍以内（[DEVICE-RULES.md](DEVICE-RULES.md) §5）。

**ヒーロー内テキストの例外（縦横比追従）**: heroは100svhのsticky枠のため、内部の文字サイズと配置は `vw + svh` のミックスでスケールさせる（画像の `object-fit: cover` と同じ感覚で、横長の低い画面では小さく・縦に余裕がある画面では大きく）。実装値: h1 `clamp(1.625rem, 1.2vw + 3.2svh + .4rem, 3.25rem)`（SPは上限2.125rem）/ 階段リード `clamp(1rem, .6vw + 1.7svh + .35rem, 1.75rem)` / copy配置 `top: clamp(80px, 12svh, 140px)`。通常フローのセクション見出しは従来どおり vw のみで良い。

| 用途 | 変数 | 値（≒px 320→1440幅） |
|------|------|------|
| ヒーロー h1 | `--rx-fs-hero` | `clamp(2.25rem, 1.4rem + 3.4vw, 4.5rem)`（36→72） |
| 見出し h2 | `--rx-fs-h2` | `clamp(1.875rem, 1.4rem + 1.8vw, 3rem)`（30→48） |
| 見出し h3 | `--rx-fs-h3` | `clamp(1.25rem, 1.1rem + 0.7vw, 1.5rem)`（20→24） |
| リード文 | `--rx-fs-lead` | `clamp(1.125rem, 1rem + 0.4vw, 1.375rem)`（18→22） |
| 本文 | `--rx-fs-body` | `1.0625rem`（17px・Apple基準） |
| 補足/キャプション | `--rx-fs-small` | `0.875rem`（14px） |
| アイブロウ | `--rx-fs-eyebrow` | `0.875rem`・`letter-spacing: .12em`・全英大文字 |

**ボタン**
```css
.rx-btn { min-height: 48px; font-weight: 700; }                                  /* タップ44px超(§12) */
.rx-btn--primary {                                                                 /* グラデCTA「無料で相談」 */
  background: var(--rx-grad); color: #fff; border-radius: var(--rx-radius-pill);
  padding: clamp(.95rem, .8rem + .4vw, 1.1rem) clamp(1.6rem, 1.3rem + 1vw, 2.25rem);
}
.rx-btn--ghost {                                                                   /* 「資料DL」 */
  background: #fff; color: var(--rx-text); border: 1px solid var(--rx-border);
  border-radius: var(--rx-radius-sm);
  padding: clamp(.85rem, .7rem + .4vw, 1rem) clamp(1.4rem, 1.1rem + 1vw, 2rem);
}
```

**コンテナ幅**（[DEVICE-RULES.md](DEVICE-RULES.md) §9 準拠）
```css
.rx-container { width: min(100%, 1200px); margin: 0 auto; padding: 0 clamp(20px, 4vw, 40px); }
@media (min-width:1440px){ .rx-container{ max-width:1340px; } }
@media (min-width:1920px){ .rx-container{ max-width:1560px; } }
section { padding: clamp(80px, 12vw, 200px) 0; }   /* 旧 48→160 から拡大 */
/* 長文本文ブロックのみ可読性のため max-width 720〜820px */
```

## クラス命名規則

- プレフィックス `.rx-`（例 `.rx-header` `.rx-hero` `.rx-btn` `.rx-container`）
- BEM風: ブロック `.rx-block` / 要素 `__elem` / 修飾 `--mod`
- z-index は生数字を使わず階層変数（[DEVICE-RULES.md](DEVICE-RULES.md) §11）

## 旧トークンからの主な変更点（diff サマリ）

| 区分 | 旧 | 新 |
|---|---|---|
| テキスト主色 | `#1a2742` | `#0a0a0c` |
| テキスト副 | `#5c6b85` | `#6e7280` |
| 背景薄 | `#f6f7fb` | `#fafafa` |
| ボーダー | `#e7eaf1` | `#e7e7eb` |
| 副アクセント青/スカイ | あり | **廃止** |
| 見出しフォント | Zen Kaku Gothic New 900 | **Shippori Mincho 500/600**（明朝・編集者的） |
| 本文フォント | Noto Sans JP 400 | **Zen Kaku Gothic Antique 400** |
| 英字・数字 | — | **Inter 500/700**（新規） |
| h1 サイズ | 32→56 | **36→72** |
| 本文サイズ | 16 | **17** |
| カード角丸 | 16 | **20** |
| シャドウ | `0 4px 24px rgba(...,.08)` | **極弱2段** |
| セクションpadding | 48→160 | **80→200** |
| グラデ使用範囲 | 比較的自由 | **CTA・1語色変え・細い帯だけ** |

## ページ専用トークン: 料金プラン（price.html / `--rxp-*`）

> 出典モック: `採用/資料/デザイン候補/料金ページ/1〜5.png`（2026-06-12）。モックのピンクはサイト共通 `--rx-accent`（`#ec2d87`）と**別系統**のため、`css/price.css` 内にページ専用トークンとして分離。グローバル `--rx-*` は変更しない。

| 用途 | 変数 | 値 |
|------|------|-----|
| 主ピンク（数字・強調・枠） | `--rxp-pink` | `#eb2a63` |
| **ヒーロー専用の鮮やかピンク**（`.rx-phero2` スコープ。最新版.png 準拠） | `--hp` | `#f00858` |
| **ヒーロー専用CTAグラデ**（同上） | `--hp-grad` | `linear-gradient(95deg, #f8246a 0%, #ef0a5a 58%, #e80a64 100%)` |
| CTAグラデ | `--rxp-grad` | `linear-gradient(95deg, #e8205c 0%, #ee316b 55%, #f24a80 100%)` |
| 薄ピンク面（9ヶ月総額帯・診断バンド等） | `--rxp-pink-pale` | `#fdeef4` |
| プラン頭帯・期タグの黒 | `--rxp-dark` | `#1a191c` |
| ヒーロー/ステップパネルの薄グレー | `--rxp-bg-gray` | `#f7f7f5` |
| 見出し書体 | — | Noto Sans JP 900（モック準拠。ページ内のみ） |
| 英字・数字 | — | Inter 700（金額・PRICE PLAN・ステップ番号） |
| LINEブランド緑 | — | `#06c755`（SVGアイコンのみ） |

## ロゴ・ファビコン

ヘッダー／フッターのブランドは**企業ロゴ画像**（ワードマーク「イチ推し採用」。「推」だけピンク＋上の2本の勢い線＋文字の下から右上へ伸びるピンクの筆の矢印）。**2026-10-31 にビズ採用から改名し、支給ロゴ（透過PNG 2172×724 と、タグライン「採用の新しいスタンダード。」入りの白背景版）に差し替え**。ファビコン（角丸ピンク＋白「1」）は 2026-07-07 のまま。

| 用途 | ファイル | 実装 |
|------|---------|------|
| ロゴ（ヘッダー） | `images/logo/ichioshi-saiyo-logo.webp`（480×158・**透過**） | `.rx-nav__logo`。原色のまま。高さ clamp(34→46px)・`width:auto` |
| ロゴ（フッター） | `images/logo/ichioshi-saiyo-logo-white.webp`（480×158・**透過**） | `.rx-footer__logo-img`。濃紺地用に**紺の文字だけ白**へ置き換えた書き出し（ピンクは原色）。CSS フィルタは使わない（`brightness(0) invert(1)` だとピンクまで白になるため） |
| ロゴ（タグライン入り・控え） | `images/logo/ichioshi-saiyo-logo-full.webp`（960×415・白背景） | 未使用。OG画像などで使うときの素材 |
| ファビコン | `images/favicon/favicon-32.png` / `favicon-16.png` / `favicon-192.png` / `apple-touch-icon.png`（180）/ `favicon-master-transparent.png`（192・マスター） | 全サイズ共通で**角丸ピンク背景ごと**（透過なし・完成品アイコンをそのままリサイズ）。iOS黒角回避の合成処理は不要（元から背景込みのため）。全ページ `<head>` に `rel="icon"` / `apple-touch-icon` を相対パスで設置 |

- ロゴの書き出し（2026-10-31）: 支給の透過PNGを不透明部分の外接矩形＋12px で切り詰め → 不透明度 240 以上を 255 にそろえる（背景除去の名残で本体が 253 前後だったため）→ 幅480へ Lanczos 縮小（乗算済みアルファで縮小し縁の黒ずみを防ぐ）→ WebP（品質92・アルファ品質100）。フッター用は、各画素の赤成分で紺（R≈2）とピンク（R≈252）の混ざり具合を出し、紺の分だけ白に置き換えて同じ手順で書き出す。
- `width`/`height` 属性はCLS対策のため実寸（480×158）と一致させる（DEVICE-RULES.md §1）。CSSは高さ固定・`width:auto`。
- 旧ロゴ: `biz-saiyo-logo*.webp`（ビズ採用・白背景）は 2026-10-31 に削除。`recruitx-logo.png`（リクルートX）はどこからも参照していない。
- アイコン原典はGPT生成の「ICON A」（複数バリエーションのプレビュー付き1枚絵）。ピンク画素のbbox検出でメインアイコン（角丸正方形）のみをクロップし、そのまま各サイズ（16/32/180/192）へLanczos縮小。**角丸ピンク背景ごと**なので透過処理・iOS黒角合成は行わない。
- パスは**各ページからの相対**（事例・コラム記事は `../../images/...`）。ルート絶対パス禁止の原則に従う。
- 事例詳細・コラム記事のビルド雛形 `tools/templates/*.tpl` も同じロゴ＋faviconを参照する。ロゴを変えたらテンプレも同時に直す（直さないと次のビルドで戻る）。
- ロゴ差し替え手順: ① 透過版があればそれを使う（無ければ白→透過化）→ ② 外接矩形で切り詰め → ③ 幅480へ縮小しヘッダー用とフッター用（紺→白）を書き出す → ④ 縦横比が変わった場合は全HTML＋tplの `width/height` 属性を一括置換。
- 画像の中に描き込まれたロゴ・名前: ホームの `images/home/scene-3.webp`（採用サイト画面のヘッダー）と `scene-5.webp`（SNS のアカウント名 `ichioshi_recruit`）は 2026-10-31 に新ロゴ・新名へ描き替え済み。`works-5.webp`（自社の採用漫画の表紙）は作品なので旧ロゴ「ビズ採用」のまま。
