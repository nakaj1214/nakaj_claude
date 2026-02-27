---
name: react-performance
description: Reactパフォーマンス最適化 - メモ化、コード分割、仮想化のパターン。
---

# Reactパフォーマンス最適化

Reactアプリのパフォーマンスを最適化するためのパターンとテクニック。

## 使う場面

- コンポーネント描画が遅い
- 大量リストでラグが発生
- バンドルサイズ削減
- 初期表示時間の改善

## メモ化

### useMemoで高コスト計算を回避

```tsx
function FilteredList({ items, filter }: Props) {
  const filteredItems = useMemo(
    () => items.filter(item => item.name.includes(filter)),
    [items, filter]
  );

  return (
    <ul>
      {filteredItems.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
  );
}
```

### useCallbackで安定した関数参照を作る

```tsx
function Parent() {
  const [count, setCount] = useState(0);

  // useCallbackなし: 毎回新しい関数
  // const handleClick = () => console.log('Clicked');

  // useCallbackあり: 参照が安定
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []); // deps空 = 変更なし

  const handleIncrement = useCallback(() => {
    setCount(c => c + 1);
  }, []); // 関数型更新で依存を回避

  return (
    <>
      <ExpensiveChild onClick={handleClick} />
      <button onClick={handleIncrement}>Count: {count}</button>
    </>
  );
}
```

### React.memoでコンポーネントをメモ化

```tsx
// propsが変わった時だけ再描画
const ExpensiveComponent = memo(function ExpensiveComponent({ data }: Props) {
  return <div>{/* Expensive render */}</div>;
});

// カスタム比較関数付き
const DeepCompareComponent = memo(
  function DeepCompareComponent({ config }: Props) {
    return <div>{/* ... */}</div>;
  },
  (prevProps, nextProps) => {
    return JSON.stringify(prevProps.config) === JSON.stringify(nextProps.config);
  }
);
```

## コード分割

### コンポーネントの遅延読み込み

```tsx
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

### Named exportの遅延読み込み

```tsx
// 名前付きexportはdefaultへラップ
const { Chart } = lazy(() =>
  import('./components/Charts').then(module => ({
    default: module.Chart
  }))
);
```

### 事前読み込み

```tsx
// ホバー時にプリロード
const Settings = lazy(() => import('./pages/Settings'));

function NavLink() {
  const preloadSettings = () => {
    import('./pages/Settings');
  };

  return (
    <Link
      to="/settings"
      onMouseEnter={preloadSettings}
      onFocus={preloadSettings}
    >
      Settings
    </Link>
  );
}
```

## 仮想化

### 基本的な仮想化リスト

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // 推定行高さ
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: virtualRow.size,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 高さ可変アイテム

```tsx
function VariableHeightList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback((index) => {
      // コンテンツに応じて推定サイズを返す
      return items[index].content.length > 100 ? 100 : 50;
    }, [items]),
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            ref={virtualizer.measureElement}
            data-index={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <ItemComponent item={items[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 再レンダリング回避

### 状態の持ち上げを適切に行う

```tsx
// NG: カウント更新で全体が再描画
function App() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <Counter count={count} setCount={setCount} />
      <ExpensiveTree /> {/* 毎回再描画される */}
    </div>
  );
}

// OK: 状態を隔離して再描画を最小化
function App() {
  return (
    <div>
      <CounterWrapper /> {/* ここだけ再描画 */}
      <ExpensiveTree /> {/* 再描画されない */}
    </div>
  );
}

function CounterWrapper() {
  const [count, setCount] = useState(0);
  return <Counter count={count} setCount={setCount} />;
}
```

### Children as Propsパターン

```tsx
// コンポーネントは再描画されるがchildrenは再描画されない
function ScrollContainer({ children }: { children: ReactNode }) {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div>
      <div>Scroll: {scrollY}</div>
      {children} {/* childrenは再描画されない */}
    </div>
  );
}

// Usage
function App() {
  return (
    <ScrollContainer>
      <ExpensiveComponent /> {/* スクロールで再描画されない */}
    </ScrollContainer>
  );
}
```

## プロファイリング

### React DevTools Profilerの利用

```tsx
// Profilerを追加して描画時間を測定
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) {
  console.log({ id, phase, actualDuration, baseDuration });
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <MyComponent />
    </Profiler>
  );
}
```

## 関連スキル

- [react-hooks](react-hooks.md): カスタムフック
- [react-components](react-components.md): コンポーネントパターン
- [react-state](react-state.md): 状態管理
