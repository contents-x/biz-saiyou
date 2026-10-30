# INFRA — 開発環境・外部サービス・触ってはいけない領域

> 「どのクラウドを使っているか」「外部サービスの種別」「触ると壊れる領域はどこか」の重要情報を集約。**実IDは非公開**（公開リポのため。実値は `INFRA-PRIVATE.md`／gitignoreで保管）。

## TL;DR

イチ推し採用は GitHub Pages + CNAME `ichioshi.contentsx.jp`、DNSはお名前.com。GA4/Clarityは**新規発行**、Google広告タグとHubSpot Portalは既存流用可（実IDは非公開ファイル参照）。

## 1. 会社情報

| 項目 | 内容 |
|------|------|
| 運営会社 | コンテンツエックス株式会社 / Contents X Co., Ltd. |
| 所在地 | 非公開（[INFRA-PRIVATE.md](INFRA-PRIVATE.md)） |
| コピーライト | © Contents X Co., Ltd. 2026 All rights reserved. |

## 2. デプロイ・インフラ

| 項目 | 値 |
|------|-----|
| ホスティング | GitHub Pages（既存2サイトと同方式） |
| ドメイン | `ichioshi.contentsx.jp`（CNAME）— **2026-06-28 改名移行**（DNS追加済 → push/Pages設定/Enforce HTTPS で切替）。旧 `recruitx.contentsx.jp`（2026-06-13開通）は301元として保持 |
| DNS | お名前.com（CNAME `recruitx`→`josawa2255.github.io`） |

### サブドメイン開通手順（ランブック・他サービスにも流用可）

GitHub Pages のプロジェクトページに `*.contentsx.jp` サブドメインを割り当てる標準手順。`recruitx.contentsx.jp` 開通（2026-06-13）で実証済み。新サービスでも同じ流れ。

1. **お名前.com で CNAME レコード追加** — ⚠️**入口を間違えやすい（2026-06-28 ハマった）**
   - ✅ **正しい入口**: [navi.onamae.com](https://navi.onamae.com)（お名前.com Navi）→ **ドメイン** → **DNS（DNS関連機能の設定）** → 対象 `contentsx.jp` → **DNSレコード設定** → 「DNSレコードを追加」。**既存の `recruitx`（CNAME → `josawa2255.github.io`）が一覧に見えれば、その画面が正解。**
   - ❌ **罠**: 「**レンタルサーバーコントロールパネル**」側のDNS編集画面は**別物・無効**。contentsx.jp は `dnsv.jp` 管理（レンタルサーバー不使用）のため、そちらでは赤字「**ご利用サービス以外のネームサーバーです**」と表示され、`recruitx` 等の実レコードも一覧に出てこない。**recruitx が見えない画面で追加しても効かない**ので、見えない＝入口違いと判断して Navi 側へ。
   - 入力値 — ホスト名: `<サブドメイン>`（例 `recruitx`。`.contentsx.jp` は自動付与。フルFQDNを書かない） / TYPE: `CNAME` / VALUE: `<GitHubユーザー名>.github.io`（例 `josawa2255.github.io`。末尾ドット任意） / TTL: `3600` / 状態: 有効
   - 「追加」→「確認画面へ進む」→「設定する」。伝播は数分〜1時間
   - ※ネームサーバーは `01〜04.dnsv.jp`。確認: `dig contentsx.jp NS +short` / レコード存否: `dig <サブドメイン>.contentsx.jp +short`
2. **GitHub Pages でカスタムドメイン設定**（Settings → Pages）
   - Custom domain に `<サブドメイン>.contentsx.jp` を入力して Save → リポ直下に `CNAME` ファイルが自動生成される（手動作成不要）
   - 「DNS Check in Progress」→ 伝播後に緑 ✓。証明書は自動発行（approved になる）
3. **Enforce HTTPS にチェック**（証明書発行後に押せるようになる）。これで `http://` → `https://` 301リダイレクト＝常時SSL
4. **検証コマンド**:
   - `dig <サブドメイン>.contentsx.jp +short` → `<user>.github.io.` ＋ GitHub IP `185.199.108-111.153` が返る
   - `gh api repos/<owner>/<repo>/pages` → `cname` 一致・`https_enforced: true`・証明書 `state: approved`
   - `curl -sI -o /dev/null -w "%{http_code} -> %{redirect_url}\n" http://<サブドメイン>.contentsx.jp/` → `301 -> https://...`

**注意**: 当リポは相対パス設計のため、サブパス配信（`josawa2255.github.io/recruitx/`）でもルート配信（`ichioshi.contentsx.jp/`）でもリンク・CSSが壊れない。絶対パス（`/css/...`）に戻すとサブパス時に壊れる（→ CLAUDE.md・BUGS.md）。

## 3. 外部サービス（種別とイチ推し採用方針）

| サービス | 実IDの所在 | イチ推し採用方針 |
|----------|---------|----------------|
| GA4 | 測定ID `G-S2RDKPM1LE`（本番HTMLに露出＝秘匿不要）／プロパティID等は[INFRA-PRIVATE.md](INFRA-PRIVATE.md) | **2026-06-14 全ページ実装済**（自己ホスト `js/ga4.js`＋ライブラリは googletagmanager／strict CSP 維持のため `'unsafe-inline'` は足さず CSP に GA ドメインのみ追記。事例詳細は `tools/templates/case-detail.html.tpl` 経由で22件反映） |
| Microsoft Clarity | 非公開（同上） | **新規発行** |
| Google広告タグ | 非公開（同上）／**既存タグを両サイト設置済** | 既存を流用可 |
| HubSpot | 非公開（同上・[HUBSPOT-CTA-HANDOFF.md](HUBSPOT-CTA-HANDOFF.md) 参照） | **共通フォーム流用**（送信元タグ `ビズ採用` で識別。2026-10-31 のイチ推し採用への改名では変更を保留し旧名のまま） |
| WordPress API | 非公開（同上） | 必要時に利用（コラム/制作事例CMS） |
| Google Search Console | recruitx を登録済（URL-prefix `https://recruitx.contentsx.jp/`・siteOwner・sitemap送信済 2026-06-14）。**改名移行に伴い `ichioshi.contentsx.jp` を新規プロパティ登録＋sitemap再送信が必要（旧recruitxは301監視用に残す）** | 索引促進は case.html を最優先で手動申請（→22詳細を芋づる発見） |

### WordPress（WP）運用メモ
- CMSは社内WP環境（実URL非公開）。**PHPローカルがマスター**、お名前.comファイルマネージャーでアップロード。
- **採用事例CMS（2026-06-12 WP側実装済み）**: case.html のカード＋「詳しく見る」詳細ページをWPの専用投稿タイプ `rx_case` で管理する。
  - API: 一覧 `GET {API}/cases` / 個別 `GET {API}/cases/{id}`（詳細本文 `content` つき）
  - フィールド: 会社名（タイトル）/ タグ（`rx_case_tag`・チェックボックス選択）/ 成果概要 / メイン画像（アイキャッチ＋フォーカルポイント `focal.x/y` → フロントは `object-position: x% y%` で再現）/ 実績数値 `stats[{label,value,unit,arrow:up|down|none}]` 最大3個可変
  - 詳細ページURLは `/case/{slug}` 予定（サブディレクトリ化に伴い、該当ページはパス規約を絶対パスへ切替）
  - フロント実装（fetch JS・静的ビルド・日次cron）は未着手。WP側手順の正本は ContentX_HP 側 `docs/operations/WP-SERVICE-ONBOARDING.md`
- **コラムの自動取り込み（2026-10-19）**: WP の共有コラム `cx_column` のうち掲載先「リクルートX」の記事を、GitHub Actions `.github/workflows/build-columns.yml` が**15分ごと（毎時7・22・37・52分）**に `tools/build-columns.py` で静的ページに書き出し、差分があれば `github-actions[bot]` が main に push → GitHub Pages が公開する。WP で公開・修正・非公開にした内容は通常15分〜数十分で反映（GitHub の混雑で遅れることがある。2026-10-27 までの1時間ごとの設定では、実際は2〜7時間おきにしか動いていなかった）。すぐ反映したいときは GitHub の Actions 画面 →「Build Column Pages」→「Run workflow」
  - push のためワークフローに `permissions: contents: write` を明示している（このリポの既定トークンは読み取り専用）
  - 2026-10-22 19:10〜10-23 10:30（JST）の約15時間、WP の API が GitHub Actions からの取得を **403** で拒否し、5回失敗した（その後は自然に回復。サーバー側のアクセス制限と推定・原因は未確認）。失敗中はサイトが前回の内容のまま止まるだけで、壊れはしない。続くようならサーバー側の設定を WP 担当に確認する
  - ⚠️ 公開リポの定期実行は、**60日間リポに動き（コミット等）が無いと GitHub が自動で止める**。記事の更新が長く無い時期のあとは Actions 画面で「Build Column Pages」が無効になっていないか確認し、止まっていたら Enable workflow
  - ⚠️ **事例の `build-cases.yml` は 2026-09-27 から毎日失敗中**（push が 403＝上の permissions が無い）。ただし WP の事例本文はまだ旧名「リクルートX」のため、push が通ると22ページの「イチ推し採用」が戻る。**WP 側の表記を直してから permissions を足す**（[ROADMAP](../planning/ROADMAP.md)・[BUGS](../../BUGS.md) 2026-10-19）
- **ホームの制作実績の読み画面（2026-10-06）はWPの制作事例 works のページ画像を直接表示している**（`js/works-viewer.js` の `MANGA`。対象 `hana` / `gaudia-3` / `birdman`。works はビズマンガ・ContentsX と共有の投稿タイプ）。⚠️ WPでこれらの作品のページ画像（メディア）を削除・差し替えると、イチ推し採用のホームで画像が出なくなる／古いままになる。差し替えたら `MANGA` のURLも更新する
  - 公開API `/contentsx/v1/*` の CORS は `ichioshi.contentsx.jp` のみ許可（`josawa2255.github.io` と `file://` は不可・2026-10-06 確認）。そのためフロントから実行時にAPIを読まず、URLを静的に持つ（`<img>` の読み込みは CORS の影響を受けない。`index.html` の CSP `img-src` は `https://cms.contentsx.jp` を許可済み）

## 4. 触ってはいけない領域 ⛔（既存資産を参照・流用する際の地雷）

具体的なパス・GitHub Actions等は [INFRA-PRIVATE.md](INFRA-PRIVATE.md) 参照。要点のみ:

- BizMangaの**外部配布済みURL**は変更禁止
- **301リダイレクト用HTML**は削除禁止
- **共有画像フォルダ**の画像削除は、両リポgrepで参照確認してから
- 既存サイトの**日次ランクトラッカー**（GitHub Actions）は触らない

## 5. 公開ポリシー（このリポについて）

このリポジトリは public のため、**運用機微情報（外部サービスID・触禁領域の具体パス）は本ファイルから外し**、`INFRA-PRIVATE.md`（gitignored）に集約しています。
- リポを clone した開発者は、別ルート（社内Wiki等）から `INFRA-PRIVATE.md` を取得して `docs/operations/` 配下に配置すること
- 新規にIDが必要な作業をする場合は、コミット対象に含めないよう注意
- ランタイムJS（`js/main.js`）には HubSpot ID等が**ハードコードで残っている**（API呼び出しに必要なため）。これはブラウザのview-sourceで誰でも閲覧可能、というのは仕様
