---
name: z-paging
description: "Create and configure z-paging components for uni-app (Vue2/Vue3, nvue/vue, all platforms). z-paging is a high-performance paging list component supporting pull-to-refresh, load-more, virtual lists, chat record mode, local paging, data caching, and more. Use when building paginated lists, implementing pull-to-refresh, load-more, virtual scrolling, chat UIs, or any list-based page in uni-app projects."
---

# z-paging Skill

> **Source**: [GitHub](https://github.com/SmileZXLee/uni-z-paging) | **Docs**: [z-paging.zxlee.cn](https://z-paging.zxlee.cn) | **Version**: v2.8.8

## Quick Start

The core pattern is **two steps**:
1. Bind `@query` to your data-fetching method (z-paging auto-calculates `pageNo` & `pageSize`)
2. Bind `v-model` to your list array, call `complete()` with the result

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <text>{{ item.title }}</text>
    </view>
  </z-paging>
</template>

<script>
export default {
  data() { return { dataList: [] } },
  methods: {
    async queryList(pageNo, pageSize) {
      const res = await api.getList({ pageNo, pageSize });
      this.$refs.paging.complete(res.data.list);
      // On error: this.$refs.paging.complete(false);
    }
  }
}
</script>
```

## Layout Modes

| Mode | Prop | Use Case |
|------|------|----------|
| **Fixed** (default) | `:fixed="true"` | Full-page list, content inside z-paging, top/bottom via slots |
| **Non-fixed** | `:fixed="false"` | Inside modals/swipers, needs explicit height |
| **Page scroll** | `:use-page-scroll="true"` + mixins | Content starts below a custom view, page-level scroll |

## Key Concepts

### Data Flow
- `@query(pageNo, pageSize, from)` — triggered on mount (if `auto=true`), pull-down, scroll-to-bottom
- `complete(data)` — pass result array; auto-detects no-more when `length < pageSize`
- `complete(false)` — signal request failure
- `completeByTotal(data, total)` — when backend returns total count
- `completeByNoMore(data, noMore)` — manually control no-more state
- `reload()` — reset to page 1 and re-fetch
- `refresh()` — re-fetch current loaded pages without resetting

### Slots
- `top` — fixed top area (nav bar, tabs)
- `bottom` — fixed bottom area (input bar, tabbar)
- `left` / `right` — fixed side panels
- `refresher` — custom pull-to-refresh view (scope: `{ refresherStatus }`)
- `empty` — custom empty state (scope: `{ isLoadFailed }`)
- `loading` — custom full-screen loading
- `loadingMoreDefault/Loading/NoMore/Fail` — custom load-more states
- `cell` — for virtual/inner list mode (scope: `{ item, index }`)
- `header` / `footer` — for virtual/inner list mode
- `chatLoading` / `chatNoMore` — chat record mode
- `f2` / `refresherF2` — pull-down-to-second-floor

### Fetch (Simplified API, v2.7.8+)
```vue
<z-paging :fetch="queryList" :fetch-params="{ type: 1 }" v-model="dataList">
```
Pass a function that receives `{ pageNo, pageSize, ...extraParams }` and returns the list array.

## Common Patterns

### Delayed Load (e.g., load tabs first)
```vue
<z-paging ref="paging" :auto="false" v-model="dataList" @query="queryList">
```
Call `this.$refs.paging.reload()` after tabs are ready.

### Local Paging
```js
// Server returns all data at once, z-paging handles local pagination
this.$refs.paging.setLocalPaging(res.data.list);
```

### Data Caching
```vue
<z-paging use-cache cache-key="goodsList" v-model="dataList" @query="queryList">
```

### Virtual List (10k+ items)
```vue
<z-paging use-virtual-list v-model="dataList" @query="queryList">
  <template #cell="{ item, index }">
    <view>{{ item.title }}</view>
  </template>
</z-paging>
```
- `cell-height-mode`: `fixed` (default, fast) or `dynamic` (slower, flexible)
- `preload-page`: default 12, increase for fast-scroll scenarios

### Chat Record Mode
```vue
<z-paging use-chat-record-mode v-model="chatList" @query="queryChatList">
  <template #cell="{ item }">
    <chat-bubble :item="item" />
  </template>
</z-paging>
```

### Custom Refresher
```vue
<z-paging v-model="dataList" @query="queryList">
  <template #refresher="{ refresherStatus }">
    <my-custom-refresher :status="refresherStatus" />
  </template>
</z-paging>
```

### Pull-Down-to-Second-Floor (v2.7.7+)
```vue
<z-paging refresher-f2-enabled v-model="dataList" @query="queryList">
  <template #f2>
    <second-floor-page />
  </template>
</z-paging>
```

## Global Config (main.js)
```js
uni.$zp = {
  config: {
    'default-page-size': 15,
    'empty-view-text': '暂无数据',
    'loading-more-no-more-text': '没有更多了',
  }
}
```

## Important Notes

- In **nvue**, child items of z-paging must be wrapped in `<cell>`
- `pageSize` prop must match the backend's pageSize
- In Page `onLoad()`, use `setTimeout` or `nextTick` to access `this.$refs`
- When using page-scroll mode, import the provided mixins
- For virtual lists: do NOT use `margin-top`/`margin-bottom` on cells (use padding instead)

## Reference Files

For detailed API documentation, see the `reference/` directory:
- `reference/props.md` — All props organized by module
- `reference/events.md` — All events
- `reference/methods.md` — All methods
- `reference/slots.md` — All slots
- `reference/examples.md` — Complete code examples
