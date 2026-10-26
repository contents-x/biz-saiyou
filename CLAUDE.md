# ビズ採用（リポジトリ名 recruitx） — Claude Code 作業ガイド

> ビズ採用 採用LP の入口ドキュメント（**2026-09-28 にビズ採用から改名**。その前はリクルートX。リポジトリ名・内部識別子は `recruitx` のまま維持）。**まずここを読み、変更時はどのドキュメントを更新するか [docs/DOC-RULES.md](docs/DOC-RULES.md) で判断する。**

## TL;DR（最優先で守る3点）

1. **同階層相対パス**（`href="css/..."`・`file://`で開ける）・**HTML/CSS/JS分離**・**commit & push は Claude が実施**
2. **絵文字禁止 / 「Webtoon」表記回避（→「縦スクロール漫画」「縦読み」）/ AI混在比率を書かない**
3. 機能・動作・URL・共通コンポーネントを変えたら **同一コミット内で該当mdを更新**（後回し禁止）

## リポジトリ

| 項目 | 値 |
|------|-----|
| サービス | ビズ採用（表示名。旧名ビズ採用・リクルートX／英語表記は使わない） |
| 運営会社 | コンテンツエックス株式会社 |
| 社内プレフィックス | `[R]` = ビズ採用（兄弟: `[C]`=Contents X / `[B]`=BizManga）。GitHubリポジトリ名・クラスプレフィックス等の内部識別子は引き続き `recruitx`/`rx-` |
| ドメイン | `ichioshi.contentsx.jp`（GitHub Pages + CNAME / DNS お名前.com） |
| クラスプレフィックス | `.rx-` / CSS変数 `--rx-*` / localStorage `rx-lang`（表示名変更後も維持。変更しない） |

## WordPress連携（cms.contentsx.jp・⭐スキル必須）

ビズ採用のコンテンツをWPで管理する作業（CPT追加・メニュー・CORS・API）は、**ユーザーレベルスキル `wp-service-onboard` を必ず発動**して進める（「WPに引き込んで」「CPT追加」等で自動発動）。

| 項目 | 値 |
|------|-----|
| WPプラグインのマスター | `/Users/hirasawa4323/Documents/書類 -重要/contentX/web/ContentX_HP/ContentX/wordpress/contentsx-cms/contentsx-cms.php`（**このリポジトリにPHPは無い・置かない**） |
| アクセス権 | `.claude/settings.json` の `additionalDirectories` で ContentX_HP に付与済み。`ContentX/bizmanga/`（301リダイレクト群）は deny で編集禁止 |
| 編集前の必読 | ContentX_HP側の `CLAUDE.md`・`BUGS.md` Pre-flight・`docs/operations/WP-SERVICE-ONBOARDING.md`（スキルの §0b 別ワークスペース実行プロトコルに従う） |
| 本番反映 | お名前.comファイルマネージャーで手動アップロード（コード修正＝本番反映ではない） |

## SEO記事・事例の制作手順（⭐毎回この手順で）

SEO記事（コラム）・採用事例の本文を書くときは、**必ず7ステップワークフロー**で進める:
`/competitive-brief` → `/seo-plan` → `/draft-content` → 画像提案 → `/brand-review` → `/seo-content` → `/seo-page`

- **手順とトンマナの正本**: 非公開のコラム制作リポ（採用ワークスペース直下 `../column-project/`）の `clients/recruitx.md`。作業前に必ず読む
- **事例単位のSEO仕様書**: 同 `clients/recruitx_cases/{slug}.md`（1事例=1MD）。**KW割当マップ `_index.md` を着手前に確認・着手後に更新**（カニバリ防止）
- **SEO戦略・KW割当をこの公開リポに書かない**（公開してよいのはメタの実装値のみ → docs/content/SEO.md）
- 本文の正本はWP（採用事例=rx_case 専用CPT / コラム=共有 `cx_column` に相乗り＝掲載先「リクルートX」にチェック※WP管理画面の項目名は未改名。ビズマンガ/ContentsX と同じ「コラム」メニュー）。**事例は3,000〜5,000字・コラムは7,000字以上**。コラム一覧フロントは `column.html`＋`tools/build-columns.py`（`/columns?site=recruitx` を取得→静的生成）。**GitHub Actions `build-columns.yml` が1時間ごとに自動で取り込み・公開**（手動実行も可）。`column.html` の BUILD マーカー内と `column/` 配下は手で直さない（次のビルドで上書き）

## エンジニアリング規約（Contents X 系共通・厳守）

- **リンクのパス**: 常に**各ページからの相対パス**で書く（ルート直下は `href="css/style.css"`、サブディレクトリ `case/{slug}/` からは `href="../../css/style.css"`）。これで `file://`・ローカルサーバー・GitHub Pages いずれでも解決する。⚠️**ルート絶対パス（`/css/...`・`/case/...`）は使わない**: 本番は GitHub Pages のプロジェクトページ `josawa2255.github.io/recruitx/`（サブパス配信）のため、`/` 始まりだと `/recruitx/` が抜けて全リンク・CSSが壊れる（2026-06-13 事例詳細で発覚・BUGS.md）。相対なら将来 ichioshi.contentsx.jp をルート稼働させても両対応。build-cases.py も相対で出力する
- **HTML/CSS/JS分離**: インラインCSS/JS禁止、最初から外部ファイルに分ける
- **commit & push は Claude 側で実施**
- バグを直したら [BUGS.md](BUGS.md) に1行追記

## ブランドボイス（厳守）

| ルール | 内容 |
|--------|------|
| 絵文字禁止 | SVG / タイポ記号（+ − — 「」）で代替（絵文字多用はAI製LPの兆候） |
| 「Webtoon」表記回避 | ユーザー可視は「縦スクロール漫画」「縦読み」。CSS/JS内部識別子は可（NAVER商標対策） |
| AI混在比率を書かない | 「7割人間3割AI」等は禁止。「独自の制作メソッド」として訴求 |
| 平易な日本語で | 変数名・コード用語の羅列をせず自然な日本語で説明 |

## ドキュメント・ルーティング

| 何を変えたか | 更新するファイル |
|---|---|
| 機能・ページ・URL・コンポーネント | [docs/specs/SPEC.md](docs/specs/SPEC.md) |
| 色・フォント・角丸などデザイントークン | [docs/specs/DESIGN.md](docs/specs/DESIGN.md) |
| 全デバイス表示の崩れ防止ルール | [docs/specs/DEVICE-RULES.md](docs/specs/DEVICE-RULES.md) |
| メタ・構造化データ・内部リンク | [docs/content/SEO.md](docs/content/SEO.md) |
| WP・クラウド・外部サービスID・触禁領域 | [docs/operations/INFRA.md](docs/operations/INFRA.md) |
| やること・拡張計画 | [docs/planning/ROADMAP.md](docs/planning/ROADMAP.md) |
| 事例フロント実装（詳細ページ・ビルド）の要件 | [docs/planning/CASE-FRONTEND-PLAN.md](docs/planning/CASE-FRONTEND-PLAN.md) |
| 客先ごとの採用LP（制作サンプル `/sample/{客先}/`）の仕様・素材の作り方 | [docs/specs/SAMPLE-LP.md](docs/specs/SAMPLE-LP.md) |
| 学び・引き継ぎ知識 | [docs/planning/KNOWLEDGE.md](docs/planning/KNOWLEDGE.md) |
| ルール化候補（自動収集の下書き） | [docs/planning/RULE-CANDIDATES.md](docs/planning/RULE-CANDIDATES.md) |
| お問い合わせのHubSpot連携仕様 | [docs/operations/HUBSPOT-CTA-HANDOFF.md](docs/operations/HUBSPOT-CTA-HANDOFF.md) |
| バグと再発防止 | [BUGS.md](BUGS.md) |
| **md運用ルール・スキル使用・自動修整の判断** | [docs/DOC-RULES.md](docs/DOC-RULES.md) ⭐ |
| **Claude公式の最新推奨の追従状況** | [docs/operations/BEST-PRACTICE-WATCH.md](docs/operations/BEST-PRACTICE-WATCH.md) ⭐ |
| GitHubに公開する概要・技術スタック・現在の状態 | [README.md](README.md) |

迷ったら [docs/DOC-RULES.md](docs/DOC-RULES.md) を見る。
