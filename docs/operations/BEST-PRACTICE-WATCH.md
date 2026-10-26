# BEST-PRACTICE-WATCH — Claude公式の推奨を追従する

> Claude Code / Anthropic 公式の最新推奨（ドキュメントの書き方・行数目安・スキル設計など）を**週次で追従**し、変化があればこのリポのmdとルールに反映するための台帳。あわせて週次でハブmd（CLAUDE.md / DOC-RULES.md）の健康監査も行う。

## TL;DR

週次の定期エージェントが公式ドキュメントを確認 → 下の「追跡中の推奨値」と差分があれば、この表と [../DOC-RULES.md](../DOC-RULES.md) を更新し変更ログに記録 → 影響するmd/skillを通知。**md自動更新OK・skillは提案のみ**（[../DOC-RULES.md](../DOC-RULES.md)）。

## 追跡中の推奨値

| 項目 | 現在の値 | 出典 | 最終確認 |
|------|---------|------|---------|
| ドキュメント1ファイルの行数目安 | 200行以下 | [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) | 2026-10-26 |
| CLAUDE.md の書き方 | 簡潔・重要情報を上・TL;DR | [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices) | 2026-10-26 |
| Skill の設計 | SKILL.md は短く・フロントマター付き、詳細は references/ に分離（段階的開示） | [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices) | 2026-10-26 |
| リンク書式（VS Code拡張） | `[text](path)` クリック可能形式 | — | 2026-10-26 |

> ↑ 値は初期推定を含む。週次ジョブが公式の一次ソースで検証し、URLと値を確定・更新する。

## 週次ジョブの動作

定期エージェント（毎週月曜9:00 JST）は**パートA・Bを実行し1つのPRにまとめる**。

**パートA: 公式追従**
1. 公式ドキュメント（Claude Code / Agent SDK のベストプラクティス）を取得
2. 上表の各項目と比較し、変化を検出
3. 変化あり → このファイルの表と変更ログを更新、[../DOC-RULES.md](../DOC-RULES.md) の該当ルールを更新（md自動）
4. スキル本体への影響は**変更案を提示**（自動では書き換えない）

**パートB: ハブmd健康監査**（[CLAUDE.md](../../CLAUDE.md) / [DOC-RULES.md](../DOC-RULES.md)）
5. 鮮度・構造・重複・リンク・可読性/行数を点検し、ズレを修正
6. 全mdを列挙し、ハブのルーティング表と照合 → **孤立md**（表に未登録）と **stale参照**（実在しないmdへのリンク）を検出・修正
7. 問題ゼロでも「全項目クリア」とわかるPRを出す（PRレビューが安全弁）

## 確認すべき一次ソース（候補）

- Claude Code ドキュメント（docs.claude.com）
- Claude Agent SDK / スキル設計ガイド
- Anthropic エンジニアリングブログのドキュメント運用記事

## 変更ログ

| 日付 | 変わった項目 | 旧→新 | 反映したファイル |
|------|------------|--------|----------------|
| 2026-05-24 | 初期セットアップ | — | 台帳作成 |
| 2026-10-26 | 全項目の最終確認日・出典URL更新（値は変化なし）。新機能メモ: `/doctor prompt-audit`（CLAUDE.md自動監査）・`AGENTS.md` サポート・`.claude/rules/`（パス別スコープルール）が公式ドキュメントに追記 | 変化なし | BEST-PRACTICE-WATCH.md |
