# React Hooks 完整指南

## 什么是 Hooks？

Hooks 是 React 16.8 引入的新特性，允许在函数组件中使用 state 和其他 React 特性，无需编写 class 组件。

## useState - 状态管理

### 基本用法

```jsx
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>点击了 {count} 次</p>
      <button onClick={() => setCount(count + 1)}>
        点击我
      </button>
    </div>
  );
}
```

**核心概念：**
- `useState` 返回一对值：当前状态和更新函数
- 初始值只在首次渲染时使用
- 更新函数触发组件重新渲染

### 多个状态变量

```jsx
function UserProfile() {
  const [name, setName] = useState('张三');
  const [age, setAge] = useState(25);
  const [email, setEmail] = useState('zhangsan@example.com');

  return (
    <div>
      <h2>{name}</h2>
      <p>年龄：{age}</p>
      <p>邮箱：{email}</p>
    </div>
  );
}
```

## useEffect - 副作用处理

### 基本用法

```jsx
import React, { useState, useEffect } from 'react';

function DataFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 组件挂载时执行
    fetch('https://api.example.com/data')
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []); // 空依赖数组 = 仅在挂载时执行一次

  if (loading) return <div>加载中...</div>;
  return <div>{JSON.stringify(data)}</div>;
}
```

### 清理副作用

```jsx
function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(s => s + 1);
    }, 1000);

    // 清理函数：组件卸载时执行
    return () => clearInterval(interval);
  }, []);

  return <div>已运行 {seconds} 秒</div>;
}
```

**关键点：**
- 返回的清理函数在组件卸载或依赖变化前执行
- 避免内存泄漏的重要机制

### 依赖数组

```jsx
function SearchResults({ query }) {
  const [results, setResults] = useState([]);

  useEffect(() => {
    // 当 query 变化时重新搜索
    searchAPI(query).then(setResults);
  }, [query]); // query 变化时重新执行

  return (
    <ul>
      {results.map(item => <li key={item.id}>{item.title}</li>)}
    </ul>
  );
}
```

## useContext - 跨组件传递数据

```jsx
import React, { createContext, useContext, useState } from 'react';

// 创建 Context
const ThemeContext = createContext();

function App() {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  return (
    <div>
      <ThemedButton />
    </div>
  );
}

function ThemedButton() {
  // 使用 Context
  const { theme, setTheme } = useContext(ThemeContext);

  return (
    <button 
      style={{ background: theme === 'light' ? '#fff' : '#333' }}
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      切换主题
    </button>
  );
}
```

**优势：**
- 避免 props drilling（层层传递）
- 全局状态管理的轻量方案

## useReducer - 复杂状态管理

```jsx
import React, { useReducer } from 'react';

// Reducer 函数
function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return [...state, { id: Date.now(), text: action.text, done: false }];
    case 'TOGGLE_TODO':
      return state.map(todo =>
        todo.id === action.id ? { ...todo, done: !todo.done } : todo
      );
    case 'DELETE_TODO':
      return state.filter(todo => todo.id !== action.id);
    default:
      return state;
  }
}

function TodoApp() {
  const [todos, dispatch] = useReducer(todoReducer, []);
  const [input, setInput] = useState('');

  const addTodo = () => {
    dispatch({ type: 'ADD_TODO', text: input });
    setInput('');
  };

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={addTodo}>添加</button>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => dispatch({ type: 'TOGGLE_TODO', id: todo.id })}
            />
            {todo.text}
            <button onClick={() => dispatch({ type: 'DELETE_TODO', id: todo.id })}>
              删除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**适用场景：**
- 状态逻辑复杂
- 多个子状态相互依赖
- 需要可预测的状态更新

## useRef - 持久化引用

### DOM 引用

```jsx
function TextInputWithFocus() {
  const inputRef = useRef(null);

  const focusInput = () => {
    inputRef.current.focus();
  };

  return (
    <div>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>聚焦输入框</button>
    </div>
  );
}
```

### 保存可变值

```jsx
function Stopwatch() {
  const [time, setTime] = useState(0);
  const intervalRef = useRef(null);

  const start = () => {
    intervalRef.current = setInterval(() => {
      setTime(t => t + 1);
    }, 1000);
  };

  const stop = () => {
    clearInterval(intervalRef.current);
  };

  return (
    <div>
      <p>时间：{time}秒</p>
      <button onClick={start}>开始</button>
      <button onClick={stop}>停止</button>
    </div>
  );
}
```

**特点：**
- 修改 `.current` 不触发重新渲染
- 在组件生命周期内保持不变
- 适合存储定时器 ID、DOM 节点等

## 自定义 Hook

```jsx
// 自定义 Hook：窗口大小监听
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return size;
}

// 使用自定义 Hook
function ResponsiveComponent() {
  const { width } = useWindowSize();

  return (
    <div>
      {width < 768 ? '移动端视图' : '桌面端视图'}
    </div>
  );
}
```

## Hooks 规则

1. **只在顶层调用**：不要在循环、条件或嵌套函数中调用
2. **只在 React 函数中调用**：函数组件或自定义 Hook 中
3. **命名规范**：自定义 Hook 必须以 `use` 开头

## 性能优化 Hooks

### useMemo

```jsx
function ExpensiveComponent({ items, filter }) {
  const filteredItems = useMemo(() => {
    console.log('执行过滤计算');
    return items.filter(item => item.category === filter);
  }, [items, filter]); // 只在依赖变化时重新计算

  return <List items={filteredItems} />;
}
```

### useCallback

```jsx
function ParentComponent() {
  const [count, setCount] = useState(0);

  // 缓存函数引用，避免子组件不必要的重渲染
  const handleClick = useCallback(() => {
    console.log('点击了按钮');
  }, []); // 空依赖 = 函数引用永不改变

  return (
    <div>
      <p>计数：{count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
      <ChildComponent onClick={handleClick} />
    </div>
  );
}
```

## 总结

| Hook | 用途 | 常见场景 |
|------|------|----------|
| useState | 状态管理 | 表单输入、开关状态 |
| useEffect | 副作用处理 | API 请求、订阅、定时器 |
| useContext | 跨组件传递 | 主题、用户信息 |
| useReducer | 复杂状态 | 购物车、表单验证 |
| useRef | 持久引用 | DOM 操作、保存定时器 ID |
| useMemo | 缓存计算结果 | 昂贵计算优化 |
| useCallback | 缓存函数引用 | 防止子组件重渲染 |

Hooks 让函数组件拥有了与 class 组件同等的能力，同时代码更简洁、逻辑更清晰。
