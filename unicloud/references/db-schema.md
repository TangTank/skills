# DB Schema 数据库表结构

## 简介

DB Schema 是基于 JSON 格式定义数据结构的规范。每张表/集合都有一个 `${表名}.schema.json` 文件来描述表和字段信息。

**核心作用：**
- 描述数据表结构（一目了然阅读每个表、字段的用途）
- 设定字段默认值（`defaultValue` / `forceDefaultValue`）
- 设定字段值域校验（`validator`）：类型、范围、正则、枚举等
- 设定字段间约束关系（`fieldRules`）
- 设定表间关联关系（`foreignKey`），支持自动联表查询
- 设定数据操作权限（`permission`）
- 根据 schema 自动生成前端界面（`schema2code`）

> **重要：** 只有通过 JQL 操作数据库时 DB Schema 才生效。传统 MongoDB API 不执行 Schema 校验。

## 编写方式

### 方式一：HBuilderX（推荐）

1. 项目右键 → 创建 `database` 目录
2. `database` 目录右键 → 新建数据集合 schema
3. 本地调试时 schema 直接生效，无需上传
4. 右键上传 / `Ctrl+U` 快捷上传

### 方式二：Web 控制台

登录 [uniCloud 控制台](https://unicloud.dcloud.net.cn) → 数据表 → 表结构 → 编辑

> Web 控制台保存后**实时在线上生效**，注意对商用项目的影响。

## Schema 结构

```json
{
  "bsonType": "object",
  "required": ["name", "tel"],
  "permission": {
    "read": true,
    "create": false,
    "update": "doc._id == auth.uid",
    "delete": false
  },
  "properties": {
    "_id": {
      "description": "ID，系统自动生成"
    },
    "name": {
      "bsonType": "string",
      "title": "姓名",
      "description": "用户姓名",
      "minLength": 2,
      "maxLength": 17,
      "trim": "both",
      "permission": {
        "read": true,
        "write": "doc._id == auth.uid"
      }
    }
  },
  "fieldRules": [
    {
      "rule": "end_date > create_date",
      "errorMessage": "结束时间需大于开始时间"
    }
  ]
}
```

## 一级节点

| 属性 | 类型 | 说明 |
|------|------|------|
| bsonType | string | 固定为 `"object"` |
| required | array | 必填字段列表 |
| permission | object | 表级权限控制 |
| properties | object | 字段定义 |
| fieldRules | array | 字段间校验规则 |

## 字段属性

### 基本属性

| 属性 | 类型 | 说明 |
|------|------|------|
| bsonType | any | 字段类型（见下方类型表） |
| arrayType | string | 数组项类型（`bsonType="array"` 时有效） |
| title | string | 标题（schema2code 生成表单 label） |
| description | string | 描述（schema2code 生成 input placeholder） |
| defaultValue | string/Object | 默认值（客户端可覆盖） |
| forceDefaultValue | string/Object | 强制默认值（客户端不可覆盖） |

### 值域校验属性

| 属性 | 类型 | 说明 |
|------|------|------|
| required | array | 必填子字段（object 类型内使用） |
| enum | array | 枚举值域 |
| enumType | string | `"tree"` 时 enum 为树形结构 |
| maximum | number | 数字最大值 |
| exclusiveMaximum | boolean | 是否排除 maximum |
| minimum | number | 数字最小值 |
| exclusiveMinimum | boolean | 是否排除 minimum |
| minLength | string/array | 最小长度 |
| maxLength | string/array | 最大长度 |
| trim | string | 去除空白：`none`/`both`/`start`/`end` |
| format | string | 格式：`"url"` / `"email"` |
| pattern | string | 正则表达式 |
| validateFunction | string | 扩展校验函数名 |
| fileMediaType | string | 文件类型：`all`/`image`/`video`（`bsonType="file"` 时） |
| fileExtName | string | 文件扩展名过滤，逗号分隔 |

### 权限与关联

| 属性 | 类型 | 说明 |
|------|------|------|
| permission | object | 字段级权限控制 |
| foreignKey | string | 外键关联：`表名.字段名` |
| parentKey | string | 父子关系（树形查询） |

### schema2code 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| label | string | 表单项 label（不填则用 title） |
| group | string | 分组 ID |
| order | int | 表单项排序序号 |
| componentForEdit | Object/Array | 编辑页组件（add.vue、edit.vue） |
| componentForShow | Object/Array | 展示页组件（list.vue、detail.vue） |

## 字段类型 (bsonType)

| 类型 | 说明 |
|------|------|
| `bool` | 布尔值 |
| `string` | 字符串 |
| `password` | 密码字符串，clientDB 完全不可读写（即使 admin） |
| `int` | 整数 |
| `double` | 浮点数（慎用，有精度问题，金额建议用 int 以分为单位） |
| `object` | JSON 对象（地理位置也属于 object） |
| `file` | 文件对象，固定格式存储云存储文件信息 |
| `array` | 数组 |
| `timestamp` | 时间戳（毫秒数字，推荐使用以屏蔽时区差异） |
| `date` | 日期 |

### file 类型格式

```json
{
  "name": "文件名.jpg",
  "extname": "jpg",
  "url": "https://xxx.com/file.jpg",
  "size": 102400,
  "image": {
    "width": 800,
    "height": 600
  }
}
```

> 配套组件：`<uni-file-picker>`，可自动上传到云存储并写入 file 字段。

### arrayType（数组子类型）

```json
{
  "bsonType": "array",
  "arrayType": "file",
  "title": "照片列表"
}
```

## 默认值

### defaultValue vs forceDefaultValue

| 对比项 | defaultValue | forceDefaultValue |
|--------|-------------|-------------------|
| 客户端可覆盖 | ✅ 是 | ❌ 否 |
| 适用场景 | 可选默认值 | 不可篡改的值（创建时间、用户ID等） |

### 预置变量 `$env`

```json
{
  "defaultValue": { "$env": "now" },
  "forceDefaultValue": { "$env": "uid" }
}
```

| 变量 | 说明 |
|------|------|
| `now` | 当前服务器时间戳 |
| `clientIP` | 当前客户端 IP |
| `uid` | 当前用户 ID（基于 uni-id，未登录时报错） |

### 示例

```json
{
  "create_time": {
    "bsonType": "timestamp",
    "title": "创建时间",
    "forceDefaultValue": { "$env": "now" }
  },
  "user_id": {
    "bsonType": "string",
    "title": "用户ID",
    "forceDefaultValue": { "$env": "uid" }
  }
}
```

## 外键 (foreignKey)

描述表与表之间的关联关系，用于 JQL 联表查询。

### 用法

```json
{
  "user_id": {
    "bsonType": "string",
    "foreignKey": "uni-id-users._id",
    "title": "作者"
  }
}
```

> 格式：`表名.字段名`（如 `uni-id-users._id`）

### 设计原则

- **分表存储**：文章、评论、用户各自独立成表
- **用 ID 关联**：文章表存 `user_id`（用户表的 `_id`），不存用户名、头像等冗余数据
- **在引用方配置**：foreignKey 配在引用方字段（文章表的 `user_id`），不是被引用方

### 联表查询

配好 foreignKey 后，JQL 自动支持联表查询，无需写 join：

```js
// 自动联表：order 表的 book_id 指向 book 表的 _id
const res = await db.collection('order', 'book').get()
```

## 树形表 (parentKey)

描述同一表内记录的父子关系，用于 JQL 树形查询。

### 用法

```json
{
  "parent_id": {
    "bsonType": "string",
    "parentKey": "_id",
    "title": "父部门ID"
  }
}
```

> `parentKey` 指向同表的另一个字段（通常是 `_id`），表示"本字段的值 = 父记录的该字段值"。

### 树形查询

```js
const res = await db.collection('department').get({
  getTree: {
    limitLevel: 10,
    startWith: 'parent_id == null || parent_id == ""'
  }
})
// 返回树形结构，子节点在 children 字段下
```

## 值域校验 (Validator)

校验系统由 4 部分组成：

1. **字段属性配置**：required、minimum、maxLength、format、pattern、enum、trim 等
2. **字段间约束**：fieldRules
3. **扩展校验函数**：validateFunction
4. **错误提示**：errorMessage

### 1. 字段属性校验

#### required 必填

```json
{
  "required": ["name", "tel"]
}
```

- 未传字段 → 跳过其他校验
- 传了字段 → 执行其他校验规则

#### format 格式

```json
{
  "email": {
    "bsonType": "string",
    "format": "email"
  }
}
```

目前支持：`"url"` / `"email"`

#### pattern 正则

```json
{
  "tel": {
    "bsonType": "string",
    "pattern": "^\\+?[0-9-]{3,20}$"
  }
}
```

#### enum 枚举

**简单数组：**

```json
{
  "gender": {
    "bsonType": "string",
    "enum": ["0", "1", "2"]
  }
}
```

**带描述的数组（推荐）：**

```json
{
  "gender": {
    "bsonType": "string",
    "enum": [
      { "value": "0", "text": "未知" },
      { "value": "1", "text": "男" },
      { "value": "2", "text": "女" }
    ]
  }
}
```

**数据表查询：**

```json
{
  "nation": {
    "bsonType": "string",
    "foreignKey": "opendb-nation-china.name",
    "enum": {
      "type": "query",
      "value": {
        "collection": "opendb-nation-china",
        "field": "name"
      }
    }
  }
}
```

**树形数据（enumType: "tree"）：**

```json
{
  "city": {
    "bsonType": "string",
    "enumType": "tree",
    "enum": {
      "type": "query",
      "value": {
        "collection": "opendb-city-china",
        "field": "name",
        "getTree": { "limitLevel": 3 }
      }
    }
  }
}
```

> schema2code 自动生成多级级联选择组件。

#### trim 去除空白

```json
{
  "name": {
    "bsonType": "string",
    "trim": "both"
  }
}
```

值：`none` / `both` / `start` / `end`（默认 `none`）

> trim 优先级高于其他校验规则（format、pattern、minLength 等）。

### 2. fieldRules 字段间校验

> HBuilderX 3.1.0+ 支持

```json
{
  "fieldRules": [
    {
      "rule": "end_date > create_date",
      "errorMessage": "结束时间需大于开始时间"
    },
    {
      "rule": "start_time < now",
      "errorMessage": "开始时间不能晚于当前时间"
    }
  ]
}
```

- `rule` 语法同 JQL where，支持数据库运算方法
- 新增/更新时校验所有相关字段的 fieldRules
- 不支持正则

### 3. validateFunction 扩展校验函数

当属性配置和 fieldRules 不能满足需求时，可编写 JS 函数校验。

**创建方式：**
- HBuilderX：`database` 目录右键 → 创建数据库扩展校验函数
- Web 控制台：数据库 → 扩展校验函数 → 新增

**示例：**

```js
// uniCloud/database/validateFunction/checkAge.js
module.exports = function(rule, value, data, callback) {
  if (value < 0 || value > 150) {
    callback({
      code: 'AGE_INVALID',
      message: '年龄必须在 0-150 之间'
    })
  } else {
    callback(true)
  }
}
```

**在 Schema 中引用：**

```json
{
  "age": {
    "bsonType": "int",
    "validateFunction": "checkAge"
  }
}
```

> validateFunction 类型为字符串时云端和客户端同时生效。类型为对象时可配置 `"client": false` 仅云端生效。

### 4. errorMessage 自定义错误提示

```json
{
  "name": {
    "bsonType": "string",
    "minLength": 2,
    "maxLength": 17,
    "errorMessage": {
      "minLength": "姓名至少 2 个字符",
      "maxLength": "姓名最多 17 个字符"
    }
  }
}
```

`{}` 为占位符，可引用 `title`、`label` 等属性。

## 权限系统 (Permission)

### 概述

- JQL / clientDB 强依赖此权限系统
- 规则：对数据的指定 + 对角色的指定 → 匹配则通过
- **admin 角色（超级管理员）不受 Schema 权限限制**
- 不配置 permission → 所有操作默认 `false`（admin 例外）

### 表级权限

```json
{
  "permission": {
    "read": true,
    "create": false,
    "update": "doc._id == auth.uid",
    "delete": false,
    "count": true
  }
}
```

| 权限 | 说明 |
|------|------|
| `read` | 读取（get） |
| `create` | 新增（add） |
| `update` | 更新（update） |
| `delete` | 删除（remove） |
| `count` | 计数（HBuilderX 3.1.0+） |

> count 操作同时触发 `read` + `count` 权限校验。

### 字段级权限

```json
{
  "age": {
    "bsonType": "int",
    "permission": {
      "read": true,
      "write": "doc._id == auth.uid"
    }
  }
}
```

- 子级继承父级权限（需同时满足）
- `bsonType: "password"` 的字段 clientDB 完全不可操作（即使 admin）

### 数据级权限

使用 `doc` 变量指定数据条件：

```json
{
  "permission": {
    "read": "doc.status == true",
    "update": "doc._id == auth.uid",
    "delete": "doc.user_id == auth.uid"
  }
}
```

### 权限变量

| 变量 | 说明 |
|------|------|
| `auth.uid` | 当前用户 ID |
| `auth.role` | 用户角色数组（uni-id） |
| `auth.permission` | 用户权限数组（uni-id） |
| `doc` | 目标数据记录（不可用于 create） |
| `now` | 当前服务器时间戳（毫秒） |

### 权限运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `==` | 等于 | `auth.uid == 'abc'` |
| `!=` | 不等于 | `auth.uid != null` |
| `>` | 大于 | `doc.age > 10` |
| `>=` | 大于等于 | `doc.age >= 10` |
| `<` | 小于 | `doc.age < 10` |
| `<=` | 小于等于 | `doc.age <= 10` |
| `in` | 在数组中 | `doc.status in ['a','b']` |
| `!` | 非 | `!(doc.status in ['a','b'])` |
| `&&` | 与 | `auth.uid == 'a' && doc.age > 10` |
| `\|\|` | 或 | `auth.uid == 'a' \|\| doc.age > 10` |

### get 方法（跨表权限判断）

在权限规则中通过 `get` 方法获取其他表的数据：

```json
{
  "permission": {
    "create": "get('database.user.' + auth.uid).score > 100"
  }
}
```

> `get` 参数必须是唯一确定值，格式：`database.表名.记录ID`

### 权限排查步骤

1. 确认连接的是云端还是本地（云端需上传 schema）
2. 检查字段级权限配置
3. 确认访问的数据是否为权限规则的子集
4. 检查是否访问了 `password` 类型字段

## schema.ext.js 触发器

schema.json 是配置，schema.ext.js 是编程扩展。在数据增删改查时触发相应操作。

> 详见 [数据库触发器](references/database-trigger.md)

## schema2code 代码生成

根据 Schema 自动生成前端页面：
- 列表页（list.vue）
- 详情页（detail.vue）
- 新增页（add.vue）
- 编辑页（edit.vue）

入口：
1. Web 控制台 → Schema → schema2code
2. HBuilderX → Schema 右键 → schema2code

> 详见 [schema2code 文档](https://doc.dcloud.net.cn/uniCloud/schema2code.html)

## 最佳实践

1. **分表设计**：独立实体分表存储，用 foreignKey 关联
2. **ID 关联**：表间通过 `_id` 关联，不存冗余字段（除非为减少联表查询）
3. **时间用 timestamp**：屏蔽时区差异，前端渲染用组件格式化
4. **金额用 int**：以分为单位，避免 double 精度问题
5. **密码用 password 类型**：clientDB 完全不可读写
6. **必填 + 校验**：配合 `required`、`pattern`、`enum`、`validateFunction`
7. **强制默认值**：创建时间、用户 ID、客户端 IP 用 `forceDefaultValue`
8. **权限最小化**：只开放必要的读写权限
9. **配合 openDB**：参考官方开源数据库规范（用户表、文章表等模板）
