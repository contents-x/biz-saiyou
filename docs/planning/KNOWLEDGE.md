# KNOWLEDGE — 学び / 引き継ぎ知識

> 親会社・兄弟事業の前提と、開発中に得た学びを蓄積。**枝分かれ前提**: 200行超 or 話題3系統以上になったら `knowledge/` に分割（[../DOC-RULES.md](../DOC-RULES.md)）。

## TL;DR

イチオシ採用はコンテンツエックス（Contents X / BizManga を運営）の新サービス。**「伝わる設計」**が事業の軸。デザインは新規だが、ブランドボイス・デバイス品質・エンジニアリング規約は兄弟事業から継承する。

## 1. 会社・事業の前提

- 運営: コンテンツエックス株式会社（[../operations/INFRA.md](../operations/INFRA.md) に詳細）
- 既存サービス: **Contents X**（contentsx.jp / コーポレート・タグライン「伝える」を、再発明する）、**BizManga**（bizmanga.contentsx.jp / ビジネス向け縦スクロール漫画制作）
- 新サービス: **イチオシ採用**（ichioshi.contentsx.jp / 採用LP・デザイン新規）

## 2. コア思想（メッセージ設計の下敷き）

- 「問題はコンテンツの量ではない。届くかどうか。」
- 「埋もれていた物語に、光を当てる。」
- 人は説明ではなく共感で動く、という前提の「伝わる設計」

## 3. なぜこのルールなのか（背景）

| ルール | なぜ |
|--------|------|
| 絵文字禁止・「Webtoon」回避・AI比率を書かない | AI製LPに見えない / NAVER商標リスク回避（[/CLAUDE.md](../../CLAUDE.md)） |
| 絶対パス・HTML/CSS/JS分離 | サブディレクトリ404防止 / 後の作業者が迷わない |
| デバイス16ルールの継承 | 「PCでキレイ・スマホで崩れる」を恒久的に防ぐ（[../specs/DEVICE-RULES.md](../specs/DEVICE-RULES.md)） |

## 4. 参考: 兄弟事業のトーン（流用しない・参照まで）

- Contents X: Cyber Green `#6fc31c` 系の硬質ミニマル、本文 Noto Sans JP、ボタン角丸24px
- BizManga: オレンジ `#EB5200` の親しみトーン、見出し RocknRoll One、ボタンpill(50px)

## 5. 開発中の学び

<!-- 新しい知見・トラブル解決をここに追記。系統が増えたら見出しで分け、肥大したら knowledge/ へ枝分かれ -->

### WP の内容を GitHub Actions で静的に書き出すときの勘所（2026-10-19）

- WP の公開API（`/contentsx/v1/*`）の CORS は本番ドメインだけ許可のため、ブラウザから実行時に読まず、Actions でビルドして HTML を push する（事例・コラム共通）
- Actions の「成功」は push できた証拠ではない。差分が無い日は push しないので成功に見え、差分が出た日に初めて権限不足（403）が出る。自動 push するワークフローには `permissions: contents: write` を書き、初回は手動実行で push まで見る
- WP 側の本文が古いまま（例: 旧サービス名）だと、ビルドが通った瞬間にサイトを手直しした分が巻き戻る。止まっていたビルドを直す前に、`python3 tools/build-*.py` をローカルで回して差分を読む
- `GITHUB_TOKEN` で push したコミットは別のワークフローを起動しないので、無限ループ防止の `[skip ci]` は要らない
- 公開リポの定期実行は、60日間リポに動きが無いと GitHub が自動で無効にする

### クロスOS表記ズレの正体と対策（2026-05-24 調査）

BizManga制作で「Mac/Win/iPhone/Androidで表記がずれる」問題が判明。徹底調査の結論を [../specs/DEVICE-RULES.md](../specs/DEVICE-RULES.md) §16 にルール化。要点:

- **原因は3層**：① 未読込時のOS別フォント置換（Mac=ヒラギノ/Win=游ゴシック・メイリオ/Android=Noto・**主因**）② 縦メトリクスの読み元がOSで違う（macOS=`hhea` / Win・Android=`OS/2 Win`）③ ラスタライズ差（ClearType vs グレースケール）。**③はCSSで統一不可**。
- **対策の本丸は「Webフォントを自前ホスト(WOFF2)で固定 + 和文サブセット」**。これで①がほぼ消える。比率(%)配置は装飾要素には有効だが、**文字を含む要素では逆効果**（フォント差で即はみ出す）→ 文字は `clamp()`、構造は Flex/Grid。
- メトリクス上書き（`size-adjust` 等）は**主に欧文向け**で和文は効果限定的・Safariは `size-adjust` のみ対応。CLS対策としては有効。
- **DevToolsのレスポンシブ表示では検出不可**（自分のOS上で描画するため）。Win ClearType / 本物のSafari は実機 or 実機クラウド（BrowserStack/LambdaTest）でしか確認できない → §2に追記。
- 出典: web.dev(font best practices / css size-adjust)、Every Layout、Defensive CSS、Playwright docs、MDN、ICS MEDIA 他。
