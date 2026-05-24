# JQL 数据库操作 (Javascript Query Language)

## 简介

JQL（Javascript Query Language）是 uniCloud 提供的 JS 方式操作数据库的规范。

- 比 SQL 和传统 MongoDB API 更清晰易学
- 支持强大的 DB Schema 权限控制
- 利用 JSON 嵌套特性简化联表查询和树查询

### 使用场景

| 场景 | 权限校验 | 数据校验 | 触发器 | 说明 |
|------|---------|---------|--------|------|
| 客户端 clientDB | ✅ 完整 | ✅ | ✅ | 依赖 uni-id |
| HBuilderX JQL 管理器 | ❌ 跳过（管理员身份） | ✅ | ❌ | 可读写 password 类型 |
| 云函数 JQL 扩展 | ✅（可用 setUser 指定身份） | ✅ | ✅ | password 类型可配置权限 |

### JQL 限制

- 不可 JSON 序列化的参数不支持（Date、RegExp 除外）
- **禁止使用 `set` 方法**
- **禁止使用更新操作符**（`db.command.inc` 等）
- 更新数据键值不可用 `{'a.b.c': 1}` 形式，需写成 `{a: {b: {c: 1}}}`

## 云端环境变量

在 JQL 语句中可使用以下变量：

| 变量 | 说明 |
|------|------|
| `$cloudEnv_uid` | 当前用户 uid（依赖 uni-id） |
| `$cloudEnv_now` | 服务器时间戳 |
| `$cloudEnv_clientIP` | 当前客户端 IP |

```js
// 在字符串内使用
const res = await db.collection('todos')
  .where('uid == $cloudEnv_uid')
  .get()

// 在对象内使用
const res = await db.collection('todos')
  .where({ uid: '$cloudEnv_uid' })
  .get()
```

> 这些变量并非直接获取值，而是生成标记，云端执行时再替换为实际值。

## 查询数据

### 基本查询

```js
const db = uniCloud.databaseForJQL()

// 查询所有
const res = await db.collection('todos').get()
console.log(res.data)       // 结果数组
console.log(res.affectedDocs) // 返回条数

// 条件查询
const res = await db.collection('todos')
  .where({ done: false })
  .get()

// 只查一条
const res = await db.collection('todos')
  .where({ done: false })
  .orderBy('createTime', 'desc')
  .get({ getOne: true })
```

### 方法调用顺序

单表查询必须按以下顺序：

```
collection → where → field → orderBy → skip → limit → get/getOne/count
```

### where — 查询条件

#### 简单查询条件

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `==` | 等于 | `where('name == "abc"')` |
| `!=` | 不等于 | `where('name != "abc"')` |
| `>` | 大于 | `where('age > 10')` |
| `>=` | 大于等于 | `where('age >= 10')` |
| `<` | 小于 | `where('age < 10')` |
| `<=` | 小于等于 | `where('age <= 10')` |
| `in` | 在数组中 | `where("status in ['a','b']")` |
| `!(xx in [])` | 不在数组中 | `where("!(status in ['a','b'])")` |
| `&&` | 与 | `where('uid == auth.uid && age > 10')` |
| `\|\|` | 或 | `where('uid == auth.uid \|\| age > 10')` |
| `test` | 正则匹配 | `where('/abc/.test(content)')` |

```js
// 简单条件
const res = await db.collection('todos')
  .where('done == false && priority == "high"')
  .get()

// 正则查询（类似 SQL LIKE）
const res = await db.collection('todos')
  .where('/关键词/.test(title)')
  .get()

// 忽略大小写
const res = await db.collection('users')
  .where('/admin/i.test(name)')
  .get()
```

> 简单查询条件中二元运算符两侧不可均为数据库字段。

#### 复杂查询条件

> HBuilderX 3.1.0+ 支持

可使用数据库运算方法，且可比较两个数据库字段：

```js
// 使用数据库运算方法
const res = await db.collection('score')
  .where('add(chinese, math) > 150')
  .get()

// 比较两个字段
const res = await db.collection('score')
  .where('math > chinese')
  .get()

// 使用日期
const res = await db.collection('todos')
  .where('deadline < $cloudEnv_now')
  .get()
```

> 复杂查询条件内不可使用正则查询。

### 查询数组字段

```js
// 数据库记录: { students: ['wang', 'li', 'zhang'] }
const res = await db.collection('class')
  .where('students == "wang"')  // 查询 students 包含 wang 的记录
  .get()
```

### field — 字段过滤

```js
// 字符串写法
const res = await db.collection('book')
  .field('title, author')
  .get()
// 返回 _id, title, author

// 对象写法
const res = await db.collection('book')
  .field({ title: true, author: true })
  .get()

// 嵌套字段过滤
const res = await db.collection('book')
  .field('price.vip')
  .get()
```

### 字段别名 (as)

```js
const res = await db.collection('book')
  .field('title as book_title, author as book_author')
  .get()
// 返回: { book_title: '...', book_author: '...' }

// _id 设置别名会同时返回 _id 和别名字段
const res = await db.collection('book')
  .field('_id as book_id, title')
  .get()
// 返回: { _id: '...', book_id: '...', title: '...' }
```

> `as` 后的别名不可与 schema 中已有字段重名。

### 字段运算

```js
// 使用数据库运算方法计算字段
const res = await db.collection('class')
  .field('grade, class, add(chinese, math) as totalScore')
  .get()
```

### orderBy — 排序

```js
// 单字段
.orderBy('createTime', 'desc')

// 多字段（前面优先级高）
.orderBy('grade asc, score desc')

// 默认升序
.orderBy('name')
```

### limit — 限制条数

```js
.limit(20)  // 默认 100，最大 1000
```

### skip — 跳过

```js
.skip(20)
```

### 分页

```js
const pageSize = 20
const page = 2
const res = await db.collection('todos')
  .skip((page - 1) * pageSize)
  .limit(pageSize)
  .get()
```

> `<unicloud-db>` 组件提供更简便的分页：`append` 模式（滚动加载）和 `replace` 模式（页码切换）。

### getOne — 只查一条

```js
const res = await db.collection('todos')
  .orderBy('createTime', 'desc')
  .get({ getOne: true })
// res.data 为单个对象而非数组
```

### count — 统计数量

```js
// 纯统计数量
const res = await db.collection('todos')
  .where({ done: false })
  .count()
console.log(res.total)

// 查询同时返回总数
const res = await db.collection('todos')
  .get({ getCount: true })
console.log(res.total)       // 符合条件的总数
console.log(res.affectedDocs) // 实际返回条数
```

### distinct — 去重

```js
const res = await db.collection('score')
  .field('grade, class')
  .distinct()
  .get()
// 返回去重后的班级列表
```

> `field` 中不可包含 `_id`，否则无法去重。

### getTree — 查询树形数据

> HBuilderX 3.0.3+ 支持

前提：在 DB Schema 中配置 `parentKey` 表达父子关系。

```json
// department 表 schema 片段
{
  "parent_id": {
    "parentKey": "_id"
  }
}
```

```js
// 查询所有子节点（从根节点开始）
const res = await db.collection('department')
  .get({
    getTree: {
      limitLevel: 10,  // 最大层级 1-15，默认 10
      startWith: 'parent_id == null || parent_id == ""'  // 根节点条件
    }
  })
// 返回树形结构，子节点在 children 字段下

// 从指定节点开始查询
const res = await db.collection('department')
  .get({
    getTree: {
      startWith: 'name == "总部"',
      limitLevel: 3
    }
  })

// 带 where 条件（对所有层级生效）
const res = await db.collection('department')
  .where('status == 0')
  .get({
    getTree: {
      startWith: '_id == "1"'
    }
  })
```

### getTreePath — 查询父节点路径

```js
const res = await db.collection('department')
  .get({
    getTreePath: {
      startWith: 'name == "一级部门A"',
      limitLevel: 10
    }
  })
// 返回从根节点到 "一级部门A" 的路径
```

### geoNear — 地理位置查询

> HBuilderX 3.6.10+ 支持

```js
const db = uniCloud.databaseForJQL()
const Geo = db.Geo

const res = await db.collection('shops')
  .geoNear({
    near: new Geo.Point(116.4, 39.9),
    spherical: true,
    maxDistance: 1000,  // 最大距离（米）
    minDistance: 0,
    distanceField: 'distance',
    query: 'status == 1'  // 额外条件
  })
  .get()
```

## 联表查询

JQL 提供了比 SQL JOIN 更简单的联表方案：在 DB Schema 中配置 `foreignKey` 关联字段，即可将多个表当虚拟联表直接查询。

### 虚拟联表（直接联查）

```js
// 前提：order 表的 book_id 字段配置了 foreignKey 指向 book 表的 _id
const res = await db.collection('order', 'book')
  .where('book_id.title == "三国演义"')
  .get()
// book 信息嵌入到 order 的 book_id 字段下
```

### 临时表联查（性能更好）

> HBuilderX 3.2.6+ 支持

先对主表/副表过滤，再生成虚拟联表，数据量大时性能更优。

```js
// 先过滤主表
const order = db.collection('order')
  .where('uid == $cloudEnv_uid')
  .getTemp()

// 再过滤副表
const book = db.collection('book')
  .field('_id, title, author')
  .getTemp()

// 联表查询
const res = await db.collection(order, book)
  .where('book_id.title == "三国演义"')
  .get()
```

#### 临时表内可用方法

```
collection → where → field → orderBy → skip → limit → getTemp
```

#### 虚拟联表可用方法

```
collection(临时表1, 临时表2) → foreignKey → where → field → orderBy → skip → limit → get/getOne/count
```

### 联表字段过滤与别名

```js
// 过滤副表字段
const res = await db.collection(order, book)
  .field('quantity, book_id.title, book_id.author')
  .get()

// 字段别名
const res = await db.collection(order, book)
  .field('quantity as order_quantity, book_id.title as book_title, book_id.author as book_author')
  .get()
```

### 副表 foreignKey 联查

> 2021年4月28日后支持

副表的数据以数组方式嵌入到主表中：

```js
// comment 表的 article 字段 foreignKey 指向 article 表
const res = await db.collection('article', 'comment')
  .get()
// 副表 comment 以数组嵌入主表 article
```

### 手动指定 foreignKey

```js
const res = await db.collection('table_a', 'table_b')
  .foreignKey('field_a')  // 指定使用哪个 foreignKey
  .get()
```

### in 查询匹配另一表字段

> HBuilderX 3.7.12+ 支持

```js
const companyFilter = db.collection('company')
  .where('level == 1')
  .field('_id')
  .getTemp()

const res = await db.collection('user')
  .where('company_id in ${companyFilter}')
  .get()
```

## 新增数据

```js
// 单条
const res = await db.collection('todos').add({
  title: '学习 JQL',
  done: false
})
console.log(res.id)  // 新记录的 _id

// 批量
const res = await db.collection('todos').add([
  { title: '任务1', done: false },
  { title: '任务2', done: true }
])
console.log(res.inserted)  // 2
console.log(res.ids)       // ['xxx', 'yyy']
```

## 删除数据

```js
// 按 ID 删除
await db.collection('todos').doc('doc-id').remove()

// 条件删除
const res = await db.collection('todos')
  .where('done == true')
  .remove()
console.log(res.deleted)  // 删除条数
```

## 更新数据

```js
// 按 ID 更新
await db.collection('todos').doc('doc-id').update({
  done: true
})

// 条件批量更新
const res = await db.collection('todos')
  .where('done == false')
  .update({ priority: 'high' })
console.log(res.updated)  // 更新条数
```

### 更新操作符（JQL 管理器专用）

> HBuilderX 3.5.1+ 支持，仅 JQL 数据库管理器可用

```js
// 重命名字段
db.command.rename('old_field', 'new_field')

// 删除字段
db.command.remove('field_name')
```

> 使用更新操作符会跳过所有数据校验。

## 分组统计 (groupBy)

> HBuilderX 3.1.0+ 支持

```js
// 按班级统计总分
const res = await db.collection('score')
  .groupBy('class')
  .groupField('sum(score) as totalScore')
  .get()

// 按班级统计平均分
const res = await db.collection('score')
  .groupBy('class')
  .groupField('avg(score) as avgScore')
  .get()

// 按班级统计人数
const res = await db.collection('score')
  .groupBy('class')
  .groupField('count(*) as studentCount')
  .get()
```

### 常用累积器

| 方法 | 说明 |
|------|------|
| `count(*)` | 计数（固定写法） |
| `sum(字段)` | 求和 |
| `avg(字段)` | 求均值 |

### 按日分组统计

```js
// 统计每日新增用户
const res = await db.collection('uni-id-users')
  .groupBy('dateToString(add(new Date(0), register_date), "%Y-%m-%d", "+0800") as date')
  .groupField('count(*) as dailyCount')
  .get()
```

### groupBy 前使用 field

```js
// field 用于预处理数据，传给 groupBy 和 groupField
const res = await db.collection('score')
  .field('grade, class, add(chinese, math) as totalScore')
  .groupBy('grade, class')
  .groupField('avg(totalScore) as avgTotal')
  .get()
```

> `groupField` 返回结果不默认包含 `_id`。`count(*)` 是固定写法。

## 多请求合并 (multiSend)

> HBuilderX 3.1.22+ 支持

将多个数据库请求合并为一个网络请求：

```js
const [res1, res2, res3] = await db.multiSend(
  db.collection('banners').where('status == 1').get(),
  db.collection('notices').orderBy('createTime', 'desc').limit(5).get(),
  db.collection('goods').where('isHot == true').limit(10).get()
)
```

## 事务操作

> HBuilderX 4.81+ 支持

```js
const transaction = await db.startTransaction()
try {
  await transaction.collection('accounts').doc('a-id').update({
    balance: db.command.inc(-100)
  })
  await transaction.collection('accounts').doc('b-id').update({
    balance: db.command.inc(100)
  })
  await transaction.commit()
} catch (e) {
  await transaction.rollback()
}
```

> JQL 事务不支持 `doc.set`、`where.updateAndReturn`。`update` 不支持使用更新操作符。

## MongoDB 聚合操作

```js
// 随机取 20 条数据
const res = await db.collection('todos')
  .aggregate()
  .match({ status: 1 })
  .sample({ size: 20 })
  .end()
```

## 返回值结构

### 查询

```js
{
  errCode: 0,
  data: [...],           // 结果数组（getOne 时为单个对象）
  affectedDocs: 10,      // 返回条数
  total: 100             // 仅 getCount: true 时有
}
```

### 新增

```js
// 单条
{ errCode: 0, id: 'xxx' }
// 批量
{ errCode: 0, inserted: 3, ids: ['a', 'b', 'c'] }
```

### 更新

```js
{ errCode: 0, updated: 5 }
```

### 删除

```js
{ errCode: 0, deleted: 3 }
```

### 错误码

| errCode | 说明 |
|---------|------|
| `TOKEN_INVALID_INVALID_CLIENTID` | 设备特征校验未通过 |
| `TOKEN_INVALID` | 云端不包含此 token |
| `TOKEN_INVALID_TOKEN_EXPIRED` | token 已过期 |
| `TOKEN_INVALID_WRONG_TOKEN` | token 校验未通过 |
| `TOKEN_INVALID_ANONYMOUS_USER` | 匿名用户 |
| `SYNTAX_ERROR` | 语法错误 |
| `PERMISSION_ERROR` | 权限校验未通过 |
| `VALIDATION_ERROR` | 数据格式未通过 |
| `DUPLICATE_KEY` | 索引冲突 |
| `SYSTEM_ERROR` | 系统错误 |

## DB Schema 配置要点

JQL 强依赖 DB Schema，核心配置包括：

- **permission** — 数据操作权限（读/写/删/增），支持角色控制
- **foreignKey** — 字段关联映射，用于联表查询
- **parentKey** — 父子关系，用于树形查询
- **validator** — 字段值域校验规则
- **defaultValue / forceDefaultValue** — 默认值

> 详见 [DB Schema 文档](db-schema.md) / [官方文档](https://doc.dcloud.net.cn/uniCloud/schema.html)

## action 云函数（已不推荐）

> HBuilderX 3.6.11 起推荐使用[数据库触发器](https://doc.dcloud.net.cn/uniCloud/jql-schema-ext.html)替代

```js
// 在 JQL 中使用 action
const res = await db.action('my-action')
  .collection('todos')
  .where('done == false')
  .get()
```

action 文件存放在 `uni-clientDB-actions` 目录下，包含 `before` 和 `after`：
- **before** — 数据库操作前执行（数据二次处理、开启事务、参数校验）
- **after** — 数据库操作后执行（返回值处理、错误回滚、二次操作如阅读数+1）
