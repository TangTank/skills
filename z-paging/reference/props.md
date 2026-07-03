# z-paging Props Reference

## 数据&布局配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `v-model` | 绑定列表渲染变量 | Array | - |
| `default-page-no` | 初始pageNo | Number | 1 |
| `default-page-size` | 每页条数（须与后端一致） | Number | 10 |
| `fixed` | 是否使用fixed布局 | Boolean | true |
| `layout-only` | 仅使用基础布局，关闭自动请求/下拉刷新/加载更多/空数据图 | Boolean | false |
| `safe-area-inset-bottom` | 底部安全区域适配 | Boolean | false |
| `use-safe-area-placeholder` | 安全区域是否用placeholder形式 | Boolean | false |
| `use-page-scroll` | 使用页面滚动（须引入mixins） | Boolean | false |
| `auto-full-height` | 页面滚动时不满屏自动填满 | Boolean | true |
| `default-theme-style` | loading主题样式 | String | black |
| `paging-style` | 设置z-paging的style | Object | - |
| `paging-class` | 设置z-paging的class | String/Array/Object | - |
| `height` | z-paging高度 | String | - |
| `width` | z-paging宽度 | String | - |
| `max-width` | 最大宽度（设置后自动margin:0 auto） | String | - |
| `bg-color` | 背景色 | String | - |
| `bottom-bg-color` | bottom区域背景色 | String | transparent |
| `watch-touch-direction-change` | 监听触摸方向改变 | Boolean | false |
| `watch-scroll-direction-change` | 监听滚动方向改变 | Boolean | false |
| `delay` | 调用complete后延迟处理(ms) | Number/String | 0 |
| `min-delay` | 触发@query后最小延迟(ms) | Number/String | 0 |
| `call-network-reject` | 请求失败是否触发reject | Boolean | true |
| `unit` | 内置布局单位 | String | rpx |
| `concat` | 自动拼接complete中的数组 | Boolean | true |
| `data-key` | tab切换时的数据一致性key | Number/String/Object | - |
| `autowire-list-name` | 极简写法：自动注入list名 | String | "" |
| `autowire-query-name` | 极简写法：自动注入query名 | String | "" |
| `fetch` | 极简写法：获取分页数据Function | Function | null |
| `fetch-params` | fetch的附加参数 | Object | null |
| `in-swiper-slot` | 是否在swiper-item中使用 | Boolean | false |

## reload相关配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `auto` | mounted后自动调用reload | Boolean | true |
| `auto-scroll-to-top-when-reload` | reload时自动滚动到顶部 | Boolean | true |
| `auto-clean-list-when-reload` | reload时自动清空原list | Boolean | true |
| `show-refresher-when-reload` | 刷新时自动显示下拉刷新view | Boolean | false |
| `show-loading-more-when-reload` | 刷新时自动显示加载更多view | Boolean | false |
| `created-reload` | created时立即触发reload | Boolean | false |

## 下拉刷新配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `refresher-enabled` | 是否开启下拉刷新 | Boolean | true |
| `refresher-threshold` | 下拉刷新阈值 | Number/String | 80rpx |
| `use-refresher-status-bar-placeholder` | 下拉刷新状态栏占位 | Boolean | false |
| `refresher-only` | 仅使用下拉刷新 | Boolean | false |
| `use-custom-refresher` | 使用自定义下拉刷新 | Boolean | true |
| `show-refresher-when-reload` | 刷新时显示下拉刷新view | Boolean | false |
| `reload-when-refresh` | 下拉刷新时触发reload | Boolean | true |
| `refresher-theme-style` | 下拉刷新主题样式 | String | black |
| `refresher-img-style` | 左侧图标样式 | Object | {} |
| `refresher-title-style` | 右侧文字样式 | Object | {} |
| `refresher-update-time-style` | 更新时间文字样式 | Object | {} |
| `watch-refresher-touchmove` | 实时监听下拉刷新进度 | Boolean | false |
| `show-refresher-update-time` | 显示最后更新时间 | Boolean | false |
| `refresher-update-time-key` | 更新时间缓存key | String | default |
| `refresher-default-text` | 默认状态文字 | String/Object | 继续下拉刷新 |
| `refresher-pulling-text` | 松手刷新文字 | String/Object | 松开立即刷新 |
| `refresher-refreshing-text` | 刷新中文字 | String/Object | 正在刷新... |
| `refresher-complete-text` | 刷新结束文字 | String/Object | 刷新成功 |
| `refresher-default-img` | 默认状态图片 | String | - |
| `refresher-pulling-img` | 松手状态图片 | String | - |
| `refresher-refreshing-img` | 刷新中图片 | String | - |
| `refresher-complete-img` | 刷新结束图片 | String | - |
| `refresher-refreshing-animated` | 刷新中是否展示旋转动画 | Boolean | true |
| `refresher-end-bounce-enabled` | 刷新结束回弹动画 | Boolean | true |
| `refresher-default-style` | 系统下拉刷新默认样式 | String | black |
| `refresher-background` | 下拉刷新区域背景色 | String | #FFFFFF00 |
| `refresher-fixed-background` | 固定下拉刷新区域背景色 | String | #FFFFFF00 |
| `refresher-fixed-bac-height` | 固定下拉刷新区域高度 | Number/String | 0 |
| `refresher-default-duration` | 默认状态回弹动画时间(ms) | Number/String | 100 |
| `refresher-complete-delay` | 刷新结束延迟收回时间(ms) | Number/String | 0 |
| `refresher-complete-duration` | 刷新结束收回动画时间(ms) | Number/String | 300 |
| `refresher-vibrate` | 松手刷新时手机短振动 | Boolean | false |
| `refresher-refreshing-scrollable` | 刷新中是否允许滚动 | Boolean | true |
| `refresher-complete-scrollable` | 刷新结束是否允许滚动 | Boolean | false |
| `refresher-out-rate` | 超出阈值后位移衰减比例 | Number | 0.65 |
| `refresher-f2-enabled` | 开启下拉进入二楼 | Boolean | false |
| `refresher-f2-threshold` | 进入二楼阈值 | Number/String | 200rpx |
| `refresher-f2-duration` | 进入二楼动画时间(ms) | Number/String | 200 |
| `show-refresher-f2` | 松手后是否弹出二楼 | Boolean | true |
| `refresher-pull-rate` | 实际位移与下拉距离比值 | Number | 0.75 |
| `refresher-fps` | 下拉刷新帧率 | Number/String | 40 |
| `refresher-max-angle` | 允许触发的最大下拉角度 | Number/String | 40 |
| `refresher-angle-enable-change-continued` | 角度变化时是否继续手势 | Boolean | false |
| `refresher-no-transform` | 禁止下拉刷新view跟随移动 | Boolean | false |

## 底部加载更多配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `loading-more-enabled` | 启用加载更多 | Boolean | true |
| `lower-threshold` | 触发scrolltolower的距离 | Number/String | 100rpx |
| `to-bottom-loading-more-enabled` | 启用滑动到底部加载更多 | Boolean | true |
| `show-loading-more-when-reload` | 刷新时显示加载更多view | Boolean | false |
| `loading-more-theme-style` | 加载更多主题样式 | String | black |
| `loading-more-custom-style` | 自定义加载更多样式 | Object | - |
| `loading-more-title-custom-style` | 自定义加载更多文字样式 | Object | - |
| `loading-more-loading-icon-custom-style` | 自定义加载中动画样式 | Object | - |
| `loading-more-loading-icon-type` | 加载中动画图标类型 | String | flower |
| `loading-more-loading-icon-custom-image` | 自定义加载中动画图片 | String | - |
| `loading-more-loading-animated` | 加载中view是否展示旋转动画 | Boolean | true |
| `loading-more-default-text` | "默认"文字 | String/Object | 点击加载更多 |
| `loading-more-loading-text` | "加载中"文字 | String/Object | 正在加载... |
| `loading-more-no-more-text` | "没有更多"文字 | String/Object | 没有更多了 |
| `loading-more-fail-text` | "加载失败"文字 | String/Object | 加载失败，点击重新加载 |
| `hide-no-more-inside` | 内容未满屏时隐藏没有更多 | Boolean | false |
| `hide-no-more-by-limit` | 数组长度少于该值时隐藏没有更多 | Number | 0 |
| `inside-more` | 未满一屏时自动加载更多 | Boolean | false |
| `loading-more-default-as-loading` | 默认状态以加载中展示 | Boolean | false |
| `show-loading-more-no-more-view` | 是否显示没有更多view | Boolean | true |
| `show-default-loading-more-text` | 是否显示默认加载更多text | Boolean | true |
| `show-loading-more-no-more-line` | 是否显示没有更多分割线 | Boolean | true |
| `loading-more-no-more-line-custom-style` | 自定义没有更多分割线样式 | Object | - |

## 虚拟列表配置 (v2.2.5+)

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `use-virtual-list` | 使用虚拟列表 | Boolean | false |
| `use-compatibility-mode` | 虚拟列表兼容模式（微信小程序推荐） | Boolean | false |
| `extra-data` | 兼容模式附加数据 | Object | null |
| `cell-height-mode` | cell高度模式 | String | fixed |
| `preload-page` | 预加载页数 | Number/String | 12 |
| `fixed-cell-height` | 固定cell高度 | Number/String | 0 |
| `virtual-list-col` | 虚拟列表列数 | Number/String | 1 |
| `virtual-scroll-fps` | 虚拟列表scroll帧率 | Number/String | 80 |
| `use-inner-list` | 使用内置列表 | Boolean | false |
| `force-close-inner-list` | 强制关闭inner-list | Boolean | false |
| `virtual-in-swiper-slot` | 虚拟列表是否在swiper-item中 | Boolean | false |
| `cell-key-name` | 内置列表cell的key名称(nvue) | String | "" |
| `inner-list-style` | innerList样式 | Object | {} |
| `inner-cell-style` | innerCell样式 | Object | {} |

## 本地分页配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `local-paging-loading-time` | 本地分页加载更多延迟(ms) | Number | 200 |

## 缓存配置 (v2.3.9+)

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `use-cache` | 使用缓存 | Boolean | false |
| `cache-key` | 缓存key（use-cache=true时必须） | String | null |
| `cache-mode` | 缓存模式 | String | default |

## 聊天记录模式配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `use-chat-record-mode` | 使用聊天记录模式 | Boolean | false |
| `auto-hide-keyboard-when-chat` | 自动隐藏键盘 | Boolean | true |
| `auto-adjust-position-when-chat` | 键盘弹出时自动调整底部高度 | Boolean | true |
| `auto-to-bottom-when-chat` | 键盘弹出时自动滚动到底部 | Boolean | false |
| `chat-adjust-position-offset` | 键盘弹出占位偏移距离 | String | 0px |
| `show-chat-loading-when-reload` | reload时显示chatLoading | Boolean | false |
| `chat-loading-more-default-as-loading` | 顶部默认状态以加载中展示 | Boolean | true |

## 返回顶部按钮配置 (v1.5.1+)

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `auto-show-back-to-top` | 自动显示返回顶部按钮 | Boolean | false |
| `back-to-top-threshold` | 显示/隐藏阈值(滚动距离) | Number/String | 400rpx |
| `back-to-top-img` | 自定义按钮图片 | String | 内置图片 |
| `back-to-top-with-animate` | 返回顶部时展示动画 | Boolean | true |
| `back-to-top-bottom` | 按钮与底部距离 | Number/String | 160rpx |
| `back-to-top-style` | 按钮自定义样式 | Object | {} |

## 空数据图配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `hide-empty-view` | 强制隐藏空数据图 | Boolean | false |
| `empty-view-fixed` | 空数据图是否铺满z-paging | Boolean | false |
| `empty-view-center` | 空数据图是否垂直居中 | Boolean | true |
| `empty-view-text` | 空数据图描述文字 | String/Object | - |
| `empty-view-img` | 空数据图图片 | String | - |
| `empty-view-error-img` | 加载失败图片 | String | - |
| `empty-view-reload-text` | 重新加载文字 | String/Object | - |
| `empty-view-error-text` | 加载失败描述文字 | String/Object | - |
| `empty-view-super-style` | 空数据图父view样式 | Object | - |
| `empty-view-style` | 空数据图样式 | Object | - |
| `empty-view-img-style` | 空数据图img样式 | Object | - |
| `empty-view-title-style` | 描述文字样式 | Object | - |
| `empty-view-reload-style` | 重新加载按钮样式 | Object | - |
| `show-empty-view-reload` | 显示重新加载按钮(无数据时) | Boolean | false |
| `show-empty-view-reload-when-error` | 加载失败时显示重新加载按钮 | Boolean | true |
| `auto-hide-empty-view-when-loading` | 加载中自动隐藏空数据图 | Boolean | true |
| `auto-hide-empty-view-when-pull` | 下拉刷新时自动隐藏空数据图 | Boolean | true |

## z-index配置

| Prop | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `top-z-index` | slot=top的z-index | Number | 99 |
| `super-content-z-index` | 内容容器父view的z-index | Number | 1 |
| `content-z-index` | 内容容器的z-index | Number | 1 |
| `empty-view-z-index` | 空数据view的z-index | Number | 9 |
