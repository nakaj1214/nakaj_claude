---
name: react-patterns
description: 2024+向けのReactコンポーネント設計パターンとベストプラクティス。詳細は関連スキル参照。
sources:
  - https://blog.bitsrc.io/react-design-patterns-for-2024-5f2696868222
  - https://refine.dev/blog/react-design-patterns/
---

# React設計パターン スキル

Reactコンポーネント設計パターンとベストプラクティスの包括的ガイド。

## このスキルを使う場面

- 新しいReactコンポーネントの構築
- 既存コンポーネントのリファクタ
- Reactコードのレビュー
- Reactアプリの設計
- コンポーネント性能の最適化

## クイックリファレンス

このスキルは以下のサブスキルに分割:

| スキル | 説明 |
|-------|-------------|
| [react-hooks](react-hooks.md) | カスタムフック: useToggle, useDebounce, useLocalStorage など |
| [react-components](react-components.md) | コンパウンド、レンダープロップ、HOC、コンテナ/プレゼンテーション |
| [react-state](react-state.md) | Context + Reducer、オプティミスティック更新、セレクタ |
| [react-performance](react-performance.md) | メモ化、コード分割、仮想化 |

## 必須パターン

### カスタムフック

```tsx
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setLoading(false));
  }, [userId]);

  return { user, loading };
}
```

### コンパウンドコンポーネント

```tsx
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab id="profile">Profile</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="profile">Content</Tabs.Panel>
</Tabs>
```

### メモ化

```tsx
const filteredItems = useMemo(
  () => items.filter(item => item.name.includes(filter)),
  [items, filter]
);

const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);

const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  return <div>{/* Expensive render */}</div>;
});
```

## フォルダ構成

```
src/
  components/
    common/           # 再利用UIコンポーネント
    features/         # 機能別コンポーネント
  hooks/              # カスタムフック
  contexts/           # Contextプロバイダ
  pages/              # ルートコンポーネント
  services/           # API層
  types/              # TypeScript型
```

## 関連スキル

- [react-hooks](react-hooks.md): カスタムフックパターン
- [react-components](react-components.md): コンポーネントパターン
- [react-state](react-state.md): 状態管理
- [react-performance](react-performance.md): パフォーマンス最適化
- [css-modern](css-modern.md): モダンCSS手法
- [tdd-workflow](tdd-workflow.md): テスト駆動開発
