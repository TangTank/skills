# z-paging Slots Reference

> 注意: slot插入的view必须是z-paging的直接子view；slot节点不支持v-if/v-show动态显示/隐藏，需在子节点上控制。

## 主体布局Slot

| Slot | 说明 |
|------|------|
| `top` | 固定在顶部的元素(导航栏、tab-view等)，不跟随滚动。多个view请用一个view包住。页面滚动模式下内容动态变化后需调用`updatePageScrollTopHeight()` |
| `bottom` | 固定在底部的元素，不跟随滚动。多个view请用一个view包住。页面滚动模式下内容动态变化后需调用`updatePageScrollBottomHeight()` |
| `left` | 固定在左侧的元素。夹在top和bottom之间。需滚动请自行插入scroll-view |
| `right` | 固定在右侧的元素。夹在top和bottom之间。需滚动请自行插入scroll-view |

## 下拉刷新Slot

| Slot | 说明 | Scope |
|------|------|-------|
| `refresher` | 自定义下拉刷新view(需设`use-custom-refresher="true"`) | `{ refresherStatus }` — `default` / `release-to-refresh` / `loading` / `complete` / `go-f2` |
| `refresherComplete` | 自定义结束状态下的下拉刷新view(需设`refresher-complete-delay`) | - |
| `refresherF2` | 自定义松手显示二楼状态的view | - |
| `f2` | 自定义需要插入二楼的view | - |

## 底部加载更多Slot

| Slot | 说明 |
|------|------|
| `loadingMoreDefault` | 自定义"默认"(点击加载更多)状态view |
| `loadingMoreLoading` | 自定义"加载中"状态view |
| `loadingMoreNoMore` | 自定义"没有更多数据"状态view |
| `loadingMoreFail` | 自定义"加载失败"状态view |

## 空数据图Slot

| Slot | 说明 | Scope |
|------|------|-------|
| `empty` | 自定义空数据占位view | `{ isLoadFailed }` — true:加载失败, false:加载成功 |

## 全屏Loading Slot

| Slot | 说明 |
|------|------|
| `loading` | 自定义页面reload时的加载view。默认仅第一次加载显示，设`auto-hide-loading-after-first-loaded="false"`可每次显示 |

## 返回顶部按钮Slot

| Slot | 说明 |
|------|------|
| `backToTop` | 自定义返回顶部view(父view默认76rpx) |

## 虚拟列表&内置列表Slot

| Slot | 说明 | Scope |
|------|------|-------|
| `cell` | 内置列表中的cell | `{ item, index }` |
| `header` | 内置列表中的header(在cell顶部，跟随滚动) | - |
| `footer` | 内置列表中的footer(在cell底部，跟随滚动) | - |

## 聊天记录模式Slot

| Slot | 说明 | Scope |
|------|------|-------|
| `chatLoading` | 自定义顶部加载更多view(除没有更多数据外) | `{ loadingMoreStatus }` — `default` / `loading` / `no-more` / `fail` |
| `chatNoMore` | 自定义没有更多数据view | - |
