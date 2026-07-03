# z-paging Methods Reference

调用方式: `this.$refs.paging.xxx()` (假设ref="paging")

> 注意: 在Page的onLoad()中无法同步获取this.$refs，请加setTimeout或nextTick

## 数据刷新&处理方法

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `reload(showRefresher?)` | 重新加载分页数据，pageNo恢复默认值 | `showRefresher`: Boolean, 是否展示下拉刷新动画, 默认false | Promise({totalList, noMore}) |
| `refresh()` | 刷新当前已加载的数据(不重置pageNo/pageSize) | - | Promise({totalList, noMore}) |
| `refreshToPage(page)` | 刷新列表至指定页 | `page`: 目标页数(必填) | Promise({totalList, noMore}) |
| `complete(data, success?)` | 请求结束调用，传结果数组 | `data`: 结果数组(必填); `success`: Boolean, 默认true, 失败时传false | Promise({totalList, noMore}) |
| `completeByTotal(data, total, success?)` | 通过total判断是否有更多数据 | `data`: 结果数组; `total`: 总长度; `success`: Boolean | Promise({totalList, noMore}) |
| `completeByNoMore(data, noMore, success?)` | 自行判断是否有更多数据 | `data`: 结果数组; `noMore`: Boolean是否没有更多; `success`: Boolean | Promise({totalList, noMore}) |
| `completeByError(error)` | 传入请求失败原因 | `error`: 失败原因(必填) | Promise({totalList, noMore}) |
| `completeByKey(data, dataKey, success?)` | 保证数据一致性 | `data`: 结果数组; `dataKey`: 与:data-key一致; `success`: Boolean | Promise({totalList, noMore}) |
| `clear()` | 清空分页数据，pageNo恢复默认 | - | - |
| `addDataFromTop(data, scrollToTop?, animate?)` | 从顶部添加数据(不影响pageNo/pageSize) | `data`: 数据(必填); `scrollToTop`: Boolean, 默认true; `animate`: Boolean, 默认true | - |
| `resetTotalData(list)` | 重新设置列表数据(不影响pageNo/pageSize，不触发请求) | `list`: 修改后的列表数组(必填) | - |

## 下拉刷新相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `endRefresh()` | 终止下拉刷新状态 | - |
| `updateCustomRefresherHeight()` | 手动更新自定义下拉刷新view高度 | - |
| `closeF2()` | 手动关闭二楼 | - |

## 底部加载更多相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `doLoadMore(type?)` | 手动触发上拉加载更多 | `type`: `click` 或 `toBottom`, 默认`click` |

## 页面滚动&布局相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `updatePageScrollTop(scrollTop)` | 页面滚动时告知当前scrollTop(页面滚动+自定义下拉刷新时必须) | `scrollTop`: 从onPageScroll获取的scrollTop(必填) |
| `updatePageScrollTopHeight()` | 更新slot=top的高度(页面滚动+top内容动态变化时调用) | - |
| `updatePageScrollBottomHeight()` | 更新slot=bottom的高度(页面滚动+bottom内容动态变化时调用) | - |
| `updateLeftAndRightWidth()` | 更新slot=left/right宽度(宽度动态改变后调用) | - |
| `updateFixedLayout()` | 更新fixed模式下布局(iOS+h5+tabbar场景) | - |

## 虚拟列表相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `doInsertVirtualListItem(item, index)` | 动态高度虚拟列表中插入item | `item`: 插入的数据; `index`: 插入位置(从0开始) |
| `didUpdateVirtualListCell(index)` | 更新指定cell的缓存高度 | `index`: cell位置(从0开始) |
| `didDeleteVirtualListCell(index)` | 删除指定cell的缓存高度 | `index`: cell位置(从0开始) |
| `updateVirtualListRender()` | 手动触发虚拟列表渲染更新 | - |

## 本地分页相关方法

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `setLocalPaging(data, success?)` | 设置本地分页数据 | `data`: 结果数组(必填); `success`: Boolean, 默认true | Promise({totalList, noMore}) |

## 聊天记录模式相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `doChatRecordLoadMore()` | 手动触发滚动到顶部加载更多 | - |
| `addChatRecordData(data, scrollToBottom?, animate?)` | 添加聊天记录 | `data`: 数据(必填); `scrollToBottom`: Boolean, 默认true; `animate`: Boolean, 默认true |
| `addKeyboardHeightChangeListener()` | 手动添加键盘高度变化监听 | - |

## 滚动到指定位置方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `scrollToTop(animate?)` | 滚动到顶部 | `animate`: Boolean, 默认true |
| `scrollToBottom(animate?)` | 滚动到底部 | `animate`: Boolean, 默认true |
| `scrollIntoViewById(id, offset?, animate?)` | 滚动到指定view(vue有效) | `id`: view的id(不含#); `offset`: 偏移量px, 默认0; `animate`: Boolean, 默认false |
| `scrollIntoViewByNodeTop(top, offset?, animate?)` | 滚动到指定view(vue有效) | `top`: view的top值; `offset`: px, 默认0; `animate`: Boolean, 默认false |
| `scrollToY(y, offset?, animate?)` | y轴滚动到指定位置(vue有效) | `y`: 与顶部距离px; `offset`: px, 默认0; `animate`: Boolean, 默认false |
| `scrollToX(x, offset?, animate?)` | x轴滚动到指定位置(vue有效, 非页面滚动) | `x`: 与左侧距离px; `offset`: px, 默认0; `animate`: Boolean, 默认false |
| `scrollIntoViewByIndex(index, offset?, animate?)` | 滚动到指定view(nvue/虚拟列表2.7.8有效) | `index`: view的index; `offset`: px, 默认0; `animate`: Boolean, 默认false |
| `scrollIntoViewByView(view, offset?, animate?)` | 滚动到指定view(nvue有效) | `view`: 通过this.$refs.xxx获取; `offset`: px, 默认0; `animate`: Boolean, 默认false |

## 缓存相关方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `updateCache()` | 手动更新列表缓存数据(自动截取前pageSize条覆盖缓存) | - |

## 其他方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `getVersion()` | 获取当前版本号 | - |
| `setListSpecialEffects(config)` / `setSpecialEffects(config)` | 设置nvue List的specialEffects(nvue独有) | config: 参见uni-app文档 |
