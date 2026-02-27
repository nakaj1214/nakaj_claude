# Project overview
- このリポジトリはDocker(WSL2)上で開発するWebアプリ。
- 主な構成: Laravel(v10系), PHP, MySQL, フロントはJavaScript(jQuery/Datatables系)。
- 目的: 仕様確認→実装→テスト→差分レビュー→PR作成までを短い往復で回す。

# Environment assumptions (Windows + WSL2 + Docker)
- コマンドは原則WSL内で実行する(Windows側パス/mnt/c配下でDBの高I/Oを直接扱う運用は避ける)。
- Docker composeで起動している前提。アプリ/DB/必要ならnodeの各コンテナがある。
- この環境は tmux 3ペインで動作する:
  - pane 0 (左上): Gemini CLI
  - pane 1 (左下): Codex CLI
  - pane 2 (右): Claude Code (自分)

# Must-follow workflow
1. 変更前に影響範囲を特定する
   - 触るファイル一覧、関連するルート/コントローラ/ビュー/JSを先に列挙。
2. 最小の変更で通す
   - 既存の構造(モジュール分割やファイル配置)を極力崩さない。
3. テスト/再現/ログで裏を取る
   - 可能なら自動化(Playwrightなど)を優先。難しい場合は再現手順を明文化。

# Tooling rules (MCPを使える時)
- 仕様/ライブラリ/CLIの使い方が絡む場合:
  - 必ずContext7等で「最新版の使い方」を確認してから提案・実装する。
- 画面操作の再現/回帰確認が絡む場合:
  - Playwrightで再現手順をスクリプト化して、期待結果と差分を出す。
- Git操作が絡む場合:
  - 差分とコミット単位で説明し、意図しない変更が混ざっていないか必ず確認する。
- DB操作が絡む場合:
  - 原則read-onlyの確認(SELECT/SHOW)で切り分け。
  - 破壊的変更(UPDATE/DELETE/MIGRATE等)は実行前に要約して確認を求める。

# Laravel-specific conventions
- バリデーションはForm Requestを使う(コントローラ内のinline validateは避ける)。
- 関数シグネチャの返り値型宣言は付けない(ユーザーの規約)。
- 既存の命名/責務分割を尊重し、共通化は段階的に行う。

# Frontend conventions (JS/jQuery)
- 1行ifや1行に詰めた条件分岐は避け、ブロックで書く。
- 既存のoverlay/suggest等のモジュール構造を壊さず、差分を最小化する。

# What to include in every answer
- 変更点の要約(箇条書き)
- 触ったファイル一覧
- 実行した/推奨するコマンド
- リスク(影響範囲/後方互換/データ破壊)と回避策

## Default Policy
ユーザーから「機能追加/削除/バグ修正」依頼を受けたら、原則この順で進める:

1) Geminiで分析を取得する（/gemini-analyze を自分で実行）
   - 出力は FACTS / ROOT CAUSE / MIN TESTS / RECOMMENDED FIX

2) 自分(Claude/Opus)が設計する
   - DECISIONS / PATCH PLAN(ファイル別) / TEST PLAN / RISKS / Acceptance Criteria を必ず書く

3) Codexで設計レビュー（/codex-review を自分で実行）
   - Must/Should/Could
   - Mustは Rationale + Acceptance Criteria が必須

4) Mustが0になるまで、設計を修正して 3) を繰り返す

5) Geminiで実装（/gemini-implement を自分で実行）
   - unified diff
   - minimal diff only

6) Codexで実装レビュー（/codex-review を自分で実行）
   - Mustが0になるまで修正を回す
   - 高リスクで判断が必要な時だけ自分で設計からやり直す