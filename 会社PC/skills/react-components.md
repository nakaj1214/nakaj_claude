---
name: react-components
description: Reactコンポーネントパターン - コンパウンド、レンダープロップ、HOC、コンテナ/プレゼンテーション分離。
---

# Reactコンポーネントパターン

柔軟で再利用可能なReactコンポーネントを構築するための設計パターン。

## 使う場面

- コンポーネントライブラリの構築
- 柔軟なAPI設計
- コンポーネント間のロジック共有
- 関心の分離

## コンパウンドコンポーネントパターン

柔軟で合成可能なコンポーネントAPIを作る。

```tsx
const TabsContext = createContext<{
  activeTab: string;
  setActiveTab: (tab: string) => void;
} | null>(null);

function Tabs({ children, defaultTab }: { children: ReactNode; defaultTab: string }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: ReactNode }) {
  return <div className="tab-list" role="tablist">{children}</div>;
}

function Tab({ id, children }: { id: string; children: ReactNode }) {
  const context = useContext(TabsContext);
  if (!context) throw new Error('Tab must be used within Tabs');

  const { activeTab, setActiveTab } = context;

  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
      className={activeTab === id ? 'active' : ''}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }: { id: string; children: ReactNode }) {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabPanel must be used within Tabs');

  if (context.activeTab !== id) return null;

  return <div role="tabpanel">{children}</div>;
}

// サブコンポーネントを紐付け
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage
function App() {
  return (
    <Tabs defaultTab="profile">
      <Tabs.List>
        <Tabs.Tab id="profile">Profile</Tabs.Tab>
        <Tabs.Tab id="settings">Settings</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel id="profile">Profile content</Tabs.Panel>
      <Tabs.Panel id="settings">Settings content</Tabs.Panel>
    </Tabs>
  );
}
```

## レンダープロップパターン

ロジックを共有しつつ描画を柔軟にする。

```tsx
interface MousePosition {
  x: number;
  y: number;
}

function MouseTracker({ render }: { render: (pos: MousePosition) => ReactNode }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return <>{render(position)}</>;
}

// Usage
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        <div>Mouse position: {x}, {y}</div>
      )}
    />
  );
}
```

## 高階コンポーネント（HOC）

追加機能でコンポーネントを拡張する。

```tsx
// withAuth HOC
function withAuth<P extends object>(Component: ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();

    if (loading) return <Spinner />;
    if (!user) return <Navigate to="/login" />;

    return <Component {...props} />;
  };
}

// withErrorBoundary HOC
function withErrorBoundary<P extends object>(
  Component: ComponentType<P>,
  fallback: ReactNode
) {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

// Usage
const ProtectedDashboard = withAuth(Dashboard);
const SafeChart = withErrorBoundary(Chart, <div>Failed to load chart</div>);
```

## コンテナ/プレゼンテーションパターン

ロジックと見た目を分離する。

```tsx
// プレゼンテーションコンポーネント（純UI）
interface UserListProps {
  users: User[];
  loading: boolean;
  onDelete: (id: string) => void;
}

function UserListView({ users, loading, onDelete }: UserListProps) {
  if (loading) return <Spinner />;

  return (
    <ul className="user-list">
      {users.map(user => (
        <li key={user.id}>
          <span>{user.name}</span>
          <button onClick={() => onDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}

// コンテナコンポーネント（ロジック）
function UserListContainer() {
  const { users, loading, deleteUser } = useUsers();

  return (
    <UserListView
      users={users}
      loading={loading}
      onDelete={deleteUser}
    />
  );
}
```

## エラーバウンダリ

```tsx
class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
    // エラー報告サービスへ送信
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <DefaultErrorUI error={this.state.error} />;
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <Router />
    </ErrorBoundary>
  );
}
```

## Propsインターフェースのベストプラクティス

```tsx
// 良い例: 明示的で説明があるprops
interface ButtonProps {
  /** Button variant style */
  variant?: 'primary' | 'secondary' | 'ghost';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Loading state shows spinner */
  loading?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Button content */
  children: ReactNode;
}

function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
}
```

## 制御コンポーネントと非制御コンポーネント

```tsx
// Controlled: 親が状態を管理
function ControlledInput({ value, onChange }: ControlledProps) {
  return <input value={value} onChange={e => onChange(e.target.value)} />;
}

// Uncontrolled: コンポーネントが状態を持つ
function UncontrolledInput({ defaultValue, onSubmit }: UncontrolledProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (inputRef.current) {
      onSubmit(inputRef.current.value);
    }
  };

  return (
    <>
      <input ref={inputRef} defaultValue={defaultValue} />
      <button onClick={handleSubmit}>Submit</button>
    </>
  );
}
```

## 関連スキル

- [react-hooks](react-hooks.md): カスタムフック
- [react-state](react-state.md): 状態管理
- [react-performance](react-performance.md): パフォーマンス最適化
