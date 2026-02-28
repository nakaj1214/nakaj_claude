# 設計ドキュメントを更新する

会話の内容に基づいて、プロジェクトの設計・実装上の決定事項を `.claude/docs/DESIGN.md` に記録/更新する。

> **注意**: このスキルは `design-tracker` スキルと同じワークフローを明示的に実行する。
> 設計ドキュメントの更新を強制したい場合に使用する。

## ワークフロー

1. 既存の `.claude/docs/DESIGN.md` を読み込む
2. 会話から決定事項/情報を抽出する
3. 適切なセクションを更新する
4. 今日の日付でChangelogにエントリを追加する

## セクションマッピング

| トピック | セクション |
|---------|-----------|
| 目標、目的 | Overview |
| 構造、コンポーネント | Architecture |
| 設計パターン | Implementation Plan > Patterns |
| ライブラリの選択 | Implementation Plan > Libraries |
| 決定の根拠 | Implementation Plan > Key Decisions |
| 将来の作業 | TODO |
| 未解決の問題 | Open Questions |

## 更新フォーマット

更新時は適切なセクションに追加する:

```markdown
### Key Decisions

#### {決定タイトル} ({日付})

**Context**: {この決定が必要だった理由}
**Decision**: {何が決まったか}
**Rationale**: {このオプションが選ばれた理由}
```

## Changelogエントリ

常にChangelogに追加する:

```markdown
## Changelog

### {日付}
- {記録された内容の簡単な説明}
```

## 言語

- ドキュメントの内容: 英語（技術的内容）、日本語の説明も可
- ユーザーとのコミュニケーション: 日本語

$ARGUMENTS が指定された場合は、その内容の記録に集中する。
