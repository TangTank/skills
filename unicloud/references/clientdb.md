# ClientDB

> 自 HBuilderX 2.9.5 起支持

## 简介

ClientDB 允许在前端直接操作云数据库。通过 DB Schema 配置权限和字段校验规则，解决前端操作数据库的安全问题。

**核心优势：不用写服务器代码！**

## 前提条件

- 依赖 `uni-id`（1.1.10+）提供身份和权限校验
- 存在 `uni-id-common` 时优先使用
- 需在 **DB Schema** 中配置权限和校验规则 → [DB Schema 参考](db-schema.md)

## 两种 API

| API | 说明 |
|-----|------|
| `uniCloud.database()` | 传统 nosql 查询语法 |
| `uniCloud.databaseForJQL()` | JQL 查询语法（推荐） |

> **强烈推荐** 使用 `databaseForJQL`，返回结构与云端 JQL 扩展库一致，方便代码复用。

## JQL 与 ClientDB 的关系

ClientDB 是前端直接操作数据库的能力，JQL 是其底层的查询语言。

```
ClientDB（前端能力）
├── JS API: uniCloud.databaseForJQL() + JQL 语法
├── 组件: <unicloud-db> 组件
└── 底层依赖: DB Schema（权限 + 字段校验 + foreignKey）
```

- JQL 详细语法请参考 → [JQL 数据库操作](references/jql.md)
- 本文档聚焦 ClientDB 特有的前端能力

## 前端使用示例

```js
// 使用 JQL 语法（推荐）
const db = uniCloud.databaseForJQL()
const res = await db.collection('todos')
  .where('done == false')
  .orderBy('createTime desc')
  .get()
console.log(res.data)
```

```js
// 使用传统 nosql 语法
const db = uniCloud.database()
const res = await db.collection('todos')
  .where({ name: 'hello-uni-app' })
  .get()
// res 结构多一层 result
console.log(res.result.data)
```

## 两种获取引用方式对比

| 对比项 | `database()` | `databaseForJQL()` |
|--------|-------------|-------------------|
| 返回结构 | `res.result.data` | `res.data` |
| 拦截器接口名 | `database` | `databaseForJQL` |
| 推荐度 | — | ✅ 推荐 |

## 前端限制

与云函数操作数据库语法一致，但有以下限制：

- 不可序列化参数类型不支持（如 `undefined`，Date 和 RegExp 除外）
- **禁止前端使用 `set` 方法**
- **禁止使用更新操作符**（`db.command.inc` 等）
- 更新数据键值不可用 `{'a.b.c': 1}` 形式，需写成 `{a: {b: {c: 1}}}`

## 客户端事件

### 刷新 token

```js
// HBuilderX 3.2.11+，自动管理
// token 及过期时间自动保存在 storage
```

### 错误处理

```js
uniCloud.databaseForJQL().on('error', (err) => {
  console.error('ClientDB error:', err)
})
```

## <unicloud-db> 组件

HBuilderX 3.0+ 内置，是 JS API 的再封装，进一步简化代码。

### 基础用法

```html
<template>
  <unicloud-db
    ref="udb"
    collection="todos"
    where="done == false"
    orderby="createTime desc"
    v-slot="{ data, loading, error }"
  >
    <view v-for="item in data" :key="item._id">
      {{ item.title }}
    </view>
  </unicloud-db>
</template>
```

### 分页

```html
<!-- append 模式：滚动到底加载下一页 -->
<unicloud-db
  collection="todos"
  :page-size="20"
  page-data="append"
  v-slot="{ data, loading, hasMore, loadMore }"
>
  <view v-for="item in data" :key="item._id">{{ item.title }}</view>
  <view v-if="hasMore" @click="loadMore">加载更多</view>
</unicloud-db>

<!-- replace 模式：页码切换 -->
<unicloud-db
  collection="todos"
  :page-size="20"
  page-data="replace"
  :page-current="currentPage"
  v-slot="{ data, loading }"
>
  <view v-for="item in data" :key="item._id">{{ item.title }}</view>
</unicloud-db>
```

### 联表查询

```html
<unicloud-db
  collection="order, book"
  where='book_id.title == "三国演义"'
  v-slot="{ data }"
>
  <view v-for="item in data" :key="item._id">
    {{ item.book_id.title }} x {{ item.quantity }}
  </view>
</unicloud-db>
```

### 树形查询

```html
<unicloud-db
  collection="department"
  :gettree="{
    limitLevel: 10,
    startWith: 'parent_id == null || parent_id == \"\"'
  }"
  v-slot="{ data }"
>
  <!-- data 为树形结构 -->
</unicloud-db>
```

### 组件常用属性

| 属性 | 说明 |
|------|------|
| `collection` | 表名（联表用逗号分隔） |
| `where` | 查询条件（JQL 语法） |
| `field` | 返回字段 |
| `orderby` | 排序 |
| `page-size` | 每页条数 |
| `page-current` | 当前页码 |
| `page-data` | `append` / `replace` |
| `getone` | 只查一条 |
| `getcount` | 返回总数 |
| `gettree` | 树形查询参数 |
| `action` | 指定 action 云函数 |

### JS 操作

```js
// 重新加载数据
this.$refs.udb.loadData()

// 添加数据
this.$refs.udb.add({ title: '新任务', done: false })

// 删除数据
this.$refs.udb.remove('doc-id')
```

## JQL 语法速查

| 能力 | 示例 |
|------|------|
| 条件查询 | `.where('age > 18 && status == "active"')` |
| 正则搜索 | `.where('/关键词/.test(title)')` |
| 字段过滤 | `.field('title, author')` |
| 字段别名 | `.field('title as book_title')` |
| 联表查询 | `.collection('order', 'book')` |
| 树形查询 | `.get({ getTree: { limitLevel: 5 } })` |
| 统计数量 | `.count()` 或 `.get({ getCount: true })` |
| 分组统计 | `.groupBy('class').groupField('count(*) as total')` |
| 地理位置 | `.geoNear({ near: point, maxDistance: 1000 })` |
| 去重 | `.field('category').distinct()` |

> 完整 JQL 语法参考 → [JQL 数据库操作](references/jql.md)
