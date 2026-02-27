---
name: react-hooks
description: Reactカスタムフックパターン - 状態を伴うロジックを抽出して再利用する。
---

# Reactカスタムフックパターン

状態を伴うロジックを抽出し、コンポーネント間で再利用する。

## 使う場面

- コンポーネント間でロジックを共有したいとき
- 複雑な状態管理を抽出したいとき
- 再利用可能なデータフェッチを作りたいとき
- コンポーネントコードを簡潔にしたいとき

## カスタムフックパターン

### Before: コンポーネント内にロジックが混在

```tsx
function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/user')
      .then(res => res.json())
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, []);

  // ... render logic
}
```

### After: ロジックをカスタムフックへ抽出

```tsx
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        if (!cancelled) {
          setUser(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { user, loading, error };
}

// クリーンなコンポーネント
function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error } = useUser(userId);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{user?.name}</div>;
}
```

## よく使うカスタムフック

### useToggle

```tsx
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle] as const;
}

// Usage
function Modal() {
  const [isOpen, toggleOpen] = useToggle(false);

  return (
    <>
      <button onClick={toggleOpen}>Open Modal</button>
      {isOpen && <ModalContent onClose={toggleOpen} />}
    </>
  );
}
```

### useLocalStorage

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// Usage
function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <select value={theme} onChange={e => setTheme(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  );
}
```

### useDebounce

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      // Fetch search results
      searchAPI(debouncedQuery);
    }
  }, [debouncedQuery]);

  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}
```

### usePrevious

```tsx
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}

// Usage
function Counter() {
  const [count, setCount] = useState(0);
  const prevCount = usePrevious(count);

  return (
    <div>
      Now: {count}, Before: {prevCount}
    </div>
  );
}
```

### useAsync

```tsx
function useAsync<T>(asyncFn: () => Promise<T>, deps: any[] = []) {
  const [state, setState] = useState<{
    loading: boolean;
    error: Error | null;
    data: T | null;
  }>({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    let cancelled = false;

    setState(prev => ({ ...prev, loading: true }));

    asyncFn()
      .then(data => {
        if (!cancelled) {
          setState({ loading: false, error: null, data });
        }
      })
      .catch(error => {
        if (!cancelled) {
          setState({ loading: false, error, data: null });
        }
      });

    return () => {
      cancelled = true;
    };
  }, deps);

  return state;
}

// Usage
function UserList() {
  const { data: users, loading, error } = useAsync(
    () => fetch('/api/users').then(r => r.json()),
    []
  );

  if (loading) return <Spinner />;
  if (error) return <Error error={error} />;

  return <ul>{users?.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### useOnClickOutside

```tsx
function useOnClickOutside(
  ref: RefObject<HTMLElement>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

// Usage
function Dropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useOnClickOutside(dropdownRef, () => setIsOpen(false));

  return (
    <div ref={dropdownRef}>
      <button onClick={() => setIsOpen(!isOpen)}>Menu</button>
      {isOpen && <DropdownMenu />}
    </div>
  );
}
```

## フックのルール

1. **トップレベルでのみ呼び出す** - ループ/条件分岐/ネスト関数内では呼ばない
2. **React関数からのみ呼び出す** - 関数コンポーネントかカスタムフック内で使う
3. **カスタムフック名はuseで始める** - ルールのlintが効く

## 関連スキル

- [react-components](react-components.md): コンポーネントパターン
- [react-state](react-state.md): 状態管理
- [react-performance](react-performance.md): パフォーマンス最適化
