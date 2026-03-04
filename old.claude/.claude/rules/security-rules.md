# セキュリティルール

これらのルールは、コードの記述やレビュー時に常に従わなければならない。

## 1. シークレットのハードコード禁止

### ルール
シークレット、認証情報、API キー、機密データをコードにハードコードしないこと。

### 違反例
```typescript
// ❌ 絶対にやってはいけない
const API_KEY = "sk_live_abc123xyz789";
const DB_PASSWORD = "mypassword123";
const SECRET_TOKEN = "super-secret-token";
```

### 正しいアプローチ
```typescript
// ✅ 環境変数を使用する
const API_KEY = process.env.API_KEY;
const DB_PASSWORD = process.env.DB_PASSWORD;
const SECRET_TOKEN = process.env.SECRET_TOKEN;

// ✅ 存在確認を行う
if (!API_KEY) {
  throw new Error('API_KEY environment variable is required');
}
```

### 検出方法
- パターンのスキャン: `password`, `secret`, `key`, `token`, `api_key`
- 代入文内の認証情報のような文字列をチェック
- .env ファイルが .gitignore に含まれているか確認

## 2. 入力バリデーション

### ルール
すべてのユーザー入力は処理前に必ずバリデーションすること。

### 要件
- 型のバリデーション
- フォーマットのバリデーション
- 長さのバリデーション
- 範囲のバリデーション
- 特殊文字のサニタイズ

### 例
```typescript
// ❌ バリデーションなし
function createUser(email: string, age: number) {
  db.query(`INSERT INTO users (email, age) VALUES ('${email}', ${age})`);
}

// ✅ 適切なバリデーション
function createUser(email: string, age: number) {
  // 型のバリデーション
  if (typeof email !== 'string' || typeof age !== 'number') {
    throw new ValidationError('Invalid types');
  }

  // フォーマットのバリデーション
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format');
  }

  // 範囲のバリデーション
  if (age < 0 || age > 150) {
    throw new ValidationError('Invalid age range');
  }

  // 長さのバリデーション
  if (email.length > 255) {
    throw new ValidationError('Email too long');
  }

  // パラメータ化クエリを使用
  db.query('INSERT INTO users (email, age) VALUES (?, ?)', [email, age]);
}
```

## 3. SQL インジェクション防止

### ルール
常にパラメータ化クエリまたは ORM を使用すること。ユーザー入力を SQL に結合しないこと。

### 違反例
```typescript
// ❌ SQL インジェクション脆弱性
const query = `SELECT * FROM users WHERE id = ${userId}`;
const query = `SELECT * FROM users WHERE name = '${userName}'`;
db.execute(query);
```

### 正しいアプローチ
```typescript
// ✅ パラメータ化クエリ
db.query('SELECT * FROM users WHERE id = ?', [userId]);

// ✅ ORM を使用
await User.findOne({ where: { id: userId } });

// ✅ 名前付きパラメータ
db.query('SELECT * FROM users WHERE name = :name', { name: userName });
```

## 4. XSS 防止

### ルール
HTML にレンダリングする前に、すべてのユーザー生成コンテンツをエスケープすること。

### 違反例
```typescript
// ❌ XSS 脆弱性
function displayComment(comment: string) {
  return `<div>${comment}</div>`;
}
```

### 正しいアプローチ
```typescript
// ✅ HTML をエスケープ
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function displayComment(comment: string) {
  return `<div>${escapeHtml(comment)}</div>`;
}

// ✅ フレームワークの組み込み機能を使用（React）
function Comment({ text }: { text: string }) {
  return <div>{text}</div>; // React が自動エスケープ
}
```

## 5. 認証と認可

### ルール
- パスワードは必ず bcrypt または argon2 でハッシュ化すること
- セッショントークンは暗号学的に安全な乱数を使用すること
- 認可チェックはすべてのリクエストで行うこと
- レート制限を実装すること

### パスワードハッシュ化
```typescript
// ❌ 平文または弱いハッシュ
const password = userInput;
const hash = md5(password); // 弱い
const hash = sha1(password); // 弱い

// ✅ 適切なハッシュ化
import bcrypt from 'bcrypt';

const saltRounds = 12;
const hash = await bcrypt.hash(password, saltRounds);

// 検証
const isValid = await bcrypt.compare(inputPassword, storedHash);
```

### セッション管理
```typescript
// ✅ 安全なセッショントークン生成
import crypto from 'crypto';

function generateSessionToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// ✅ セッション設定
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,      // HTTPS のみ
    httpOnly: true,    // JavaScript からアクセス不可
    sameSite: 'strict', // CSRF 保護
    maxAge: 3600000    // 1時間
  }
}));
```

### 認可
```typescript
// ✅ すべての保護されたルートでチェック
function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
}

function requireRole(role: string) {
  return (req, res, next) => {
    if (req.user.role !== role) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

app.get('/admin', requireAuth, requireRole('admin'), handler);
```

## 6. コマンドインジェクション防止

### ルール
サニタイズされていないユーザー入力でシェルコマンドを実行しないこと。

### 違反例
```typescript
// ❌ コマンドインジェクション脆弱性
exec(`convert ${userFileName} output.jpg`);
```

### 正しいアプローチ
```typescript
// ✅ バリデーションとサニタイズ
function sanitizeFileName(fileName: string): string {
  // 英数字、ドット、ハイフンのみ許可
  return fileName.replace(/[^a-zA-Z0-9.-]/g, '');
}

const safeFileName = sanitizeFileName(userFileName);
exec(`convert ${safeFileName} output.jpg`);

// ✅ より良い方法: シェルコマンドの代わりにライブラリを使用
import sharp from 'sharp';
await sharp(userFileName).toFile('output.jpg');

// ✅ 最善の方法: 配列引数で spawn を使用（シェル補間なし）
import { spawn } from 'child_process';
spawn('convert', [userFileName, 'output.jpg']);
```

## 7. パストラバーサル防止

### ルール
ディレクトリトラバーサル攻撃を防ぐためにファイルパスをバリデーションすること。

### 違反例
```typescript
// ❌ パストラバーサル脆弱性
app.get('/file/:name', (req, res) => {
  const filePath = `./uploads/${req.params.name}`;
  res.sendFile(filePath);
});
// 攻撃者が使用可能: /file/../../etc/passwd
```

### 正しいアプローチ
```typescript
// ✅ パスのバリデーション
import path from 'path';

app.get('/file/:name', (req, res) => {
  const uploadsDir = path.resolve('./uploads');
  const filePath = path.resolve(uploadsDir, req.params.name);

  // パスが uploads ディレクトリ内であることを確認
  if (!filePath.startsWith(uploadsDir)) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  res.sendFile(filePath);
});
```

## 8. CSRF 保護

### ルール
状態を変更する操作には CSRF トークンを実装すること。

### 実装
```typescript
// ✅ CSRF 保護ミドルウェア
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/submit', csrfProtection, (req, res) => {
  // フォームの処理
});

// ✅ HTML 内
<form method="POST">
  <input type="hidden" name="_csrf" value="{{csrfToken}}">
  <!-- フォームフィールド -->
</form>
```

## 9. セキュアヘッダー

### ルール
常にセキュリティヘッダーを設定すること。

### 実装
```typescript
// ✅ helmet.js を使用
import helmet from 'helmet';

app.use(helmet());

// ✅ 手動設定
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});
```

## 10. エラーハンドリング

### ルール
エラーメッセージで機密情報を公開しないこと。

### 違反例
```typescript
// ❌ 情報漏洩
catch (err) {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    query: sql
  });
}
```

### 正しいアプローチ
```typescript
// ✅ 安全なエラーハンドリング
catch (err) {
  // サーバーサイドで詳細なエラーをログ出力
  logger.error('Database error', {
    error: err,
    query: sql,
    user: req.user.id
  });

  // クライアントには汎用的なエラーを送信
  res.status(500).json({
    error: 'An error occurred while processing your request'
  });
}
```

## セキュリティチェックリスト

コードをコミットする前に確認すること:

- [ ] シークレットや認証情報がハードコードされていない
- [ ] すべてのユーザー入力がバリデーションされている
- [ ] SQL クエリがパラメータ化されている
- [ ] HTML 出力がエスケープされている
- [ ] パスワードが適切にハッシュ化されている（bcrypt/argon2）
- [ ] 保護されたルートで認証が強制されている
- [ ] 認可チェックが実施されている
- [ ] コマンドインジェクション脆弱性がない
- [ ] ファイルパスがバリデーションされている
- [ ] CSRF 保護が実装されている
- [ ] セキュリティヘッダーが設定されている
- [ ] エラーメッセージが情報を漏洩していない
- [ ] レート制限が実装されている
- [ ] 本番環境で HTTPS が強制されている
- [ ] 依存関係が最新である

## 自動チェック

CI/CD で以下を自動化すべき:

```bash
# 依存関係の脆弱性スキャン
npm audit

# 静的解析
npm run lint:security

# シークレットスキャン
git-secrets --scan

# ライセンスコンプライアンス
npm run license-check
```

## インシデント対応

セキュリティ脆弱性が発見された場合:

1. **停止** — 現在の作業を直ちに中止する
2. **エスカレーション** — **security-reviewer** エージェントに委任する
3. **修正** — 再開前に重大な欠陥を修正する
4. **ローテーション** — 漏洩が発生した場合は認証情報を変更する
5. **監査** — コードベース全体で同様の脆弱性がないかレビューする

## エスカレーションが必要な場合

以下の場合は直ちにセキュリティチームにエスカレーションすること:
- データ漏洩の可能性を発見した場合
- 認証バイパスが見つかった場合
- 権限昇格が可能な場合
- シークレットがリポジトリにコミットされた場合
- 本番環境の認証情報が漏洩した場合
