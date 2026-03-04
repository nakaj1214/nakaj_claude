# Python MCP サーバー実装ガイド

## 概要

このドキュメントは、MCP Python SDK を使用した MCP サーバー実装のための Python 固有のベストプラクティスと例を提供する。サーバーセットアップ、ツール登録パターン、Pydantic による入力バリデーション、エラーハンドリング、完全な動作例をカバーする。

---

## クイックリファレンス

### 主要なインポート
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
```

### サーバー初期化
```python
mcp = FastMCP("service_mcp")
```

### ツール登録パターン
```python
@mcp.tool(name="tool_name", annotations={...})
async def tool_function(params: InputModel) -> str:
    # 実装
    pass
```

---

## MCP Python SDK と FastMCP

公式 MCP Python SDK は FastMCP を提供する。MCP サーバー構築のための高レベルフレームワーク:
- 関数シグネチャと docstring からの自動的な description と inputSchema 生成
- 入力バリデーションのための Pydantic モデル統合
- `@mcp.tool` によるデコレータベースのツール登録

**完全な SDK ドキュメントは WebFetch でロード:**
`https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

## サーバー命名規則

Python MCP サーバーは以下の命名パターンに従う:
- **フォーマット**: `{service}_mcp`（小文字、アンダースコア区切り）
- **例**: `github_mcp`, `jira_mcp`, `stripe_mcp`

名前は:
- 一般的であること（特定の機能に紐付けない）
- 統合するサービス/API を説明的に示すこと
- タスク説明から推測しやすいこと
- バージョン番号や日付を含めないこと

## ツール実装

### ツールの命名

ツール名には snake_case を使用（例: "search_users", "create_project", "get_channel_info"）。明確でアクション指向の名前を付ける。

**命名の衝突を避ける**: サービスコンテキストを含めて重複を防止:
- "send_message" ではなく "slack_send_message"
- "create_issue" ではなく "github_create_issue"
- "list_tasks" ではなく "asana_list_tasks"

### FastMCP によるツール構造

ツールは `@mcp.tool` デコレータと入力バリデーション用の Pydantic モデルで定義する:

```python
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# MCP サーバーの初期化
mcp = FastMCP("example_mcp")

# 入力バリデーション用 Pydantic モデルの定義
class ServiceToolInput(BaseModel):
    '''Input model for service tool operation.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 文字列の空白を自動トリム
        validate_assignment=True,    # 代入時にバリデーション
        extra='forbid'              # 余分なフィールドを禁止
    )

    param1: str = Field(..., description="First parameter description (e.g., 'user123', 'project-abc')", min_length=1, max_length=100)
    param2: Optional[int] = Field(default=None, description="Optional integer parameter with constraints", ge=0, le=1000)
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags to apply", max_items=10)

@mcp.tool(
    name="service_tool_name",
    annotations={
        "title": "Human-Readable Tool Title",
        "readOnlyHint": True,     # ツールは環境を変更しない
        "destructiveHint": False,  # ツールは破壊的操作を行わない
        "idempotentHint": True,    # 繰り返し呼び出しに追加の効果なし
        "openWorldHint": False     # ツールは外部エンティティと相互作用しない
    }
)
async def service_tool_name(params: ServiceToolInput) -> str:
    '''Tool description automatically becomes the 'description' field.

    This tool performs a specific operation on the service. It validates all inputs
    using the ServiceToolInput Pydantic model before processing.

    Args:
        params (ServiceToolInput): Validated input parameters containing:
            - param1 (str): First parameter description
            - param2 (Optional[int]): Optional parameter with default
            - tags (Optional[List[str]]): List of tags

    Returns:
        str: JSON-formatted response containing operation results
    '''
    # 実装
    pass
```

## Pydantic v2 の主要機能

- ネストされた `Config` クラスの代わりに `model_config` を使用
- 非推奨の `validator` の代わりに `field_validator` を使用
- 非推奨の `dict()` の代わりに `model_dump()` を使用
- バリデーターには `@classmethod` デコレータが必要
- バリデーターメソッドには型ヒントが必要

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class CreateUserInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="User's full name", min_length=1, max_length=100)
    email: str = Field(..., description="User's email address", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., description="User's age", ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower()
```

## レスポンスフォーマットオプション

柔軟性のために複数の出力フォーマットをサポート:

```python
from enum import Enum

class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"

class UserSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )
```

**Markdown フォーマット**:
- ヘッダー、リスト、フォーマットを使用して明確に
- タイムスタンプを人間が読めるフォーマットに変換（例: epoch ではなく "2024-01-15 10:30:00 UTC"）
- 表示名と ID を括弧付きで表示（例: "@john.doe (U123456)"）
- 冗長なメタデータを省略（例: すべてのサイズではなくプロフィール画像 URL を1つだけ表示）
- 関連情報を論理的にグループ化

**JSON フォーマット**:
- プログラム処理に適した完全で構造化されたデータを返す
- 利用可能なすべてのフィールドとメタデータを含む
- 一貫したフィールド名と型を使用

## ページネーションの実装

リソースをリストするツール向け:

```python
class ListInput(BaseModel):
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)

async def list_items(params: ListInput) -> str:
    # ページネーション付きの API リクエスト
    data = await api_request(limit=params.limit, offset=params.offset)

    # ページネーション情報を返す
    response = {
        "total": data["total"],
        "count": len(data["items"]),
        "offset": params.offset,
        "items": data["items"],
        "has_more": data["total"] > params.offset + len(data["items"]),
        "next_offset": params.offset + len(data["items"]) if data["total"] > params.offset + len(data["items"]) else None
    }
    return json.dumps(response, indent=2)
```

## エラーハンドリング

明確で実行可能なエラーメッセージを提供:

```python
def _handle_api_error(e: Exception) -> str:
    '''Consistent error formatting across all tools.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"
```

## 共有ユーティリティ

共通機能を再利用可能な関数に抽出:

```python
# 共有 API リクエスト関数
async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''Reusable function for all API calls.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
```

## Async/Await のベストプラクティス

ネットワークリクエストと I/O 操作には常に async/await を使用:

```python
# 良い例: 非同期ネットワークリクエスト
async def fetch_data(resource_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/resource/{resource_id}")
        response.raise_for_status()
        return response.json()

# 悪い例: 同期リクエスト
def fetch_data(resource_id: str) -> dict:
    response = requests.get(f"{API_URL}/resource/{resource_id}")  # ブロッキング
    return response.json()
```

## 型ヒント

全体を通じて型ヒントを使用:

```python
from typing import Optional, List, Dict, Any

async def get_user(user_id: str) -> Dict[str, Any]:
    data = await fetch_user(user_id)
    return {"id": data["id"], "name": data["name"]}
```

## ツールの Docstring

すべてのツールに明示的な型情報を含む包括的な docstring が必要:

```python
async def search_users(params: UserSearchInput) -> str:
    '''
    Search for users in the Example system by name, email, or team.

    This tool searches across all user profiles in the Example platform,
    supporting partial matches and various search filters. It does NOT
    create or modify users, only searches existing ones.

    Args:
        params (UserSearchInput): Validated input parameters containing:
            - query (str): Search string to match against names/emails (e.g., "john", "@example.com", "team:marketing")
            - limit (Optional[int]): Maximum results to return, between 1-100 (default: 20)
            - offset (Optional[int]): Number of results to skip for pagination (default: 0)

    Returns:
        str: JSON-formatted string containing search results with the following schema:

        Success response:
        {
            "total": int,           # 見つかったマッチの総数
            "count": int,           # このレスポンスの結果数
            "offset": int,          # 現在のページネーションオフセット
            "users": [
                {
                    "id": str,      # ユーザーID (例: "U123456789")
                    "name": str,    # フルネーム (例: "John Doe")
                    "email": str,   # メールアドレス (例: "john@example.com")
                    "team": str     # チーム名 (例: "Marketing") - オプション
                }
            ]
        }

        Error response:
        "Error: <error message>" or "No users found matching '<query>'"

    Examples:
        - Use when: "Find all marketing team members" -> params with query="team:marketing"
        - Use when: "Search for John's account" -> params with query="john"
        - Don't use when: You need to create a user (use example_create_user instead)
        - Don't use when: You have a user ID and need full details (use example_get_user instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Rate limit exceeded" if too many requests (429 status)
        - Returns "Error: Invalid API authentication" if API key is invalid (401 status)
        - Returns formatted list of results or "No users found matching 'query'"
    '''
```

## 完全な例

完全な Python MCP サーバーの例:

```python
#!/usr/bin/env python3
'''
MCP Server for Example Service.

This server provides tools to interact with Example API, including user search,
project management, and data export capabilities.
'''

from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# MCP サーバーの初期化
mcp = FastMCP("example_mcp")

# 定数
API_BASE_URL = "https://api.example.com/v1"

# Enum
class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"

# 入力バリデーション用 Pydantic モデル
class UserSearchInput(BaseModel):
    '''Input model for user search operations.'''
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    query: str = Field(..., description="Search string to match against names/emails", min_length=2, max_length=200)
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()

# 共有ユーティリティ関数
async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''Reusable function for all API calls.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

def _handle_api_error(e: Exception) -> str:
    '''Consistent error formatting across all tools.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"

# ツール定義
@mcp.tool(
    name="example_search_users",
    annotations={
        "title": "Search Example Users",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def example_search_users(params: UserSearchInput) -> str:
    '''Search for users in the Example system by name, email, or team.

    [Full docstring as shown above]
    '''
    try:
        # バリデーション済みパラメータを使用して API リクエスト
        data = await _make_api_request(
            "users/search",
            params={
                "q": params.query,
                "limit": params.limit,
                "offset": params.offset
            }
        )

        users = data.get("users", [])
        total = data.get("total", 0)

        if not users:
            return f"No users found matching '{params.query}'"

        # リクエストされたフォーマットに基づいてレスポンスをフォーマット
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# User Search Results: '{params.query}'", ""]
            lines.append(f"Found {total} users (showing {len(users)})")
            lines.append("")

            for user in users:
                lines.append(f"## {user['name']} ({user['id']})")
                lines.append(f"- **Email**: {user['email']}")
                if user.get('team'):
                    lines.append(f"- **Team**: {user['team']}")
                lines.append("")

            return "\n".join(lines)

        else:
            # 機械可読 JSON フォーマット
            import json
            response = {
                "total": total,
                "count": len(users),
                "offset": params.offset,
                "users": users
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
```

---

## 高度な FastMCP 機能

### Context パラメータインジェクション

FastMCP はツールに `Context` パラメータを自動注入でき、ログ、進捗報告、リソース読み取り、ユーザーインタラクションなどの高度な機能を提供:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("example_mcp")

@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    '''Advanced tool with context access for logging and progress.'''

    # 長い操作の進捗を報告
    await ctx.report_progress(0.25, "Starting search...")

    # デバッグ用の情報をログ
    await ctx.log_info("Processing query", {"query": query, "timestamp": datetime.now()})

    # 検索を実行
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    # サーバー設定にアクセス
    server_name = ctx.fastmcp.name

    return format_results(results)

@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    '''Tool that can request additional input from users.'''

    # 必要に応じて機密情報を要求
    api_key = await ctx.elicit(
        prompt="Please provide your API key:",
        input_type="password"
    )

    # 提供されたキーを使用
    return await api_call(resource_id, api_key)
```

**Context の機能:**
- `ctx.report_progress(progress, message)` - 長い操作の進捗報告
- `ctx.log_info(message, data)` / `ctx.log_error()` / `ctx.log_debug()` - ログ
- `ctx.elicit(prompt, input_type)` - ユーザーからの入力要求
- `ctx.fastmcp.name` - サーバー設定へのアクセス
- `ctx.read_resource(uri)` - MCP リソースの読み取り

### リソース登録

効率的なテンプレートベースのアクセスのためにデータをリソースとして公開:

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    '''Expose documents as MCP resources.

    リソースは複雑なパラメータを必要としない静的または準静的データに有用。
    柔軟なアクセスのために URI テンプレートを使用する。
    '''
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()

@mcp.resource("config://settings/{key}")
async def get_setting(key: str, ctx: Context) -> str:
    '''Expose configuration as resources with context.'''
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

**リソース vs ツールの使い分け:**
- **リソース**: シンプルなパラメータ（URI テンプレート）によるデータアクセス
- **ツール**: バリデーションとビジネスロジックを伴う複雑な操作

### 構造化出力型

FastMCP は文字列以外の複数の返り値型をサポート:

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel

# 構造化された返り値のための TypedDict
class UserData(TypedDict):
    id: str
    name: str
    email: str

@mcp.tool()
async def get_user_typed(user_id: str) -> UserData:
    '''Returns structured data - FastMCP handles serialization.'''
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# 複雑なバリデーションのための Pydantic モデル
class DetailedUser(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    metadata: Dict[str, Any]

@mcp.tool()
async def get_user_detailed(user_id: str) -> DetailedUser:
    '''Returns Pydantic model - automatically generates schema.'''
    user = await fetch_user(user_id)
    return DetailedUser(**user)
```

### ライフスパン管理

リクエスト間で永続するリソースの初期化:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    '''Manage resources that live for the server's lifetime.'''
    # 接続の初期化、設定のロードなど
    db = await connect_to_database()
    config = load_configuration()

    # すべてのツールで利用可能に
    yield {"db": db, "config": config}

    # シャットダウン時のクリーンアップ
    await db.close()

mcp = FastMCP("example_mcp", lifespan=app_lifespan)

@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    '''Access lifespan resources through context.'''
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

### トランスポートオプション

FastMCP は 2 つの主要なトランスポートメカニズムをサポート:

```python
# stdio トランスポート（ローカルツール用）- デフォルト
if __name__ == "__main__":
    mcp.run()

# Streamable HTTP トランスポート（リモートサーバー用）
if __name__ == "__main__":
    mcp.run(transport="streamable_http", port=8000)
```

**トランスポートの選択:**
- **stdio**: コマンドラインツール、ローカル統合、サブプロセス実行
- **Streamable HTTP**: Web サービス、リモートアクセス、複数クライアント

---

## コードのベストプラクティス

### コードの構成可能性と再利用性

実装では構成可能性とコードの再利用を最優先にすること:

1. **共通機能の抽出**:
   - 複数のツールで使用される操作のための再利用可能なヘルパー関数を作成
   - コードを複製する代わりに、HTTP リクエスト用の共有 API クライアントを構築
   - エラーハンドリングロジックをユーティリティ関数に集約
   - ビジネスロジックを組み合わせ可能な専用関数に抽出
   - 共有の Markdown または JSON フィールド選択とフォーマット機能を抽出

2. **重複の回避**:
   - ツール間で類似コードを絶対にコピーペーストしない
   - 同様のロジックを 2 回書いていると気づいたら、関数に抽出する
   - ページネーション、フィルタリング、フィールド選択、フォーマットなどの共通操作は共有する
   - 認証/認可ロジックは集約する

### Python 固有のベストプラクティス

1. **型ヒントを使用**: 関数パラメータと返り値に常に型アノテーションを含める
2. **Pydantic モデル**: すべての入力バリデーションに明確な Pydantic モデルを定義
3. **手動バリデーションを避ける**: 制約付きで Pydantic に入力バリデーションを処理させる
4. **適切なインポート**: インポートをグループ化（標準ライブラリ、サードパーティ、ローカル）
5. **エラーハンドリング**: 具体的な例外型を使用（汎用 Exception ではなく httpx.HTTPStatusError）
6. **非同期コンテキストマネージャー**: クリーンアップが必要なリソースには `async with` を使用
7. **定数**: モジュールレベルの定数を UPPER_CASE で定義

## 品質チェックリスト

Python MCP サーバーの実装を完了する前に確認:

### 戦略的設計
- [ ] ツールが完全なワークフローを実現（単なる API エンドポイントラッパーではない）
- [ ] ツール名が自然なタスク分割を反映
- [ ] レスポンスフォーマットがエージェントのコンテキスト効率を最適化
- [ ] 適切な場合に人間が読める識別子を使用
- [ ] エラーメッセージがエージェントを正しい使い方に導く

### 実装品質
- [ ] 最も重要で価値のあるツールを重点的に実装
- [ ] すべてのツールに説明的な名前とドキュメントがある
- [ ] 類似の操作間で返り値型が一貫
- [ ] すべての外部呼び出しにエラーハンドリングが実装
- [ ] サーバー名が `{service}_mcp` フォーマットに従う
- [ ] すべてのネットワーク操作が async/await を使用
- [ ] 共通機能が再利用可能な関数に抽出
- [ ] エラーメッセージが明確で、実行可能で、教育的
- [ ] 出力が適切にバリデーションとフォーマット

### ツール設定
- [ ] すべてのツールがデコレータに 'name' と 'annotations' を実装
- [ ] アノテーションが正しく設定（readOnlyHint, destructiveHint, idempotentHint, openWorldHint）
- [ ] すべてのツールが入力バリデーションに Field() 定義付きの Pydantic BaseModel を使用
- [ ] すべての Pydantic Field に明示的な型、説明、制約がある
- [ ] すべてのツールに明示的な入出力型を含む包括的な docstring がある
- [ ] Docstring に dict/JSON 返り値の完全なスキーマ構造が含まれる
- [ ] Pydantic モデルが入力バリデーションを処理（手動バリデーション不要）

### 高度な機能（該当する場合）
- [ ] ログ、進捗、または elicitation のための Context インジェクションを使用
- [ ] 適切なデータエンドポイントにリソースが登録
- [ ] 永続的な接続のためのライフスパン管理が実装
- [ ] 構造化出力型を使用（TypedDict, Pydantic モデル）
- [ ] 適切なトランスポートが設定（stdio または streamable HTTP）

### コード品質
- [ ] Pydantic インポートを含む適切なインポートがファイルに含まれる
- [ ] 該当する場合にページネーションが適切に実装
- [ ] 大きな結果セットにフィルタリングオプションが提供
- [ ] すべての非同期関数が `async def` で適切に定義
- [ ] HTTP クライアントの使用が適切なコンテキストマネージャー付きの非同期パターンに従う
- [ ] コード全体で型ヒントが使用
- [ ] 定数がモジュールレベルで UPPER_CASE で定義

### テスト
- [ ] サーバーが正常に実行: `python your_server.py --help`
- [ ] すべてのインポートが正しく解決
- [ ] サンプルのツール呼び出しが期待通りに動作
- [ ] エラーシナリオが優雅に処理
