# _shared 再設計案

現状の問題を解消し、「最小コンテキスト・最大能力・自己改善」を実現する構造。

---

## 現状の課題

| 課題 | 詳細 |
|-----|------|
| ルーティングがない | Claude が全 SKILL.md を読んで判断している |
| フック間でコード重複 | transcript 解析ロジックが各スクリプトに直書き |
| evals が空 | `evaluations/` ディレクトリが放置されているスキルが多い |
| 役割が曖昧な層 | `contexts/` `commands/` `docs/libraries/` が `skills/` と重複 |
| 品質監査なし | 肥大化・重複・孤立スキルを検出する仕組みがない |

---

## 目標設計

```
_shared/
├── core/                     # 常時ロード（厳格に ≤2KB）
│   ├── CLAUDE.md            # エントリポイント（rules/ への参照のみ）
│   └── principles.md        # 全案件共通ルール（security/git/style）
│
├── registry/                 # ルーティング層
│   ├── skills.yaml          # name, triggers, path, tags を一元管理
│   └── agents.yaml          # エージェント一覧
│
├── skills/                   # registry 経由でオンデマンドロード
│   └── {skill}/
│       ├── SKILL.md         # フロントマターのみ（現状通り）
│       ├── INSTRUCTIONS.md  # 詳細（現状通り）
│       └── evals.json       # テストケース（必須化）
│
├── agents/                   # 現状とほぼ同じ
│
├── hooks/
│   ├── lib/                  # 共有ユーティリティ
│   │   ├── transcript.py    # JSONL 解析（再利用可能）
│   │   └── claude_p.py      # claude -p ラッパー + リトライ
│   └── pre-compact.py       # PreCompact フック（lib/ を利用）
│
├── rules/                    # スキルから参照される（単体ロードしない）
│   ├── security-rules.md
│   ├── performance.md
│   └── git.md
│
└── meta/                     # 自己改善インフラ
    ├── health-check.py       # 重複/欠損evals/SKILL.md肥大を定期監査
    └── skill-creator/        # 現状の skills/skill-creator をここに移動
```

---

## 変えない点

- **二段階ロード**（SKILL.md + INSTRUCTIONS.md）— 効果が実証済み
- **PreCompact フック** — 設計として正しい
- **rules/ の独立** — skills と混ぜると責務が曖昧になる

---

## 実装タスク（優先順）

### 1. `registry/skills.yaml` — 最優先

全スキルの name / triggers / path / tags を一元管理するインデックス。
Claude がこれを読めば SKILL.md を全件ロードせずにルーティングできる。

```yaml
# registry/skills.yaml
skills:
  - name: handover
    path: skills/handover/SKILL.md
    tags: [session, memory]
    triggers:
      - "引き継ぎ"
      - "handover"
      - "セッション終了"

  - name: css-organization
    path: skills/css-organization/SKILL.md
    tags: [css, design-system]
    triggers:
      - "CSS設計"
      - "デザインシステム"
      - "BEM"

  # ... 全スキル分
```

**実装手順:**
1. 既存 SKILL.md のフロントマターから name/description を抽出
2. `registry/skills.yaml` を生成するスクリプト（`meta/generate-registry.py`）を作成
3. `core/CLAUDE.md` に「スキルのルーティングは registry/skills.yaml を参照」と記載

---

### 2. `hooks/lib/` — 第2優先

`pre-compact.py` の transcript 解析と claude -p 呼び出しを独立モジュール化。
新しいフックを追加するたびに車輪の再発明をしなくて済む。

**`hooks/lib/transcript.py`:**
```python
# JSONL トランスクリプトを読み込んでテキストに変換
def read(path: str) -> str: ...
```

**`hooks/lib/claude_p.py`:**
```python
# claude -p を呼び出してテキストを返す（タイムアウト・リトライ付き）
def run(prompt: str, timeout: int = 120) -> str: ...
```

**実装手順:**
1. `pre-compact.py` の `read_transcript()` と `_run_claude()` を lib に切り出し
2. `pre-compact.py` を `from lib.transcript import read` に書き換え
3. 動作確認（既存の挙動が変わらないこと）

---

### 3. `meta/health-check.py` — 第3優先

定期実行（または `/health-check` スキルとして手動実行）で以下を検出:

- `evals.json` が存在しないスキル
- SKILL.md が30行を超えているスキル（二段階ロード崩壊の兆候）
- `registry/skills.yaml` に登録されていないスキル（孤立スキル）
- description が重複しているスキル（重複候補）

出力: `.claude/docs/memory/HEALTH-YYYY-MM-DD.md`

---

### 4. `evals.json` 必須化 — 第4優先

`skill-creator` が新スキル作成時に必ず `evals.json` のひな形も生成するよう更新。

```json
{
  "evals": [
    {
      "id": "basic-trigger",
      "input": "（スキルをトリガーするユーザー発話例）",
      "expected_behavior": "（期待される動作の説明）",
      "pass_criteria": "（合否判定の基準）"
    }
  ]
}
```

---

### 5. 廃止・統合 — 最後

| 対象 | 処置 |
|-----|------|
| `contexts/` | 内容を `skills/` または `core/` に移動後削除 |
| `commands/` | `skills/` に統合（コマンドもスキルの一形態） |
| `docs/libraries/` | `resources/` に移動 |

---

## 移行方針

- **段階的移行** — 一括置換はしない。新規追加から新設計に従い、既存は徐々に移行
- **後方互換** — registry がなくても既存スキルは動作し続ける（registry は「あると速い」オプション扱い）
- **実装後に STRUCTURE.md を更新**
