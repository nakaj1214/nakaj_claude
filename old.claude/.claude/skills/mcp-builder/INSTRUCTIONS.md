# MCPサーバー開発ガイド — 詳細手順

## 4フェーズワークフロー

### フェーズ1: 深い調査と計画

#### 1.1 対象APIの調査

WebFetchでAPIドキュメントを取得し、以下を把握する:

- 利用可能なエンドポイントと機能
- 認証方式（APIキー、OAuth 2.1等）
- レート制限とページネーション方式
- エラーレスポンスのフォーマット

```bash
# TypeScript SDK最新ドキュメント
# https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md

# Python SDK最新ドキュメント
# https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md
```

#### 1.2 ツール設計の原則

**APIカバレッジ vs ワークフローツール:**
- 単純なエンドポイントラッパーではなく、完全なワークフローを可能にするツールを設計する
- 例: `create_and_assign_task` vs 別々の `create_task` + `assign_task`

**ツール命名規則:**

| 言語 | サーバー名 | ツール名 |
|------|-----------|---------|
| Python | `{service}_mcp` | `{service}_{action}_{resource}` |
| TypeScript | `{service}-mcp-server` | `{service}_{action}_{resource}` |

例: `slack_send_message`, `github_create_issue`

**設計チェックリスト:**
- [ ] 各ツールは単一の責務を持つ（アトミック）
- [ ] ツール説明はあいまいさなく機能を記述
- [ ] サービスプレフィックスで名前衝突を回避
- [ ] レスポンスはコンテキスト効率を最適化

#### 1.3 プロジェクト構造の決定

**TypeScript:**
```
{service}-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # McpServer初期化
│   ├── types.ts          # 型定義
│   ├── tools/            # ツール実装（ドメイン別）
│   ├── services/         # APIクライアント
│   ├── schemas/          # Zodスキーマ
│   └── constants.ts      # 定数（API_URL, CHARACTER_LIMIT等）
└── dist/                 # ビルド済みJS
```

**Python:**
```
{service}_mcp/
├── server.py             # FastMCP初期化
├── tools/                # ツール実装
├── models/               # Pydanticモデル
└── utils/                # 共有ユーティリティ
```

---

### フェーズ2: 実装

#### 2.1 TypeScript実装パターン

詳細: [reference/node_mcp_server.md](reference/node_mcp_server.md)

**サーバー初期化:**
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "service-mcp-server",
  version: "1.0.0"
});
```

**ツール登録（`registerTool` を必ず使用）:**
```typescript
server.registerTool(
  "service_action_resource",
  {
    title: "Human Readable Title",
    description: `What the tool does.

Args:
  - param (string): Description with examples

Returns:
  JSON: { total, count, items[], has_more }

Examples:
  - Use when: "Find all users" -> params with query="all"
  - Don't use when: Creating users (use service_create_user instead)`,
    inputSchema: InputSchema,  // Zodスキーマ
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params) => {
    try {
      const result = await apiCall(params);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        structuredContent: result
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: handleApiError(error) }]
      };
    }
  }
);
```

**重要: 古いAPIは使用禁止**
- ❌ `server.tool()`, `server.setRequestHandler()`
- ✅ `server.registerTool()`, `server.registerResource()`, `server.registerPrompt()`

#### 2.2 Python実装パターン

詳細: [reference/python_mcp_server.md](reference/python_mcp_server.md)

**FastMCP初期化:**
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

mcp = FastMCP("service_mcp")
```

**ツール定義:**
```python
class ServiceInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )
    param: str = Field(..., description="説明 (例: 'value1')", min_length=1)

@mcp.tool(
    name="service_action_resource",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def service_action_resource(params: ServiceInput) -> str:
    '''ツールの説明（この文字列がdescriptionになる）。

    Args:
        params: 入力パラメータ
    Returns:
        str: JSON形式のレスポンス
    '''
    try:
        result = await _make_api_request(...)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_api_error(e)
```

#### 2.3 共通実装パターン

**ページネーション（必須）:**
```typescript
// レスポンスに常に含める
{
  total: number,
  count: number,
  offset: number,
  items: [...],
  has_more: boolean,
  next_offset?: number  // has_more=trueの時
}
```

**レスポンスフォーマット（両形式をサポート）:**
```typescript
// response_format パラメータ
enum ResponseFormat { MARKDOWN = "markdown", JSON = "json" }
```

**文字数制限（TypeScript）:**
```typescript
const CHARACTER_LIMIT = 25000;
if (result.length > CHARACTER_LIMIT) {
  // truncate with message
}
```

**エラーハンドリング（アクショナブルなメッセージ）:**
```typescript
// Bad: "Error occurred"
// Good: "Error: Rate limit exceeded. Please wait 60 seconds."
// Good: "Error: Resource 'USER-123' not found. Check the ID is correct."
```

**トランスポート選択:**

| 用途 | TypeScript | Python |
|------|-----------|--------|
| ローカル | `StdioServerTransport` | `mcp.run()` |
| リモート | `StreamableHTTPServerTransport` | `mcp.run(transport="streamable_http")` |

#### 2.4 セキュリティ

詳細: [reference/mcp_best_practices.md](reference/mcp_best_practices.md)

- APIキーは環境変数に保存（コードにハードコード禁止）
- 全入力はZod/Pydanticでバリデーション
- ディレクトリトラバーサル対策
- ローカルHTTPサーバーはDNS rebinding保護を有効化

---

### フェーズ3: レビューとテスト

#### 3.1 実装品質チェック

**TypeScript用チェックリスト:**
- [ ] `npm run build` が成功する
- [ ] 全ツールが `registerTool` で登録されている
- [ ] 全ツールに `title`, `description`, `inputSchema`, `annotations` が設定されている
- [ ] Zodスキーマに `.strict()` を使用
- [ ] `any` 型を使用していない（`unknown` を使用）
- [ ] 共通処理が関数に抽出されている（重複なし）

**Python用チェックリスト:**
- [ ] 全ツールに `name` と `annotations` が設定されている
- [ ] Pydantic Fieldsに `description` と制約が設定されている
- [ ] 全ての非同期関数が `async def` で定義されている
- [ ] 共通処理が関数に抽出されている（重複なし）

**共通チェック:**
- [ ] エラーメッセージがアクショナブル（何をすべきかを伝える）
- [ ] ページネーションが実装されている
- [ ] レスポンスサイズが過大でない
- [ ] セキュリティ: APIキーが環境変数で管理されている

#### 3.2 動作確認

```bash
# TypeScript
npm run build
node dist/index.js  # エラーなく起動することを確認

# Python
python server.py  # エラーなく起動することを確認
```

---

### フェーズ4: 評価の作成

詳細: [reference/evaluation.md](reference/evaluation.md)

MCPサーバーの品質は「LLMがツールを使って現実的な質問に答えられるか」で測定する。

#### 4.1 評価問題の要件

| 要件 | 説明 |
|------|------|
| READ-ONLY | 状態を変更するツールを必要としない |
| INDEPENDENT | 他の問題の答えに依存しない |
| NON-DESTRUCTIVE | 破壊的操作なし |
| COMPLEX | 複数（場合によっては数十）のツール呼び出しが必要 |
| STABLE | 時間が経っても答えが変わらない |
| VERIFIABLE | 単一の検証可能な値で答えられる |

#### 4.2 良い問題の特徴

```xml
<!-- Good: 複数ステップ、歴史的データ、人間が読める答え -->
<qa_pair>
  <question>Find the repository archived in Q3 2023 that was previously
  the most forked project. What was its primary programming language?</question>
  <answer>Python</answer>
</qa_pair>

<!-- Bad: 現在の状態（変化する） -->
<qa_pair>
  <question>How many open issues exist currently?</question>
  <answer>47</answer>
</qa_pair>
```

#### 4.3 評価ファイル作成手順

1. **APIドキュメント調査** — エンドポイントと機能を把握
2. **ツール検査** — 入出力スキーマを確認（ツールは呼ばない）
3. **READ-ONLYでコンテンツ探索** — 質問の素材を見つける
   - `limit` パラメータを小さく設定（`<10`）
   - ページネーションを活用
4. **10問の問題を作成** — 上記の要件を満たす
5. **答えを自分で確認** — MCPツールを使って検証

#### 4.4 評価の実行

```bash
# セットアップ
pip install -r scripts/requirements.txt
export ANTHROPIC_API_KEY=your_api_key

# stdio（ローカルサーバー）
python scripts/evaluation.py \
  -t stdio \
  -c python \
  -a my_server.py \
  -e API_KEY=xxx \
  evaluations/evals.xml

# HTTP（リモートサーバー）
python scripts/evaluation.py \
  -t http \
  -u https://example.com/mcp \
  -H "Authorization: Bearer token" \
  evaluations/evals.xml
```

---

## 設計判断の指針

### ツールをいくつ作るか

- 多すぎるツール（30+）: LLMが適切なツールを選べない
- 少なすぎるツール（3以下）: ワークフローが完結しない
- 推奨: サービスの主要ユースケースをカバーする最小セット（10-20）

### ツールvsリソース

| 用途 | 選択 |
|------|------|
| URIベースのシンプルなデータアクセス | Resources |
| バリデーションや副作用を伴う操作 | Tools |
| 静的または半静的なデータ | Resources |
| 複雑なワークフロー | Tools |

### コンテキスト管理

- 大きなレスポンスには文字数制限を設ける
- フィルタリングオプションを提供する
- ページネーションのデフォルトは20-50件
- LLMが消化できる情報量を意識する

---

## 参照ファイル

| ファイル | 内容 |
|---------|------|
| [reference/mcp_best_practices.md](reference/mcp_best_practices.md) | 命名規則・セキュリティ・アノテーション・エラーハンドリング |
| [reference/node_mcp_server.md](reference/node_mcp_server.md) | TypeScript実装の完全ガイド（Zod、コード例、チェックリスト） |
| [reference/python_mcp_server.md](reference/python_mcp_server.md) | Python実装の完全ガイド（FastMCP、Pydantic、チェックリスト） |
| [reference/evaluation.md](reference/evaluation.md) | 評価作成・実行の詳細ガイド |
| [scripts/evaluation.py](scripts/evaluation.py) | 評価実行スクリプト |
| [scripts/example_evaluation.xml](scripts/example_evaluation.xml) | 評価ファイルのサンプル |
