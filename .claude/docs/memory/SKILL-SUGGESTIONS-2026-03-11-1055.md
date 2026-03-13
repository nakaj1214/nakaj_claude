---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

# スキル候補レポート — 2026-03-11 10:55

## 検出されたパターン

- `create-proposal` → `create-plan` → `implement-plans` の3段階パイプラインを毎回手動でトリガー（ユーザーもスキル化を質問）
- Blade ファイルを編集後に画面が変わらず、`php artisan view:clear` でキャッシュクリアして解決（2回以上発生）
- Bootstrap の `btn-*` クラスに hover/focus 効果が残り、「ホバーを無効化して」と複数回指摘
- インライン `<script>` を外部 JS ファイルに移行する作業が多数ファイルで発生（9ファイル）
- UI 要素（`daily_items_panel`）の DOM 配置を段階的に修正（`components_title` 内 → `component_area` 外 → `switch_content` 外）

---

## スキル候補

| スキル名 | トリガー条件 | 内容 | 優先度 |
|---------|------------|------|--------|
| `prompt-to-impl` | 「prompt.mdから実装して」「一気通貫で実装して」「create-proposalからimplementまで」 | `prompt_N.md` を引数で受け取り、create-proposal → create-plan（Codex レビューループ）→ implement-plans を自動的に連鎖実行するオーケストレーションスキル。`propose-one` の完全自動版 | 高 |
| `blade-cache-clear` | 「画面が変わらない」「変更が反映されない」「何も変わってない」Blade ファイル編集後 | `docker exec blade_management_laravel php artisan view:clear` を実行し、必要に応じて `route:clear` / `config:clear` も実行。実行結果をユーザーに報告 | 高 |

---

## エージェント候補

| エージェント名 | ユースケース | 専門化内容 | 優先度 |
|--------------|------------|-----------|--------|
| `inline-js-extractor` | Blade ファイル内のインライン `<script>` を外部 JS ファイルに移行する作業 | Blade ファイルをスキャンして `<script>` ブロックを検出し、適切な外部 JS ファイルパス（`pages/`, `components/`, `debug/`）を決定して移行。`@push('scripts')` への読み込み追加も行う | 中 |

---

## フック候補

| フック種別 | トリガー | アクション | 優先度 |
|-----------|---------|-----------|--------|
| PostToolUse | `.blade.php` ファイルを Edit/Write した直後 | `docker exec blade_management_laravel php artisan view:clear` を自動実行。「Blade キャッシュをクリアしました」と通知 | 高 |
| PostToolUse | `routes/web.php` を Edit/Write した直後 | `docker exec blade_management_laravel php artisan route:clear` を自動実行 | 中 |

---

## 観察事項

- **Bootstrap ホバー無効化の手戻り**: `btn-info` の指摘が2回あり、「ホバーを使わない」というプロジェクト規約の理解が遅れた。`.claude/rules/laravel/` に Bootstrap クラス使用ガイドライン（ホバー無効化前提のボタン設計）を追記すれば防止できる
- **DOM 配置の試行錯誤**: `daily_items_panel` の配置が3回変更された。UI 要素の「どこに配置すべきか」を事前にユーザーと合意する質問フローがあると効率的
- **`propose-one` との統合**: 現在の `propose-one` は create-proposal + create-plan のみ。implement-plans の自動発火は create-plan 内で既に実装されているため、`propose-one` に `prompt_N.md` の引数対応を追加するだけで `prompt-to-impl` 相当になる