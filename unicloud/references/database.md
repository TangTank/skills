# 云数据库操作 (Cloud Database)

## 简介

云函数中支持对云数据库的全部功能操作。本文档介绍在云函数内通过传统 API 操作数据库的方式。

> 如需使用 JQL 语法操作数据库，请参考 [JQL 扩展库](https://doc.dcloud.net.cn/uniCloud/jql-cloud.html)

## 获取数据库实例

```js
// 获取当前服务空间数据库
const db = uniCloud.database()

// 获取其他服务空间数据库（HBuilderX 3.2.11+）
const otherDb = uniCloud.database({
  provider: 'aliyun',
  spaceId: 'your-space-id',
  clientSecret: 'your-secret'  // 仅阿里云需要
})
```

## 数据类型

| 类型 | 说明 |
|------|------|
| `string` | 字符串 |
| `password` | 特殊 string，clientDB 完全不可读写（即使 admin） |
| `number` | 数字（Schema 中细化为 int / double） |
| `bool` | 布尔值 |
| `date` | 日期 |
| `timestamp` | 时间戳（毫秒数字，推荐使用以屏蔽时区差异） |
| `object` | JSON 对象 |
| `file` | 特殊 object，云存储文件信息体 |
| `array` | 数组 |
| `null` | 空值占位符 |
| `GeoPoint` | 地理位置点 |
| `GeoLineString` | 地理路径 |
| `GeoPolygon` | 地理多边形 |
| `GeoMultiPoint` | 多个地理位置点 |
| `GeoMultiLineString` | 多个地理路径 |
| `GeoMultiPolygon` | 多个地理多边形 |

### Date 类型

```js
// 客户端当前时间（连接本地云函数时）
const clientDate = new Date()

// 服务端当前时间（仅腾讯云）
const serverDate = new uniCloud.database().serverDate()
// 偏移 1 小时
const laterDate = new uniCloud.database().serverDate({ offset: 3600000 })
```

> 推荐使用 `timestamp`（数字）存储时间，前端用组件格式化渲染，可屏蔽时区差异。金额建议用 `int` 以分为单位，避免 `double` 精度问题。

### 获取其他服务空间数据库实例

```js
const otherDb = uniCloud.database({
  provider: 'tencent',    // aliyun | tencent
  spaceId: 'xxx',
  clientSecret: 'xxx'     // 仅阿里云
})
```

> 云函数环境仅支付宝云与腾讯云支持。客户端环境三家均支持。

## 创建表

- **Web 控制台**：云数据库 → 创建（支持 opendb 模板）
- **HBuilderX**：`database` 目录右键 → 新建 schema → 上传时创建
- **代码方式**（不推荐）：
  - 阿里云：调用 `add` 方法时自动创建
  - 腾讯云/支付宝云：`createCollection` 方法

> 代码创建的表没有索引和 Schema，不推荐。

## 获取集合引用

```js
const db = uniCloud.database()
const collection = db.collection('todos')
```

### 集合 Collection 操作

| 类型 | 接口 | 说明 |
|------|------|------|
| 写 | `add` | 新增记录 |
| 计数 | `count` | 获取符合条件的记录条数 |
| 读 | `get` | 获取记录 |
| 引用 | `doc` | 获取指定 ID 记录的引用 |
| 查询条件 | `where` | 筛选匹配记录 |
| — | `skip` | 跳过指定数量文档（分页） |
| — | `orderBy` | 排序方式 |
| — | `limit` | 返回结果数量限制（默认 100，最大 1000） |
| — | `field` | 指定返回字段 |

### 记录 Record 操作

```js
const record = db.collection('todos').doc('doc-id')
```

| 接口 | 说明 |
|------|------|
| `update` | 局部更新（只更新传入字段） |
| `set` | 覆写（删除所有字段，创建传入字段） |
| `remove` | 删除记录 |
| `get` | 获取记录 |

## 新增文档

### 方式一：collection.add()

```js
// 单条
const res = await db.collection('todos').add({
  title: '学习 uniCloud',
  done: false
})
// res: { id: 'xxx' }

// 批量
const res = await db.collection('todos').add([
  { title: '任务1', done: false },
  { title: '任务2', done: true }
])
// res: { ids: ['xxx', 'yyy'] }
```

### 方式二：collection.doc().set()

```js
const res = await db.collection('todos').doc('doc-id').set({
  title: '新标题',
  done: true
})
// res: { updated: 1, upsertedId: 'xxx' }
```

> `set` 会覆写已有字段。如原记录有 `follow` 字段，`set` 时未传入则该字段会被删除。

## 查询文档

```js
const db = uniCloud.database()
const res = await db.collection('todos')
  .where({ done: false })
  .orderBy('createTime', 'desc')
  .skip(0)
  .limit(20)
  .field({ title: true, done: true, _id: true })
  .get()

console.log(res.data) // 查询结果数组
```

### where — 添加查询条件

```js
// 简单匹配
.where({ type: 'computer', memory: '8g' })

// 使用查询指令
const dbCmd = db.command
.where({
  memory: dbCmd.gt('4g'),
  price: dbCmd.lt(6000)
})

// 正则表达式
.where({
  name: db.RegExp({ regexp: '^ABC', options: 'i' })
})
```

### count — 获取数量

```js
const res = await db.collection('todos').where({ done: false }).count()
console.log(res.total)
```

### limit — 限制数量

```js
.limit(20)  // 默认 100，最大 1000
```

### skip — 跳过记录（分页）

```js
.skip(20)  // 跳过前 20 条
```

> 数据量大时 skip 性能差，建议使用其他分页方案。

### orderBy — 排序

```js
.orderBy('createTime', 'desc')  // 降序
.orderBy('price', 'asc')        // 升序

// 多字段排序
.orderBy('name', 'asc').orderBy('_id', 'asc')
```

### field — 指定返回字段

```js
.field({ title: true, content: true, _id: true })
// 不可混用 true/false
```

## 查询指令

挂载在 `db.command`（简写 `dbCmd`）下。

### 比较运算

| 指令 | 说明 | 示例 |
|------|------|------|
| `eq` | 等于 | `dbCmd.eq('8g')` |
| `neq` | 不等于 | `dbCmd.neq('X')` |
| `gt` | 大于 | `dbCmd.gt(3000)` |
| `gte` | 大于等于 | `dbCmd.gte(3000)` |
| `lt` | 小于 | `dbCmd.lt(6000)` |
| `lte` | 小于等于 | `dbCmd.lte(6000)` |
| `in` | 在数组中 | `dbCmd.in(['8g', '16g'])` |
| `nin` | 不在数组中 | `dbCmd.nin(['8g', '16g'])` |

### 逻辑运算

```js
// and — 且
.where({
  price: dbCmd.gt(4000).and(dbCmd.lt(8000))
})

// or — 或
.where({
  price: dbCmd.lt(4000).or(dbCmd.gt(6000))
})

// 跨字段 or
const _ = db.command
.where(_.or([
  { memory: '8g' },
  { cpu: '3.2ghz' }
]))
```

## 删除文档

```js
// 按 ID 删除
await db.collection('todos').doc('doc-id').remove()

// 条件批量删除
await db.collection('todos').where({ done: true }).remove()
// 返回 { deleted: 3 }
```

## 更新文档

### 局部更新

```js
await db.collection('todos').doc('doc-id').update({
  done: true
})
// 返回 { updated: 1 }
```

### 覆写更新（不存在则创建）

```js
await db.collection('todos').doc('doc-id').set({
  title: '新标题'
})
```

### 批量更新

```js
await db.collection('todos').where({ done: false }).update({
  priority: 'high'
})
```

### 更新并返回

```js
const res = await db.collection('todos').where({ done: false }).updateAndReturn({
  done: true
})
// res: { updated: 1, doc: {...} }
```

## 更新指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `set` | 设置字段值 | `dbCmd.set({ a: 1 })` |
| `remove` | 删除字段 | `dbCmd.remove()` |
| `inc` | 原子自增 | `dbCmd.inc(1)` |
| `mul` | 原子自乘 | `dbCmd.mul(10)` |
| `push` | 数组追加尾元素 | `dbCmd.push('item')` |
| `pop` | 数组删除尾元素 | `dbCmd.pop()` |
| `shift` | 数组删除头元素 | `dbCmd.shift()` |
| `unshift` | 数组追加头元素 | `dbCmd.unshift('item')` |

```js
// 阅读数 +1
await db.collection('articles').doc('id').update({
  readCount: dbCmd.inc(1)
})

// 删除字段
await db.collection('articles').doc('id').update({
  score: dbCmd.remove()
})

// 数组追加
await db.collection('articles').doc('id').update({
  tags: dbCmd.push('新标签')
})
```

## GEO 地理位置

### 数据类型

```js
const db = uniCloud.database()
const _ = db.command
const Geo = db.Geo

// Point — 地理位置点
const point = new Geo.Point(116.4, 39.9)

// LineString — 地理路径
const line = new Geo.LineString([
  new Geo.Point(116.4, 39.9),
  new Geo.Point(117.4, 40.9)
])

// Polygon — 地理多边形
const polygon = new Geo.Polygon([
  new Geo.LineString([
    new Geo.Point(0, 0),
    new Geo.Point(1, 0),
    new Geo.Point(1, 1),
    new Geo.Point(0, 1),
    new Geo.Point(0, 0)
  ])
])
```

### GEO 查询

```js
// 按距离排序
.where({
  location: _.geoNear({
    geometry: new Geo.Point(116.4, 39.9),
    maxDistance: 1000,  // 最大距离（米）
    minDistance: 0
  })
})

// 在多边形内
.where({
  location: _.geoWithin({
    geometry: polygon
  })
})
```

> 注意：对地理位置字段进行搜索，必须建立**地理位置索引**。

## 事务

事务用于在某个数据库操作失败后进行回滚。时间限制：从事务开始到提交/回滚不可超过 **10 秒**。

### runTransaction

```js
// 阿里云不支持此用法，请用 startTransaction
const res = await db.runTransaction(async (transaction) => {
  const coll = transaction.collection('accounts')

  const accountA = await coll.doc('a-id').get()
  const accountB = await coll.doc('b-id').get()

  const balanceA = accountA.data[0].balance
  const balanceB = accountB.data[0].balance

  if (balanceA < 100) {
    await transaction.rollback('余额不足')
  }

  await coll.doc('a-id').update({ balance: balanceA - 100 })
  await coll.doc('b-id').update({ balance: balanceB + 100 })

  return '转账成功'
})
```

### startTransaction

```js
const transaction = await db.startTransaction()
try {
  await transaction.collection('accounts').doc('a-id').update({
    balance: transaction.command.inc(-100)
  })
  await transaction.collection('accounts').doc('b-id').update({
    balance: transaction.command.inc(100)
  })
  await transaction.commit()
} catch (e) {
  await transaction.rollback()
}
```

### 事务限制

- 只允许单记录操作，不允许批量操作
- 修改和删除仅支持 `doc` 方法（不支持 `where`）
- 新增时 `add` 一次只可新增单条
- 腾讯云无 `where` 限制，但使用 `where` 修改/删除多条会导致无法回滚
