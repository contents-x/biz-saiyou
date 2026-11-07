# イチ推し採用 — 採用LP（リポジトリ名 recruitx）

> **求人広告に頼らない採用へ。** SNS運用・コンテンツ制作・Meta広告運用を通じて、共感から応募へつなげる採用支援サービス**イチ推し採用**のランディングページ。

[![Stack: HTML/CSS/JS](https://img.shields.io/badge/stack-HTML%2FCSS%2FJS-0a0a0c)](#技術スタック)
[![License: 内部](https://img.shields.io/badge/license-internal-ec2d87)](#ライセンス)
[![Status: In development](https://img.shields.io/badge/status-in_development-6e7280)](#現在の状態)

運営: **コンテンツエックス株式会社**（Contents X / BizManga 兄弟事業）

---

## クイックスタート

このサイトは**素のHTML/CSS/JS**で、ビルド不要・依存パッケージ不要です。

```bash
git clone https://github.com/josawa2255/recruitx.git
cd recruitx
# 方法A: ダブルクリックでブラウザに開く
open index.html

# 方法B: ローカルサーバー（fonts等を厳密に確認したい時）
python3 -m http.server 8753
# → http://localhost:8753/
```

> `index.html` は**同階層相対パス**で書かれているため、ファイル直開きでもサーバー経由でも、また GitHub Pages 公開後でも同じく動きます（[CLAUDE.md](CLAUDE.md) のリンクルール参照）。

---

## ページ構成

| ページ | ファイル | 内容 |
|---|---|---|
| トップLP | `index.html` | HERO → 悩み → フェーズ → 場面 → AIO → 変化 → 実績 → 導入事例 → 料金 → 流れ → 最終CTA（2026-09-28 新デザイン案準拠） |
| お問い合わせ | `contact.html` | フォーム（HubSpot Forms API v3 に直接POST） |

### トップLPのセクション

```
1.  #hero     ヒーロー（左コピー＋CTA2つ／右に4つのコンテンツカード／下に3つの特長の帯）
2.  #issue    悩み「求人票だけでは、働くイメージまでは伝わらない。」（3カード）
3.  #phase    フェーズ「フェーズに合わせて、伝わるカタチで。」（4コンテンツ×5フェーズの対応表）
4.  #scene    場面「採用のさまざまな場面で、使える。」（6カード）
5.  #aio      AIO「AIにも、会社の魅力を伝える。」（情報収集の図／ブラウザ風モック／効果3つ）
6.  #change   変化「イチ推し採用で、採用の伝わり方はこう変わる。」（導入前→導入後）
7.  #results  効果の確かめ方「効果は、4つの指標で確かめる。」（提案書 p21）
8.  #flow     流れ「ご相談から公開・改善までの流れ」（6ステップ＋CREATIVE TEAM）
9.  #plans    料金「料金は、月額15万円〜」（提案書 p24）
10. #cases    導入事例・制作実績（表紙5点）
11. #cta      最後のCTA「まずは、無料の採用力診断から。」（提案書 p26）
    Footer    共通フッター
    ※ 1〜6・8〜10 は 2026-09-28 のデザイン案（スライド9枚）、7・11 は提案書 最終版（26ページ）準拠。詳細は docs/specs/SPEC.md
```

---

## ドキュメント

| ファイル | 内容 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 開発の入口・規約・ブランドボイス・全docへのルーティング |
| [docs/DOC-RULES.md](docs/DOC-RULES.md) | md運用ルール・スキル使用判断・自動修整ポリシー・フック仕様 |
| [docs/specs/SPEC.md](docs/specs/SPEC.md) | 機能仕様（ページ・URL・コンポーネント） |
| [docs/specs/DESIGN.md](docs/specs/DESIGN.md) | デザイントークン（色・フォント・タイポ） |
| [docs/specs/DEVICE-RULES.md](docs/specs/DEVICE-RULES.md) | 全デバイス対応の絶対ルール17項目 |
| [docs/content/SEO.md](docs/content/SEO.md) | メタ・構造化データ・内部リンク |
| [docs/operations/INFRA.md](docs/operations/INFRA.md) | 開発環境・外部サービス・触禁領域（実IDは非公開） |
| [docs/operations/HUBSPOT-CTA-HANDOFF.md](docs/operations/HUBSPOT-CTA-HANDOFF.md) | お問い合わせのHubSpot連携仕様 |
| [docs/operations/BEST-PRACTICE-WATCH.md](docs/operations/BEST-PRACTICE-WATCH.md) | 週次でClaude公式追従＋ハブmd監査の台帳 |
| [docs/planning/ROADMAP.md](docs/planning/ROADMAP.md) | やること・拡張計画 |
| [docs/planning/KNOWLEDGE.md](docs/planning/KNOWLEDGE.md) | 学び・引き継ぎ知識 |
| [BUGS.md](BUGS.md) | バグの記憶・再発防止 |

---

## 技術スタック

| 領域 | 採用 |
|---|---|
| 構造 | **素の HTML / CSS / JavaScript**（フレームワーク非依存・ビルド不要） |
| フォント | Shippori Mincho（見出し） / Zen Kaku Gothic Antique（本文） / Inter（英字・数字）／ Google Fonts経由 |
| デプロイ | GitHub Pages + CNAME `ichioshi.contentsx.jp`（DNS: お名前.com） |
| お問い合わせ | HubSpot Forms API v3 に `fetch()` で直接POST（埋め込みウィジェット不使用） |
| 解析 | GA4 / Microsoft Clarity（新規発行予定） |
| 広告 | Meta広告 / Google広告 |

### デザインの方針（[DESIGN.md](docs/specs/DESIGN.md) より）

- **白基調** × **明朝＋ゴシック2書体**（編集者的トーン）
- **ピンク〜マゼンタのグラデは"点"で使う**（CTA・1語色変え・細い帯のみ）
- 副アクセントの青は不採用、**色軸は黒系＋ピンク1色**
- Apple/Stripe風の**大きな余白 × 大きい見出し**

---

## 開発ワークフロー

### コード方針

- **HTML/CSS/JS分離**（インライン禁止）
- **同階層相対パス**（`href="css/style.css"` 等。サブディレクトリ化したら絶対パスに切替）
- 機能・動作・URL・共通コンポーネントを変えたら **同一コミット内で該当mdを更新**

### ブランドボイス（厳守）

- 絵文字禁止（SVG／タイポ記号で代替）
- 「Webtoon」表記回避（→「縦スクロール漫画」「縦読み」）
- AI混在比率を書かない（「独自の制作メソッド」として訴求）
- 説明は平易な日本語で

---

## 現在の状態

🚧 **In development**

- ✅ ホーム全11セクション実装済み（2026-09-28 新デザイン案準拠。ヒーロー〜変化・流れはスライド①〜⑦）
- ✅ お問い合わせページ + HubSpot連携実装済み
- ✅ 事例一覧・事例詳細・料金・サービス・コラム・共通フッター実装済み
- ⏳ サービス資料（DL用PDF）の実体は未用意（CTAは暫定でお問い合わせフォームへ）
- ⏳ GitHub Pages 公開設定・GA4 / Clarity の発行
- ⏳ 本番フォントの自前ホスト化（現状は Google Fonts）

詳細は [docs/planning/ROADMAP.md](docs/planning/ROADMAP.md) 参照。

---

## ライセンス

このリポジトリは **コンテンツエックス株式会社の社内プロジェクト**です。コード・コンテンツの著作権は同社に帰属します。
- 第三者製スキル `nextlevelbuilder/ui-ux-pro-max-skill` 系（参照のみ）および同梱の `.claude/skills/3d-scroll-website` は MIT ライセンスです。
- 本リポを参考・引用する場合は出典明記をお願いします。

---

## 参考

- 公式サイト（運営会社）: [contentsx.jp](https://contentsx.jp/)
- 兄弟事業 BizManga: [bizmanga.contentsx.jp](https://bizmanga.contentsx.jp/)
