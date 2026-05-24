# 数据库触发器 (Database Trigger)

> HBuilderX 3.6.11+ 支持，推荐替代 action 云函数

## 简介

数据库触发器用于在执行 JQL 数据库指令（增删改查）的同时触发相应的操作。

- 仅限 JQL 操作数据库（传统 MongoDB 写法不支持）
- 触发器在**数据校验、权限校验之后**执行
- 触发器在云端执行，clientDB 操作时也可触发

## 配置方式

在 `uniCloud/database/` 目录下创建 `${表名}.schema.ext.js`：

```js
// uniCloud/database/todos.schema.ext.js
module.exports = {
  trigger: {
    beforeRead: async (obj) => {
      // 读取前触发
    },
    afterRead: async (obj) => {
      // 读取后触发
    }
  }
}
```

## 触发时机

| 时机 | 说明 |
|------|------|
| `beforeRead` | 读取前 |
| `afterRead` | 读取后 |
| `beforeCount` | 计数前 |
| `afterCount` | 计数后 |
| `beforeCreate` | 新增前 |
| `afterCreate` | 新增后 |
| `beforeUpdate` | 更新前 |
| `afterUpdate` | 更新后 |
| `beforeDelete` | 删除前 |
| `afterDelete` | 删除后 |
| `beforeReadAsSecondaryCollection` | 集合作为副表被读取前（仅 getTemp 联表） |
| `afterReadAsSecondaryCollection` | 集合作为副表被读取后（仅 getTemp 联表） |

## 触发器入参

| 参数 | 类型 | 说明 |
|------|------|------|
| collection | string | 当前表名 |
| operation | string | 操作类型：`create`/`update`/`delete`/`read`/`count` |
| where | object | 查询条件（可直接传给 where 方法） |
| field | array | read 必备，访问的字段列表 |
| addDataList | array | create 必备，新增数据列表 |
| updateData | object | update 必备，更新数据 |
| clientInfo | object | 客户端信息 |
| userInfo | object | 用户信息 `{ uid, role, permission }` |
| result | object | afterXxx 内必备，本次操作结果 |
| triggerContext | object | before 和 after 间共享数据 |
| secondaryCollection | array | 联表查询副表列表 |
| rawWhere | object/string | 原始查询条件（未经转化） |
| docId | string | doc 方法的文档 _id |
| skip | number | 跳过记录条数 |
| limit | number | 返回条数限制 |
| transaction | Transaction | 事务查询时存在 |

### triggerContext — before/after 间共享数据

```js
module.exports = {
  trigger: {
    beforeCreate: async (obj) => {
      obj.triggerContext.customData = '从 before 传到 after'
    },
    afterCreate: async (obj) => {
      console.log(obj.triggerContext.customData) // '从 before 传到 after'
    }
  }
}
```

### isEqualToJql — 判断 JQL 语句

```js
module.exports = {
  trigger: {
    afterRead: async (obj) => {
      if (obj.isEqualToJql("db.collection('todos').get()")) {
        // 特定 JQL 语句的处理
      }
    }
  }
}
```

## 常见用例

### 修改更新时间

```js
module.exports = {
  trigger: {
    beforeUpdate: async ({ updateData }) => {
      updateData.update_time = Date.now()
    }
  }
}
```

### 阅读后阅读量 +1

```js
module.exports = {
  trigger: {
    afterRead: async ({ collection, where, dbJql }) => {
      await dbJql.collection(collection)
        .where(where)
        .update({ read_count: dbJql.command.inc(1) })
    }
  }
}
```

### 删除前备份

```js
module.exports = {
  trigger: {
    beforeDelete: async ({ where, collection, dbJql }) => {
      const data = await dbJql.collection(collection).where(where).get()
      await dbJql.collection('backup_' + collection).add(data.data)
    }
  }
}
```

### 新增时自动添加摘要

```js
module.exports = {
  trigger: {
    beforeCreate: async ({ addDataList }) => {
      for (const item of addDataList) {
        if (!item.summary && item.content) {
          item.summary = item.content.substring(0, 100)
        }
      }
    }
  }
}
```

## 在触发器内使用 JQL

```js
module.exports = {
  trigger: {
    afterRead: async (obj) => {
      const { dbJql, userInfo, where } = obj
      // 记录阅读日志
      if (userInfo.uid) {
        await dbJql.collection('read_log').add({
          user_id: userInfo.uid,
          article_id: where._id,
          read_time: Date.now()
        })
      }
    }
  }
}
```

### 避免死循环

触发器内使用 JQL 操作同一张表会再次触发触发器！使用 `skipTrigger` 跳过：

```js
module.exports = {
  trigger: {
    afterRead: async ({ dbJql, where }) => {
      // 跳过触发器，避免死循环
      const db = dbJql.databaseForJQL({ skipTrigger: true })
      await db.collection('read_count').where(where).update({
        count: db.command.inc(1)
      })
    }
  }
}
```

> `skipTrigger` 仅云端生效，客户端不生效。

## 在触发器内使用公共模块和扩展库

- clientDB 访问时：可使用包含在 clientDB 内的公共模块
- 云函数/云对象访问时：可使用云函数/云对象依赖的公共模块
- 内置依赖：`uni-id-common`、`uni-config-center`、`uni-cloud-redis`（如已开通）

在 `uniCloud/database` 目录右键可管理 schema 扩展依赖的公共模块和扩展库。

## 注意事项

- 非 getTemp 联表查询在触发器内获取的 where 为 null
- 联表查询时**只触发主表触发器**，不触发副表触发器
- JQL 缓存读取不触发读触发器
- HBuilderX JQL 管理器执行时不触发任何触发器
- 如果同时使用触发器和 action：触发器的 before 在所有 action 的 before 之前执行，after 在所有 action 的 after 之后执行

## 与 action 云函数对比

| 对比项 | 数据库触发器 | action 云函数 |
|--------|------------|--------------|
| 安全性 | ✅ 不会被前端指定 | ❌ 可被前端指定 |
| 查询语法 | ✅ 支持 JQL | ❌ 仅传统 MongoDB |
| 适用范围 | 常见场景均可覆盖 | 复杂场景 |
| 推荐度 | ✅ 推荐 | ⚠️ 不推荐新项目使用 |
