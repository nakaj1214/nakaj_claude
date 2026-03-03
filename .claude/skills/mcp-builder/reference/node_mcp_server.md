# Node/TypeScript MCP サーバー実装ガイド

## 概要

このドキュメントは、MCP TypeScript SDK を使用した MCP サーバーの実装に関する、Node/TypeScript 固有のベストプラクティスと例を提供します。プロジェクト構成、サーバーセットアップ、ツール登録パターン、Zod による入力バリデーション、エラーハンドリング、完全な動作例をカバーします。

---

## クイックリファレンス

### 主要なインポート
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import express from "express";
import { z } from "zod";
```

### サーバーの初期化
```typescript
const server = new McpServer({
  name: "service-mcp-server",
  version: "1.0.0"
});
```

### ツール登録パターン
```typescript
server.registerTool(
  "tool_name",
  {
    title: "Tool Display Name",
    description: "What the tool does",
    inputSchema: { param: z.string() },
    outputSchema: { result: z.string() }
  },
  async ({ param }) => {
    const output = { result: `Processed: ${param}` };
    return {
      content: [{ type: "text", text: JSON.stringify(output) }],
      structuredContent: output // 構造化データのモダンパターン
    };
  }
);
```

---

## MCP TypeScript SDK

公式の MCP TypeScript SDK は以下を提供します:
- サーバー初期化用の `McpServer` クラス
- ツール登録用の `registerTool` メソッド
- ランタイム入力バリデーション用の Zod スキーマ統合
- 型安全なツールハンドラー実装

**重要 - モダン API のみを使用:**
- **使用すべき**: `server.registerTool()`, `server.registerResource()`, `server.registerPrompt()`
- **使用してはならない**: `server.tool()`, `server.setRequestHandler(ListToolsRequestSchema, ...)` などの古い非推奨 API、または手動ハンドラー登録
- `register*` メソッドはより良い型安全性、自動スキーマ処理を提供し、推奨されるアプローチです

完全な詳細はリファレンスの MCP SDK ドキュメントを参照してください。

## サーバー命名規則

Node/TypeScript MCP サーバーは以下の命名パターンに従う必要があります:
- **フォーマット**: `{service}-mcp-server`（ハイフン付き小文字）
- **例**: `github-mcp-server`, `jira-mcp-server`, `stripe-mcp-server`

名前は以下であるべきです:
- 汎用的（特定の機能に紐付かない）
- 統合するサービス/API を説明する
- タスクの説明から推測しやすい
- バージョン番号や日付を含まない

## プロジェクト構成

Node/TypeScript MCP サーバーには以下の構成を作成します:

```
{service}-mcp-server/
├── package.json
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts          # メインエントリーポイント（McpServer の初期化）
│   ├── types.ts          # TypeScript 型定義とインターフェース
│   ├── tools/            # ツール実装（ドメインごとに1ファイル）
│   ├── services/         # API クライアントと共有ユーティリティ
│   ├── schemas/          # Zod バリデーションスキーマ
│   └── constants.ts      # 共有定数（API_URL, CHARACTER_LIMIT 等）
└── dist/                 # ビルド済み JavaScript ファイル（エントリーポイント: dist/index.js）
```

## ツール実装

### ツールの命名

ツール名には snake_case を使用します（例: "search_users", "create_project", "get_channel_info"）。明確でアクション指向の名前にします。

**名前の衝突を避ける**: 重複を防ぐためにサービスコンテキストを含める:
- `send_message` ではなく `slack_send_message`
- `create_issue` ではなく `github_create_issue`
- `list_tasks` ではなく `asana_list_tasks`

### ツールの構造

ツールは以下の要件で `registerTool` メソッドを使用して登録します:
- ランタイム入力バリデーションと型安全性のために Zod スキーマを使用
- `description` フィールドは明示的に提供する必要がある — JSDoc コメントは自動抽出されない
- `title`, `description`, `inputSchema`, `annotations` を明示的に提供
- `inputSchema` は Zod スキーマオブジェクト（JSON スキーマではない）でなければならない
- すべてのパラメータと戻り値に明示的に型を付ける

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// 入力バリデーション用 Zod スキーマ
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
}).strict();

// Zod スキーマからの型定義
type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

server.registerTool(
  "example_search_users",
  {
    title: "Search Example Users",
    description: `Search for users in the Example system by name, email, or team.

This tool searches across all user profiles in the Example platform, supporting partial matches and various search filters. It does NOT create or modify users, only searches existing ones.

Args:
  - query (string): Search string to match against names/emails
  - limit (number): Maximum results to return, between 1-100 (default: 20)
  - offset (number): Number of results to skip for pagination (default: 0)
  - response_format ('markdown' | 'json'): Output format (default: 'markdown')

Returns:
  For JSON format: Structured data with schema:
  {
    "total": number,           // Total number of matches found
    "count": number,           // Number of results in this response
    "offset": number,          // Current pagination offset
    "users": [
      {
        "id": string,          // User ID (e.g., "U123456789")
        "name": string,        // Full name (e.g., "John Doe")
        "email": string,       // Email address
        "team": string,        // Team name (optional)
        "active": boolean      // Whether user is active
      }
    ],
    "has_more": boolean,       // Whether more results are available
    "next_offset": number      // Offset for next page (if has_more is true)
  }

Examples:
  - Use when: "Find all marketing team members" -> params with query="team:marketing"
  - Use when: "Search for John's account" -> params with query="john"
  - Don't use when: You need to create a user (use example_create_user instead)

Error Handling:
  - Returns "Error: Rate limit exceeded" if too many requests (429 status)
  - Returns "No users found matching '<query>'" if search returns empty`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    try {
      // 入力バリデーションは Zod スキーマが処理
      // バリデーション済みパラメータで API リクエスト
      const data = await makeApiRequest<any>(
        "users/search",
        "GET",
        undefined,
        {
          q: params.query,
          limit: params.limit,
          offset: params.offset
        }
      );

      const users = data.users || [];
      const total = data.total || 0;

      if (!users.length) {
        return {
          content: [{
            type: "text",
            text: `No users found matching '${params.query}'`
          }]
        };
      }

      // 構造化された出力を準備
      const output = {
        total,
        count: users.length,
        offset: params.offset,
        users: users.map((user: any) => ({
          id: user.id,
          name: user.name,
          email: user.email,
          ...(user.team ? { team: user.team } : {}),
          active: user.active ?? true
        })),
        has_more: total > params.offset + users.length,
        ...(total > params.offset + users.length ? {
          next_offset: params.offset + users.length
        } : {})
      };

      // 要求されたフォーマットに基づいてテキスト表現をフォーマット
      let textContent: string;
      if (params.response_format === ResponseFormat.MARKDOWN) {
        const lines = [`# User Search Results: '${params.query}'`, "",
          `Found ${total} users (showing ${users.length})`, ""];
        for (const user of users) {
          lines.push(`## ${user.name} (${user.id})`);
          lines.push(`- **Email**: ${user.email}`);
          if (user.team) lines.push(`- **Team**: ${user.team}`);
          lines.push("");
        }
        textContent = lines.join("\n");
      } else {
        textContent = JSON.stringify(output, null, 2);
      }

      return {
        content: [{ type: "text", text: textContent }],
        structuredContent: output // 構造化データのモダンパターン
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: handleApiError(error)
        }]
      };
    }
  }
);
```

## 入力バリデーション用 Zod スキーマ

Zod はランタイム型バリデーションを提供します:

```typescript
import { z } from "zod";

// バリデーション付き基本スキーマ
const CreateUserSchema = z.object({
  name: z.string()
    .min(1, "Name is required")
    .max(100, "Name must not exceed 100 characters"),
  email: z.string()
    .email("Invalid email format"),
  age: z.number()
    .int("Age must be a whole number")
    .min(0, "Age cannot be negative")
    .max(150, "Age cannot be greater than 150")
}).strict();  // 余分なフィールドを禁止するために .strict() を使用

// Enum
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const SearchSchema = z.object({
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format")
});

// デフォルト付きオプショナルフィールド
const PaginationSchema = z.object({
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip")
});
```

## レスポンスフォーマットオプション

柔軟性のために複数の出力フォーマットをサポート:

```typescript
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

const inputSchema = z.object({
  query: z.string(),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
});
```

**Markdown フォーマット**:
- 見出し、リスト、フォーマットを使用して明確に
- タイムスタンプを人間が読めるフォーマットに変換
- ID を括弧内に添えて表示名を表示
- 冗長なメタデータを省略
- 関連情報を論理的にグループ化

**JSON フォーマット**:
- プログラム処理に適した完全な構造化データを返す
- 利用可能なすべてのフィールドとメタデータを含む
- 一貫したフィールド名と型を使用

## ページネーション実装

リソースを一覧表示するツールの場合:

```typescript
const ListSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20),
  offset: z.number().int().min(0).default(0)
});

async function listItems(params: z.infer<typeof ListSchema>) {
  const data = await apiRequest(params.limit, params.offset);

  const response = {
    total: data.total,
    count: data.items.length,
    offset: params.offset,
    items: data.items,
    has_more: data.total > params.offset + data.items.length,
    next_offset: data.total > params.offset + data.items.length
      ? params.offset + data.items.length
      : undefined
  };

  return JSON.stringify(response, null, 2);
}
```

## 文字数制限とトランケーション

レスポンスの肥大化を防ぐために CHARACTER_LIMIT 定数を追加:

```typescript
// constants.ts のモジュールレベルで
export const CHARACTER_LIMIT = 25000;  // レスポンスの最大サイズ（文字数）

async function searchTool(params: SearchInput) {
  let result = generateResponse(data);

  // 文字数制限をチェックし、必要に応じてトランケート
  if (result.length > CHARACTER_LIMIT) {
    const truncatedData = data.slice(0, Math.max(1, data.length / 2));
    response.data = truncatedData;
    response.truncated = true;
    response.truncation_message =
      `Response truncated from ${data.length} to ${truncatedData.length} items. ` +
      `Use 'offset' parameter or add filters to see more results.`;
    result = JSON.stringify(response, null, 2);
  }

  return result;
}
```

## エラーハンドリング

明確で実行可能なエラーメッセージを提供:

```typescript
import axios, { AxiosError } from "axios";

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "Error: Resource not found. Please check the ID is correct.";
        case 403:
          return "Error: Permission denied. You don't have access to this resource.";
        case 429:
          return "Error: Rate limit exceeded. Please wait before making more requests.";
        default:
          return `Error: API request failed with status ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "Error: Request timed out. Please try again.";
    }
  }
  return `Error: Unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`;
}
```

## 共有ユーティリティ

共通機能を再利用可能な関数に抽出:

```typescript
// 共有 API リクエスト関数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}
```

## Async/Await ベストプラクティス

ネットワークリクエストと I/O 操作には常に async/await を使用:

```typescript
// 良い例: 非同期ネットワークリクエスト
async function fetchData(resourceId: string): Promise<ResourceData> {
  const response = await axios.get(`${API_URL}/resource/${resourceId}`);
  return response.data;
}

// 悪い例: Promise チェーン
function fetchData(resourceId: string): Promise<ResourceData> {
  return axios.get(`${API_URL}/resource/${resourceId}`)
    .then(response => response.data);  // 読みにくく保守しにくい
}
```

## TypeScript ベストプラクティス

1. **Strict TypeScript を使用**: tsconfig.json で strict モードを有効にする
2. **インターフェースを定義**: すべてのデータ構造に明確なインターフェース定義を作成
3. **`any` を避ける**: `any` の代わりに適切な型または `unknown` を使用
4. **ランタイムバリデーションに Zod**: 外部データのバリデーションに Zod スキーマを使用
5. **型ガード**: 複雑な型チェック用の型ガード関数を作成
6. **エラーハンドリング**: 適切なエラー型チェック付きの try-catch を常に使用
7. **Null 安全**: オプショナルチェーニング (`?.`) と Null 合体演算子 (`??`) を使用

```typescript
// 良い例: Zod とインターフェースによる型安全
interface UserResponse {
  id: string;
  name: string;
  email: string;
  team?: string;
  active: boolean;
}

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  team: z.string().optional(),
  active: z.boolean()
});

type User = z.infer<typeof UserSchema>;

async function getUser(id: string): Promise<User> {
  const data = await apiCall(`/users/${id}`);
  return UserSchema.parse(data);  // ランタイムバリデーション
}

// 悪い例: any の使用
async function getUser(id: string): Promise<any> {
  return await apiCall(`/users/${id}`);  // 型安全性がない
}
```

## パッケージ設定

### package.json

```json
{
  "name": "{service}-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for {Service} API integration",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "clean": "rm -rf dist"
  },
  "engines": {
    "node": ">=18"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.6.1",
    "axios": "^1.7.9",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 完全な例

```typescript
#!/usr/bin/env node
/**
 * MCP Server for Example Service.
 *
 * This server provides tools to interact with Example API, including user search,
 * project management, and data export capabilities.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios, { AxiosError } from "axios";

// 定数
const API_BASE_URL = "https://api.example.com/v1";
const CHARACTER_LIMIT = 25000;

// Enum
enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

// Zod スキーマ
const UserSearchInputSchema = z.object({
  query: z.string()
    .min(2, "Query must be at least 2 characters")
    .max(200, "Query must not exceed 200 characters")
    .describe("Search string to match against names/emails"),
  limit: z.number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe("Maximum results to return"),
  offset: z.number()
    .int()
    .min(0)
    .default(0)
    .describe("Number of results to skip for pagination"),
  response_format: z.nativeEnum(ResponseFormat)
    .default(ResponseFormat.MARKDOWN)
    .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable")
}).strict();

type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

// 共有ユーティリティ関数
async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: any,
  params?: any
): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${API_BASE_URL}/${endpoint}`,
      data,
      params,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
}

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      switch (error.response.status) {
        case 404:
          return "Error: Resource not found. Please check the ID is correct.";
        case 403:
          return "Error: Permission denied. You don't have access to this resource.";
        case 429:
          return "Error: Rate limit exceeded. Please wait before making more requests.";
        default:
          return `Error: API request failed with status ${error.response.status}`;
      }
    } else if (error.code === "ECONNABORTED") {
      return "Error: Request timed out. Please try again.";
    }
  }
  return `Error: Unexpected error occurred: ${error instanceof Error ? error.message : String(error)}`;
}

// MCP サーバーインスタンスの作成
const server = new McpServer({
  name: "example-mcp",
  version: "1.0.0"
});

// ツールの登録
server.registerTool(
  "example_search_users",
  {
    title: "Search Example Users",
    description: `[Full description as shown above]`,
    inputSchema: UserSearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  },
  async (params: UserSearchInput) => {
    // 上記の実装
  }
);

// メイン関数
// stdio（ローカル）用:
async function runStdio() {
  if (!process.env.EXAMPLE_API_KEY) {
    console.error("ERROR: EXAMPLE_API_KEY environment variable is required");
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running via stdio");
}

// Streamable HTTP（リモート）用:
async function runHTTP() {
  if (!process.env.EXAMPLE_API_KEY) {
    console.error("ERROR: EXAMPLE_API_KEY environment variable is required");
    process.exit(1);
  }

  const app = express();
  app.use(express.json());

  app.post('/mcp', async (req, res) => {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true
    });
    res.on('close', () => transport.close());
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  const port = parseInt(process.env.PORT || '3000');
  app.listen(port, () => {
    console.error(`MCP server running on http://localhost:${port}/mcp`);
  });
}

// 環境に基づいてトランスポートを選択
const transport = process.env.TRANSPORT || 'stdio';
if (transport === 'http') {
  runHTTP().catch(error => {
    console.error("Server error:", error);
    process.exit(1);
  });
} else {
  runStdio().catch(error => {
    console.error("Server error:", error);
    process.exit(1);
  });
}
```

---

## 高度な MCP 機能

### リソース登録

効率的な URI ベースのアクセスのためにデータをリソースとして公開:

```typescript
import { ResourceTemplate } from "@modelcontextprotocol/sdk/types.js";

// URI テンプレートでリソースを登録
server.registerResource(
  {
    uri: "file://documents/{name}",
    name: "Document Resource",
    description: "Access documents by name",
    mimeType: "text/plain"
  },
  async (uri: string) => {
    // URI からパラメータを抽出
    const match = uri.match(/^file:\/\/documents\/(.+)$/);
    if (!match) {
      throw new Error("Invalid URI format");
    }

    const documentName = match[1];
    const content = await loadDocument(documentName);

    return {
      contents: [{
        uri,
        mimeType: "text/plain",
        text: content
      }]
    };
  }
);

// 利用可能なリソースを動的に一覧表示
server.registerResourceList(async () => {
  const documents = await getAvailableDocuments();
  return {
    resources: documents.map(doc => ({
      uri: `file://documents/${doc.name}`,
      name: doc.name,
      mimeType: "text/plain",
      description: doc.description
    }))
  };
});
```

**リソースとツールの使い分け:**
- **リソース**: シンプルな URI ベースのパラメータでのデータアクセス
- **ツール**: バリデーションとビジネスロジックを必要とする複雑な操作
- **リソース**: データが比較的静的またはテンプレートベースの場合
- **ツール**: 操作に副作用や複雑なワークフローがある場合

### トランスポートオプション

TypeScript SDK は2つの主要なトランスポートメカニズムをサポートしています:

#### Streamable HTTP（リモートサーバーに推奨）

```typescript
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";

const app = express();
app.use(express.json());

app.post('/mcp', async (req, res) => {
  // 各リクエストに新しいトランスポートを作成（ステートレス、リクエスト ID の衝突を防止）
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true
  });

  res.on('close', () => transport.close());

  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

app.listen(3000);
```

#### stdio（ローカル統合用）

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const transport = new StdioServerTransport();
await server.connect(transport);
```

**トランスポートの選択:**
- **Streamable HTTP**: Web サービス、リモートアクセス、複数クライアント
- **stdio**: コマンドラインツール、ローカル開発、サブプロセス統合

### 通知サポート

サーバーの状態が変化したときにクライアントに通知:

```typescript
// ツールリストが変更されたときに通知
server.notification({
  method: "notifications/tools/list_changed"
});

// リソースが変更されたときに通知
server.notification({
  method: "notifications/resources/list_changed"
});
```

通知は控えめに使用 — サーバーの機能が本当に変化したときのみ。

---

## コードベストプラクティス

### コードの構成可能性と再利用性

実装は構成可能性とコード再利用を優先しなければなりません:

1. **共通機能を抽出**:
   - 複数のツールで使用される操作の再利用可能なヘルパー関数を作成
   - コードの重複ではなく、HTTP リクエスト用の共有 API クライアントを構築
   - エラーハンドリングロジックをユーティリティ関数に集約
   - ビジネスロジックを合成可能な専用関数に抽出
   - 共有の Markdown または JSON フィールド選択・フォーマット機能を抽出

2. **重複を避ける**:
   - ツール間で類似のコードをコピー＆ペーストしない
   - 類似のロジックを2回書いている場合は関数に抽出
   - ページネーション、フィルタリング、フィールド選択、フォーマットなどの共通操作は共有
   - 認証/認可ロジックは集約

## ビルドと実行

TypeScript コードは実行前に必ずビルド:

```bash
# プロジェクトのビルド
npm run build

# サーバーの実行
npm start

# 自動リロード付き開発
npm run dev
```

`npm run build` が正常に完了することを、実装完了と見なす前に必ず確認してください。

## 品質チェックリスト

Node/TypeScript MCP サーバーの実装を完了する前に確認:

### 戦略的設計
- [ ] ツールが API エンドポイントのラッパーではなく、完全なワークフローを可能にする
- [ ] ツール名が自然なタスクの細分化を反映している
- [ ] レスポンスフォーマットがエージェントのコンテキスト効率を最適化している
- [ ] 適切な箇所で人間が読める識別子を使用している
- [ ] エラーメッセージがエージェントを正しい使用方法に導く

### 実装品質
- [ ] 集中した実装: 最も重要で価値のあるツールを実装
- [ ] すべてのツールが完全な設定で `registerTool` を使用して登録
- [ ] すべてのツールに `title`, `description`, `inputSchema`, `annotations` を含む
- [ ] アノテーションが正しく設定（readOnlyHint, destructiveHint, idempotentHint, openWorldHint）
- [ ] すべてのツールが `.strict()` エンフォースメント付き Zod スキーマでランタイム入力バリデーション
- [ ] すべての Zod スキーマに適切な制約と説明的なエラーメッセージ
- [ ] すべてのツールに明示的な入出力型を含む包括的な説明
- [ ] 説明に戻り値の例と完全なスキーマドキュメントを含む
- [ ] エラーメッセージが明確で実行可能、教育的

### TypeScript の品質
- [ ] すべてのデータ構造に TypeScript インターフェースを定義
- [ ] tsconfig.json で Strict TypeScript を有効化
- [ ] `any` 型を使用しない — `unknown` または適切な型を使用
- [ ] すべての async 関数に明示的な Promise<T> 戻り値型
- [ ] エラーハンドリングに適切な型ガードを使用（例: `axios.isAxiosError`, `z.ZodError`）

### 高度な機能（該当する場合）
- [ ] 適切なデータエンドポイントにリソースを登録
- [ ] 適切なトランスポートを設定（stdio または Streamable HTTP）
- [ ] 動的サーバー機能の通知を実装
- [ ] SDK インターフェースで型安全

### プロジェクト設定
- [ ] package.json に必要なすべての依存関係を含む
- [ ] ビルドスクリプトが dist/ ディレクトリに動作する JavaScript を生成
- [ ] メインエントリーポイントが dist/index.js として正しく設定
- [ ] サーバー名がフォーマットに従う: `{service}-mcp-server`
- [ ] tsconfig.json が strict モードで適切に設定

### コード品質
- [ ] 該当する箇所でページネーションを適切に実装
- [ ] 大きなレスポンスが CHARACTER_LIMIT 定数をチェックし、明確なメッセージ付きでトランケート
- [ ] 大きくなる可能性のある結果セットにフィルタリングオプションを提供
- [ ] すべてのネットワーク操作がタイムアウトと接続エラーを適切に処理
- [ ] 共通機能を再利用可能な関数に抽出
- [ ] 類似操作間で戻り値の型が一貫

### テストとビルド
- [ ] `npm run build` がエラーなく正常に完了
- [ ] dist/index.js が作成され実行可能
- [ ] サーバーが実行可能: `node dist/index.js --help`
- [ ] すべてのインポートが正しく解決
- [ ] サンプルツール呼び出しが期待通りに動作
