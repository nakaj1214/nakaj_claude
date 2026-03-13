---
tags: ['session', 'automation']
scope: session
date: 2026-03-11
---

debug フォルダのインライン JS はすべて除去されました。

## 完了サマリー

### ルール追加
- `.claude/rules/laravel/no-inline-js.md` — Blade への JS 直書き禁止ルール

### インライン JS 外部化（debug フォルダのみ）

| ファイル | 変更内容 |
|---------|---------|
| `debug/copy_test.blade.php` | inline script → `js/debug/copy_test_init.js` |
| `debug/outbound_spreadsheet.blade.php` | inline script → `data-*` 属性 + `js/debug/outbound_spreadsheet_init.js` |

### ホームの扱い
- `home.blade.php` の `index_url` / `storage_scope` はインラインのまま維持（ユーザー指示により）

### 注意
- `test_stock_ui.blade.php`、`test_report.blade.php` は対象外（テスト系）
- 他の本番 Blade（inbound/stock/order/outbound/confirm/analytics 等）のインライン JS は今回の対象外