---
name: react-state
description: React状態管理 - Context + Reducerパターンとオプティミスティック更新。
---

# React状態管理パターン

Reactでアプリケーションの状態を管理するためのパターン。

## 使う場面

- グローバル状態の管理
- 離れたコンポーネント間で状態共有
- 複数アクションを伴う複雑な状態
- オプティミスティックUI更新

## Context + Reducerパターン

```tsx
// State types
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

type AppAction =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'TOGGLE_THEME' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string };

// Initial state
const initialState: AppState = {
  user: null,
  theme: 'light',
  notifications: [],
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' };
    case 'ADD_NOTIFICATION':
      return { ...state, notifications: [...state.notifications, action.payload] };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    default:
      return state;
  }
}

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: Dispatch<AppAction>;
} | null>(null);

// Provider
function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook
function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}

// Usage
function Header() {
  const { state, dispatch } = useApp();

  return (
    <header>
      <span>Welcome, {state.user?.name}</span>
      <button onClick={() => dispatch({ type: 'TOGGLE_THEME' })}>
        Toggle Theme
      </button>
    </header>
  );
}
```

## パフォーマンスのためのContext分割

```tsx
// stateとdispatchを分離して不要な再描画を防ぐ
const AppStateContext = createContext<AppState | null>(null);
const AppDispatchContext = createContext<Dispatch<AppAction> | null>(null);

function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}

// 分離されたフック
function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) throw new Error('useAppState must be used within AppProvider');
  return context;
}

function useAppDispatch() {
  const context = useContext(AppDispatchContext);
  if (!context) throw new Error('useAppDispatch must be used within AppProvider');
  return context;
}

// 必要なものだけ購読する
function ThemeToggle() {
  const dispatch = useAppDispatch(); // state変更で再描画されない
  return (
    <button onClick={() => dispatch({ type: 'TOGGLE_THEME' })}>
      Toggle
    </button>
  );
}
```

## オプティミスティック更新

```tsx
function useOptimisticTodos() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const addTodo = useCallback(async (text: string) => {
    // 楽観的更新
    const tempId = `temp-${Date.now()}`;
    const optimisticTodo = { id: tempId, text, completed: false };
    setTodos(prev => [...prev, optimisticTodo]);

    try {
      // 実際のAPI呼び出し
      const newTodo = await api.createTodo(text);

      // 楽観的更新を実データに置換
      setTodos(prev =>
        prev.map(t => (t.id === tempId ? newTodo : t))
      );
    } catch (error) {
      // エラー時にロールバック
      setTodos(prev => prev.filter(t => t.id !== tempId));
      throw error;
    }
  }, []);

  const toggleTodo = useCallback(async (id: string) => {
    // 楽観的更新
    setTodos(prev =>
      prev.map(t => (t.id === id ? { ...t, completed: !t.completed } : t))
    );

    try {
      await api.toggleTodo(id);
    } catch (error) {
      // ロールバック
      setTodos(prev =>
        prev.map(t => (t.id === id ? { ...t, completed: !t.completed } : t))
      );
      throw error;
    }
  }, []);

  const deleteTodo = useCallback(async (id: string) => {
    // ロールバック用に保持
    const deletedTodo = todos.find(t => t.id === id);

    // 楽観的削除
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await api.deleteTodo(id);
    } catch (error) {
      // ロールバック
      if (deletedTodo) {
        setTodos(prev => [...prev, deletedTodo]);
      }
      throw error;
    }
  }, [todos]);

  return { todos, addTodo, toggleTodo, deleteTodo };
}
```

## セレクタパターン

```tsx
// 派生状態のセレクタを作成
const selectCompletedTodos = (state: AppState) =>
  state.todos.filter(t => t.completed);

const selectIncompleteTodos = (state: AppState) =>
  state.todos.filter(t => !t.completed);

const selectTodoCount = (state: AppState) => ({
  total: state.todos.length,
  completed: state.todos.filter(t => t.completed).length,
});

// useMemoと併用して性能を確保
function TodoStats() {
  const state = useAppState();
  const counts = useMemo(() => selectTodoCount(state), [state.todos]);

  return (
    <div>
      {counts.completed} / {counts.total} completed
    </div>
  );
}
```

## アクション作成関数

```tsx
// 型安全のためのアクションヘルパー
const actions = {
  setUser: (user: User | null): AppAction => ({
    type: 'SET_USER',
    payload: user,
  }),
  toggleTheme: (): AppAction => ({
    type: 'TOGGLE_THEME',
  }),
  addNotification: (notification: Notification): AppAction => ({
    type: 'ADD_NOTIFICATION',
    payload: notification,
  }),
  removeNotification: (id: string): AppAction => ({
    type: 'REMOVE_NOTIFICATION',
    payload: id,
  }),
};

// Usage
function LoginButton() {
  const dispatch = useAppDispatch();

  const handleLogin = async () => {
    const user = await loginAPI();
    dispatch(actions.setUser(user));
    dispatch(actions.addNotification({
      id: Date.now().toString(),
      message: 'Logged in successfully',
      type: 'success',
    }));
  };

  return <button onClick={handleLogin}>Login</button>;
}
```

## 関連スキル

- [react-hooks](react-hooks.md): カスタムフック
- [react-components](react-components.md): コンポーネントパターン
- [react-performance](react-performance.md): パフォーマンス最適化
