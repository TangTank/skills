---
name: watermark-camera
description: 水印相机模块开发指南。涵盖组件架构、双水印系统（主水印/预览水印）、Canvas渲染、样式隔离、小程序适配等关键模式和常见陷阱。
---

# 水印相机模块开发指南

> 本技能适用于 `@src/pages_camera` 模块的开发和维护。
> 该模块是项目中最复杂的交互模块之一，涉及相机、Canvas渲染、水印系统、弹窗交互等多个子系统。

---

## 1. 模块架构概览

```
pages_camera/
├── camera/
│   ├── camera.vue                    # 主页面（相机+主水印+拍照逻辑）
│   ├── components/
│   │   ├── markList/
│   │   │   └── markList.vue          # 水印模板选择弹窗（含预览水印）
│   │   ├── water-setting/
│   │   │   └── waterSettingPanel.vue # 水印设置面板
│   │   ├── watermark-renderer/
│   │   │   └── watermark-renderer.vue # 水印渲染组件
│   │   ├── preset-list/
│   │   │   └── WatermarkPresetList.vue # 水印预设列表
│   │   └── common/
│   │       └── api/env.ts            # 环境配置
│   ├── composables/
│   │   ├── useCanvasRenderer.ts      # Canvas渲染逻辑
│   │   ├── useWatermarkConfig.ts     # 水印配置管理
│   │   ├── useWatermarkAlbum.ts      # 相册管理
│   │   ├── useShutterSound.ts        # 快门音效
│   │   └── weatherLocation.ts        # 位置信息
│   ├── config/
│   │   ├── watermarkPresets.ts       # 水印预设定义
│   │   ├── watermarkFields.ts        # 水印字段配置
│   │   ├── watermarkConfigFactory.ts # 水印配置工厂
│   │   ├── watermarkVariants.ts      # 水印变体
│   │   ├── layouts.ts                # 布局配置
│   │   ├── themes.ts                 # 主题配置
│   │   └── types.ts                  # 类型定义
│   └── utils/
│       └── dateFormat.ts             # 日期格式化
└── static/                           # 静态资源
```

---

## 2. 核心概念：双水印系统

**这是最容易出错的地方！** 系统中有两个独立的水印实例：

### 2.1 主水印（Main Watermark）
- **位置**: `camera.vue` 中的 `WatermarkRenderer` 组件
- **用途**: 拍照时合成到照片上
- **位置**: 固定在相机预览区域的左下角（`position: fixed`）
- **特点**: 
  - 始终存在于相机页面
  - 位置由 `wmTop` 和 `wmLeft` 计算属性控制
  - 支持拖动调整位置

### 2.2 预览水印（Preview Watermark）
- **位置**: `markList.vue` 中的 `WatermarkRenderer` 组件
- **用途**: 在水印模板选择弹窗中预览效果
- **位置**: 相对于弹窗容器定位
- **特点**:
  - 仅在弹窗打开时显示
  - 使用模拟数据渲染（非真实位置/时间）
  - 与主水印共享相同的渲染组件

### 2.3 常见错误：混淆两个水印

❌ **错误做法**: 
```vue
<!-- 在camera.vue中同时渲染主水印和预览水印 -->
<WatermarkRenderer ref="waterMarkObj" ... /> <!-- 主水印 -->
<WatermarkRenderer ref="previewWaterMark" ... /> <!-- 预览水印 -->
```

✅ **正确做法**:
```vue
<!-- camera.vue: 只有主水印 -->
<WatermarkRenderer v-if="!templateListDialogShow" ref="waterMarkObj" ... />

<!-- markList.vue: 预览水印在弹窗组件内部 -->
<WatermarkRenderer ref="waterMarkObj2" ... />
```

---

## 3. 水印位置管理

### 3.1 主水印位置计算

```typescript
// camera.vue
const wmTop = computed(() => {
  const heightOff = tempSize.value.height / 2
  let tempY = touchY.value
  // 防止越界
  if (tempY > showHeight.value - heightOff) {
    tempY = showHeight.value - heightOff
  }
  if (tempY < heightOff) {
    tempY = heightOff
  }
  tempY = tempY - heightOff
  return showHeight.value - tempY - tempSize.value.height
})

const wmLeft = computed(() => {
  const widthOff = tempSize.value.width / 2
  let tempX = touchX.value
  // 防止越界
  if (tempX > showWidth.value - widthOff) {
    tempX = showWidth.value - widthOff
  }
  if (tempX < widthOff) {
    tempX = widthOff
  }
  tempX = tempX - widthOff
  return tempX
})
```

### 3.2 初始位置设置

```typescript
// onLoad
onLoad((opt: any) => {
  showWidth.value = uni.getSystemInfoSync().windowWidth
  showHeight.value = showWidth.value / rate.value
  // 初始位置：左下角
  touchY.value = showHeight.value
})
```

### 3.3 常见位置问题

**问题**: 设置水印后位置变成居中
**原因**: 重置了 `touchX` 和 `touchY` 的值
**解决**: 保持原有的位置值，只更新配置

**问题**: 水印位置超出容器
**原因**: 没有处理边界情况
**解决**: 使用 `wmTop` 和 `wmLeft` 的边界检查逻辑

---

## 4. 样式隔离（关键！）

### 4.1 必须使用 defineOptions

在微信小程序中，组件样式会相互干扰。**所有水印相关组件必须添加**：

```vue
<script setup lang="ts">
defineOptions({
  name: 'ComponentName',
  options: {
    virtualHost: true,
    styleIsolation: 'shared',
  },
})
</script>
```

### 4.2 需要添加 defineOptions 的组件

- `markList.vue`
- `waterSettingPanel.vue`
- `WatermarkRenderer.vue`
- `WatermarkPresetList.vue`
- 所有 `wm-*.vue` 水印模板组件

### 4.3 样式穿透问题

如果父组件样式影响到子组件，使用 `:deep()` 选择器：

```scss
// 父组件
:deep(.child-class) {
  // 样式
}
```

---

## 5. Canvas 渲染（小程序适配）

### 5.1 Canvas 2D API 差异

微信小程序的 Canvas 2D API 与 Web 标准有差异：

```typescript
// ❌ Web 标准写法（小程序不支持）
const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')

// ✅ 小程序写法
const query = uni.createSelectorQuery()
query.select('#canvas')
  .fields({ node: true, size: true })
  .exec((res) => {
    const canvas = res[0].node
    const ctx = canvas.getContext('2d')
  })
```

### 5.2 图片加载

```typescript
// ❌ Web 标准写法
const img = new Image()
img.src = url
img.onload = () => { ... }

// ✅ 小程序写法
const img = canvas.createImage()
img.onload = () => { ... }
img.onerror = (err) => { ... }
img.src = url
```

### 5.3 常见 Canvas 错误

**错误**: `Cannot read property 'width' of undefined`
**原因**: Canvas 节点未正确获取
**解决**: 确保在 `onReady` 后获取 Canvas 节点

**错误**: `ctx.beginPath is not a function`
**原因**: 使用了错误的 Context 类型
**解决**: 确保使用 `canvas.getContext('2d')` 而非 `uni.createCanvasContext()`

---

## 6. 弹窗交互流程

### 6.1 水印模板选择流程

```
用户点击水印模板按钮
  ↓
打开 markList 弹窗
  ↓
显示预览水印（使用模拟数据）
  ↓
用户选择水印模板
  ↓
更新配置（useWatermarkConfig）
  ↓
关闭弹窗
  ↓
主水印重新渲染（使用新配置）
```

### 6.2 水印设置流程

```
用户点击主水印/设置按钮
  ↓
打开 waterSettingPanel 弹窗
  ↓
加载当前水印配置
  ↓
用户修改设置
  ↓
点击确定
  ↓
更新配置
  ↓
关闭弹窗
  ↓
主水印重新渲染
```

### 6.3 常见交互错误

**错误**: 打开设置面板时，主水印和预览水印重叠
**原因**: 没有隐藏主水印
**解决**: 
```vue
<WatermarkRenderer 
  v-if="!templateListDialogShow && !showSettingsPanel" 
  ref="waterMarkObj" 
  ... 
/>
```

**错误**: 关闭弹窗后水印未更新
**原因**: 没有触发重新渲染
**解决**: 使用 `refreshKey` 强制更新

---

## 7. 配置管理

### 7.1 水印配置结构

```typescript
interface WatermarkConfig {
  name: string           // 水印名称
  list: WatermarkFieldConfig[]  // 字段列表
  accentColor?: string   // 强调色
  theme?: string         // 主题
}
```

### 7.2 配置持久化

使用 `useWatermarkConfig` composable 管理配置：

```typescript
import { 
  queryWaterMarkName, 
  queryWaterMarkConfigure,
  updateWaterMarkName,
  updateWaterMarkConfigure 
} from './composables/useWatermarkConfig'

// 获取当前水印名称
const currentName = queryWaterMarkName()

// 获取水印配置
const config = queryWaterMarkConfigure(name)

// 更新水印名称
updateWaterMarkName(newName)

// 更新水印配置
updateWaterMarkConfigure(name, newConfig)
```

---

## 8. 小程序编译注意事项

### 8.1 路径问题

- 使用 `@/` 别名而非相对路径
- 静态资源使用 `require()` 或绝对路径

### 8.2 条件编译

```vue
<!-- #ifdef MP-WEIXIN -->
<!-- 微信小程序特有代码 -->
<!-- #endif -->

<!-- #ifndef MP-WEIXIN -->
<!-- 非微信小程序代码 -->
<!-- #endif -->
```

### 8.3 常见编译错误

**错误**: `module 'pages_camera/...' is not defined`
**原因**: 路径错误或文件不存在
**解决**: 检查文件路径和导入语句

**错误**: `WXSS 文件编译错误`
**原因**: 样式语法错误或不支持的特性
**解决**: 检查 WXSS 兼容性

---

## 9. 开发检查清单

在修改水印相机模块时，请检查：

- [ ] 是否正确使用了双水印系统（主水印 vs 预览水印）
- [ ] 水印位置计算是否正确（边界检查）
- [ ] 是否添加了 `defineOptions` 样式隔离
- [ ] Canvas API 是否兼容小程序
- [ ] 弹窗交互是否正确（显示/隐藏主水印）
- [ ] 配置更新是否触发重新渲染
- [ ] 是否处理了小程序编译错误

---

## 10. 常见问题速查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 水印位置变成居中 | 重置了 touchX/touchY | 保持原有位置值 |
| 水印列表和实际不一致 | 使用了不同的渲染逻辑 | 共享相同的 WatermarkRenderer |
| 样式穿透 | 缺少 defineOptions | 添加 styleIsolation: 'shared' |
| Canvas 渲染失败 | API 不兼容 | 使用小程序 Canvas 2D API |
| 弹窗关闭后水印未更新 | 未触发重新渲染 | 使用 refreshKey |
| 编译报错 | 路径或语法错误 | 检查小程序兼容性 |
