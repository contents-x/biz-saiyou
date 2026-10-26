# DOC-RULES — md運用の頭脳

> このリポのドキュメント運用ルールを1枚に集約。「どの変更でどのmdを更新するか」「いつスキルを使うか」「自動で修整してよい範囲」を定義する。**運用判断に迷ったら必ずここを見る。**

## TL;DR

1. 変更したら**同一コミット内**で対応mdを更新（下の更新ルーティング表）
2. md（リポ内）は**自動更新OK**、スキル本体（`~/.claude/skills`）は**提案のみ**（勝手に書き換えない）
3. 1ファイル**200行以下**を目安（出典と最新値は [BEST-PRACTICE-WATCH.md](operations/BEST-PRACTICE-WATCH.md)）
4. 構成は単一LPのうちフラット寄り。**分割トリガー**を満たしたら枝分かれ

## 更新ルーティング（変更 → 更新するmd）

| 変更の種類 | 更新先 |
|---|---|
| 機能追加・動作変更・URLパラメータ・共通コンポーネント | [specs/SPEC.md](specs/SPEC.md) |
| 客先ごとの採用LP（`/sample/{客先}/`・`css/sample-lp.css`・`js/sample-lp.js`） | [specs/SAMPLE-LP.md](specs/SAMPLE-LP.md) |
| 色・フォント・角丸・余白などデザイントークン | [specs/DESIGN.md](specs/DESIGN.md) |
| デバイス表示・レスポンシブ・アクセシビリティ規則 | [specs/DEVICE-RULES.md](specs/DEVICE-RULES.md) |
| メタタグ・構造化データ・内部リンク・KW戦略 | [content/SEO.md](content/SEO.md) |
| 外部サービスID・WP・クラウド・DNS・触禁領域 | [operations/INFRA.md](operations/INFRA.md) |
| タスク進捗・拡張計画 | [planning/ROADMAP.md](planning/ROADMAP.md) |
| 新しい学び・トラブル解決・引き継ぎ知識 | [planning/KNOWLEDGE.md](planning/KNOWLEDGE.md) |
| ルール化候補（逆フックが自動収集） | [planning/RULE-CANDIDATES.md](planning/RULE-CANDIDATES.md) |
| HubSpot連携の実装仕様 | [operations/HUBSPOT-CTA-HANDOFF.md](operations/HUBSPOT-CTA-HANDOFF.md) |
| 直したバグ | [/BUGS.md](../BUGS.md) |
| 規約・ブランドボイス・ルーティング自体 | [/CLAUDE.md](../CLAUDE.md) |
| GitHubの概要・技術スタック・現在の状態 | [/README.md](../README.md) |

「今回は小さいから」「後でまとめて」は禁止。

## コミット時のmd同期ガード（フック）

[`.claude/settings.json`](../.claude/settings.json) に PreToolUse フックを設定済み。**`git commit` の直前**に、ステージされたコード（`*.html` / `*.css` / `*.js`）があるのに `docs/` 配下や `*.md` が未ステージなら、**コミットをブロック**して該当mdの更新を促す。

- 発火するのは `git commit` 時のみ。コードと一緒にmdをステージしていれば**沈黙**して通過する。
- 意図的にコードだけコミットしたい稀なケースは、`BUGS.md` 等を併せて更新するか `/hooks` で一時無効化する。

### なぜこの形にしたか

| 採用した設計 | 理由 |
|---|---|
| **編集のたび**ではなく**コミット時**に発火 | 編集のたびに注入するとリマインドがコンテキストに積み重なり**トークンを浪費**し、機能の作業途中（まだmd更新の段階でない時）にも鳴ってノイズになる。コミットは「変更が一区切りする」自然な節目で、「同一コミット内でmd更新」というルールとも一致する。 |
| 「コードのみステージ・md未ステージ」の時**だけ**発火 | きちんとmdを更新できている時は一切鳴らさず、消費をほぼゼロにするため。鳴るのは取りこぼした瞬間だけ。 |
| リマインドではなく**ブロック** | md更新を「同一コミット内」に確実に収めるため。警告だけだとコミット後になり、ルールが形骸化する。 |
| ハーネス実行の**フック**で担保（md記述だけに頼らない） | 「うっかり忘れ」は人/AIの判断に任せると必ず漏れる。決定論的に発火するフックがトリガーを保証し、どのmdに何を書くかの**判断と編集はClaude**が担う二段構え。 |

## 新規md作成時のハブ同期（フック）

[`.claude/settings.json`](../.claude/settings.json) に PostToolUse フックを設定済み。**git未追跡の `.md` を新規作成した直後**に、「ハブmd（ルート [CLAUDE.md](../CLAUDE.md) のドキュメント・ルーティング表 と この DOC-RULES.md の更新ルーティング表）へ参照を追加すべきか判断せよ」という指示を注入する。判断と実際の追記はClaudeが行う。

- 発火するのは**新規（未追跡）の `.md` を Write した時のみ**。既存mdの上書き・md以外のファイルでは沈黙。
- 新規mdを作ったら、孤立させずハブmdの表に必ず登録する（探せないドキュメントは無いのと同じ）。

### なぜこの形にしたか

| 採用した設計 | 理由 |
|---|---|
| コミット時ではなく**作成直後**に即発火 | 新規md作成は稀なイベントでトークン負荷が小さく、ハブ登録は作りたてのその場でやる方が正確。頻発するコード編集（→コミット時）とはイベント特性が違うので扱いを分ける。 |
| **未追跡の`.md`新規作成時だけ**発火 | 既存mdの編集のたびに鳴ると無駄。本当に新しく増えた時だけハブ同期すればよい。 |
| 追記内容は注入せず**Claudeが判断して書く** | 「どの表に・どんな説明文で」入れるかは文脈判断が要る。シェルで機械的に追記すると質の低い項目になる。フックはトリガー役に徹する。 |
| ハブmdを**単一の入口**に保つ | CLAUDE.md / DOC-RULES.md の表だけ見れば全mdに辿り着ける状態を維持するため。新規mdの登録漏れ＝孤立を防ぐ。 |

## その他の自動化フック

| フック | イベント | 動作 |
|---|---|---|
| 行き詰まり検出 [stuck-detect.sh](../.claude/hooks/stuck-detect.sh) | PostToolUse(Edit/Write) | 同じファイルを5回連続編集したら「/clearや別アプローチを」と警告 |
| ルール化候補 [rule-candidate.sh](../.claude/hooks/rule-candidate.sh) | UserPromptSubmit(async) | ユーザー発言に繰り返し指摘のシグナル（毎回/何度も/ルール化 等）があれば、**逆フック**で `claude -p` が「ルール化すべきか」を判断し [planning/RULE-CANDIDATES.md](planning/RULE-CANDIDATES.md) に候補を追記 |

### 逆フック（hookからclaude -pを叩く）の安全則

`claude -p` をフックから呼ぶ場合は必ず:
1. **再帰ガード**: 全フック先頭に `[ -n "$CLAUDE_REVERSE_HOOK" ] && exit 0`。逆フック側は `CLAUDE_REVERSE_HOOK=1` を export して呼ぶ（呼ばれたclaudeのフックが再発火する無限ループを防ぐ）。
2. **コスト上限**: `--max-budget-usd` を付ける。
3. **非ブロック**: フックは `async: true` で背景実行。
4. **事前フィルタ**: 毎回claudeを呼ばない（キーワード等で絞ってから）。
5. **ハブ本体は直接書き換えず候補止まり**: 自動編集はRULE-CANDIDATES等の下書きに限定し、本体への昇格は人がレビュー。

## スキル使用の判断

| 状況 | 使うスキル |
|---|---|
| md群の整理・監査・同期・stale点検 | `md-maintainer` |
| SEO監査・コンテンツ品質・スキーマ・サイトマップ | `seo-*`（seo-audit / seo-technical / seo-schema 等） |
| 公開前のローカル表示確認 | `webapp-testing` / `run` |
| 公式の最新推奨の追従（週次） | [BEST-PRACTICE-WATCH.md](operations/BEST-PRACTICE-WATCH.md) の定期ジョブ |

迷ったら「専用スキルがあるなら使う、なければ手作業」。

## 自動修整の範囲（⭐確定ポリシー）

| 対象 | 自動修整 | 理由 |
|---|---|---|
| リポ内の md（記録・ルール類） | **自動OK** | 出典付きで追記・修正、差分は通知 |
| `~/.claude/skills` のスキル本体 | **提案のみ**（承認制） | 全プロジェクト影響のため勝手に書き換えない |
| コード（HTML/CSS/JS） | 提案のみ | 仕様変更は人が判断 |

自動更新時は「何を・なぜ・出典」を変更サマリで残す。

## ファイルサイズ・構造ガイド

- 1ファイル**200行以下**目安（超えたら分割を検討。最新の推奨値は BEST-PRACTICE-WATCH が追従）
- 各mdの先頭に**TL;DR（3行以内）**、重要情報を上に
- H1は1つ、見出しは3階層以内、リンクは `[text](path)` 形式

## 分割トリガー（フラット → 枝分かれ）

以下のいずれかを満たしたら該当ディレクトリ内で分割する:

- **ページが5枚超** → `specs/` にページ別 SPEC を追加
- **知識が肥大**（KNOWLEDGE が200行超 or 話題が3系統以上）→ `planning/knowledge/` に枝分かれ
- **コピー差し替えが頻発** → `content/COPY.md` を新設
- **多言語化** → i18n辞書管理を `content/` に独立
- **公開運用が定常化** → `operations/CHECKLIST.md` `operations/ANALYTICS.md` を新設

将来像（拡張時の到達点）は兄弟リポ ContentX_HP の `docs/` 構成に準拠。
