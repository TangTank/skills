# z-paging Events Reference

## 数据处理相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@query` | 下拉刷新或滚动到底部时自动触发。z-paging加载时也会触发(设`:auto="false"`可禁止) | `pageNo, pageSize, from`<br>from: `user-pull-down`(下拉刷新) / `reload`(reload触发) / `refresh`(refresh触发) / `load-more`(滚动到底部加载更多) |
| `@listChange` | 分页渲染的数组改变时触发 | 最终的分页数据数组 |

## 下拉刷新相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@refresherStatusChange` | 下拉刷新状态改变 | `default` / `release-to-refresh` / `loading` / `complete` / `go-f2` |
| `@refresherTouchstart` | 下拉开始(nvue无效) | 触摸开始的y值(px) |
| `@refresherTouchmove` | 下拉拖动中(需设`:watch-refresher-touchmove="true"`) | `{pullingDistance, dy, viewHeight, rate}` |
| `@refresherTouchend` | 下拉结束(nvue无效) | 触摸结束的y值(px) |
| `@refresherF2Change` | 下拉进入二楼状态改变 | `go`(二楼开启) / `close`(二楼关闭) |
| `@onRefresh` | 自定义下拉刷新被触发 | - |
| `@onRestore` | 自定义下拉刷新被复位 | - |

## 底部加载更多相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@loadingStatusChange` | 底部加载更多状态改变 | `default` / `loading` / `no-more` / `fail` |

## 空数据与加载失败相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@emptyViewReload` | 点击空数据图重新加载按钮 | 回调函数(是否reload，默认true) |
| `@emptyViewClick` | 点击空数据图view | - |
| `@isLoadFailedChange` | 请求失败状态改变 | Boolean |

## 返回顶部按钮相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@backToTopClick` | 点击返回顶部按钮 | 回调函数(是否滚动到顶部，默认true) |

## 虚拟列表&内置列表相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@virtualListChange` | 虚拟列表当前渲染数组改变 | 虚拟列表当前渲染的数组 |
| `@innerCellClick` | 使用虚拟列表/内置列表时点击cell | `(item, index)` |
| `@virtualPlaceholderTopHeight` | 虚拟列表顶部占位高度改变 | 高度(px) |

## 聊天记录模式相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@hidedKeyboard` | 触摸列表隐藏了键盘(nvue无效) | - |
| `@keyboardHeightChange` | 键盘高度改变(仅聊天记录模式有效) | `{height}` |

## 滚动相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@scroll` | 列表滚动时触发 | vue: `event.detail = {scrollLeft, scrollTop, scrollHeight, scrollWidth, deltaX, deltaY}`<br>nvue: `{contentSize, contentOffset, isDragging}` |
| `@scrollTopChange` | scrollTop改变时触发 | scrollTop值 |
| `@scrolltolower` | 滚动到底部时触发 | - |
| `@scrolltoupper` | 滚动到顶部时触发 | - |
| `@scrollend` | list滚动结束时触发(仅nvue) | `{contentSize, contentOffset, isDragging}` |

## 布局&交互相关事件

| Event | 说明 | 回调参数 |
|-------|------|----------|
| `@contentHeightChanged` | 内容高度改变时触发 | 改变后的高度 |
| `@touchDirectionChange` | 触摸方向改变(nvue无效，需设`:watch-touch-direction-change="true"`) | `top` / `bottom` |
| `@scrollDirectionChange` | 滚动方向改变(页面滚动模式无效，需设`:watch-scroll-direction-change="true"`) | `top` / `bottom` |
