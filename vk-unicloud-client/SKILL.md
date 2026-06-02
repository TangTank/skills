---  
name: vk-unicloud-client  
description:  "Use when developing with vk-unicloud-router on uni-app + uniCloud, including cloud function routing, cloudObject, vk.baseDao, vk.callFunction, Dao 2.0, permissions, vk.userCenter, database operations, middleware filters, and WeChat mini program server APIs."  
---  

# vk-unicloud-router 开发规范与 API 参考

vk-unicloud-router 是基于 uniCloud 的云函数路由模式开发框架，用于快速开发 uni-app 全栈应用。它封装了路由管理、权限控制、数据库操作（vk.baseDao）等能力，所有开发必须遵循框架约定，禁止使用原生 uniCloud API。  

## When to Use

**适用场景：**  

- 使用 vk-unicloud-router 框架的 uni-app 项目  
- 编写云函数或云对象后端接口  
- 前端调用云函数（vk.callFunction / uni.vk.importObject）  
- 数据库增删改查、连表查询、事务操作  
- 用户登录注册、权限校验  
- 微信小程序服务端 API 调用  

**不适用：**  

- 不使用 vk-unicloud-router 的 uniCloud 项目（直接用原生 API）  
- 纯前端项目（无云函数）  
- admin 管理后台开发（参见 vk-unicloud-admin skill）  

## 核心约束

以下规则不可违背，每一条都源于框架的实际运行机制：  

1. **禁止原生 uniCloud API** - 不使用 `uniCloud.database()`、`db.collection()` 等原生方法，所有数据库操作通过 `vk.baseDao` 完成  
2. **前端请求用 vk 框架方法** - 不使用原生 `uniCloud.callFunction`，使用 `vk.callFunction` 或 `uni.vk.importObject`（云对象），因为它们自动携带 token、处理错误和加载状态  
3. **后端使用标准模板** - 云函数模式用 `main: async (event) => {}` 解构 event；云对象模式用 `isCloudObject: true` + 方法函数 + `this` 上下文  
4. **约定式路由** - URL 直接映射到 `service/` 目录下的文件路径（云函数）或文件名.方法名（云对象），不需要手动配置路由  
5. **权限由命名决定** - 云函数通过目录名 `pub/kh/sys` 决定；云对象通过函数名前缀 `pub_`/`kh_`/`sys_` 或文件名决定  
6. **vk.baseDao 没有 find() 方法** - 查询单条用 `findById()` 或 `findByWhereJson()`，查询多条用 `select()` 或 `selects()`  

## 项目结构与路由映射

```
${uniCloud目录}/
└── cloudfunctions/
    └── router/                    # 唯一的后端入口云函数
        ├── service/               # 业务逻辑（URL 映射到此目录）
        │   ├── client/moduleName/ # 客户端业务模块
        │   │   ├── pub/           # 公开接口（所有人可访问）
        │   │   └── kh/            # 用户接口（需登录）
        │   └── user/              # 用户中心
        │       ├── pub/           # 登录注册
        │       ├── kh/            # 用户私有
        │       └── sys/           # 管理后台
        ├── middleware/modules/    # 过滤器/中间件（自动加载）
        ├── dao/                   # Dao 2.0 数据访问层
        └── util/pubFunction.js    # 公共函数
```

### 路由映射规则

| 前端调用 URL | 映射到的文件 |  
|---|---|  
| `client/order/kh/getList` | `router/service/client/order/kh/getList.js`（云函数） |  
| `client/order.getList` | `router/service/client/order.js` 的 `getList` 方法（云对象） |  

### 目录权限模型

| 目录 | 访问权限 | userInfo/uid 可用 |  
|---|---|---|  
| `pub/` | 所有人可访问 | 否（除非传 `need_user_info:true`） |  
| `kh/` | 必须登录 | 是（自动注入） |  
| `sys/` | 必须登录 + 管理员权限 | 是（自动注入） |  

## 两种后端模式：云函数 vs 云对象

| 特性 | 云函数模式 | 云对象模式 |  
|---|---|---|  
| 文件结构 | 一个文件 = 一个接口 | 一个文件 = 一组相关接口 |  
| 标记 | 无需标记（默认） | 必须设置 `isCloudObject: true` |  
| 函数签名 | `main: async (event) => {}` | `methodName: async function(data) {}` |  
| 获取 uid | `let { uid } = data;` | `let { uid } = this.getClientInfo();` |  
| 获取 vk | `let { vk } = util;` | `vk = uniCloud.vk;` |  
| 权限控制 | 通过**目录名** `pub/kh/sys` | 通过**函数名前缀** `pub_`/`kh_`/`sys_` |  
| 拦截器 | 全局中间件 | 内置 `_before`/`_after` |  

> 详细参见 [cloud-function-patterns.md](references/cloud-function-patterns.md) 和 [cloud-object-patterns.md](references/cloud-object-patterns.md)  

## API 速查

| 功能 | API |  
|------|-----|  
| 调用云函数/云对象 | `vk.callFunction({ url, data })` |  
| 云对象导入调用 | `uni.vk.importObject('client/order', { easy: true })` |  
| 用户登录 | `vk.userCenter.login({ data: { username, password } })` |  
| 手机号登录 | `vk.userCenter.loginBySms({ data: { mobile, code } })` |  
| 获取用户信息 | `vk.userCenter.getCurrentUserInfo()` |  
| 本地登录检查 | `vk.checkToken()` |  
| 数据库-增 | `vk.baseDao.add({ dbName, dataJson })` |  
| 数据库-删 | `vk.baseDao.del({ dbName, whereJson })` |  
| 数据库-改 | `vk.baseDao.update({ dbName, whereJson, dataJson })` |  
| 数据库-查单条 | `vk.baseDao.findById({ dbName, id })` |  
| 数据库-分页 | `vk.baseDao.select({ dbName, pageIndex, pageSize })` |  
| 数据库-连表 | `vk.baseDao.selects({ dbName, foreignDB })` |  
| 云端缓存 | `vk.getCacheManage().get(key)` / `.set(key, value, seconds)` |  
| 微信登录 | `vk.userCenter.loginByWeixin()` |  

> 完整数据库 API 参见 [database.md](references/database.md)，用户中心参见 [userCenter.md](references/userCenter.md)  

### 常用操作符（`_` = db.command）

```js
_.gt(18) / _.gte(18) / _.lt(100) / _.lte(100)  // 比较
_.neq(0) / _.in([1,2]) / _.nin([3]) / _.exists(true)
_.and([条件1, 条件2]) / _.or([条件1, 条件2])      // 逻辑
_.inc(1) / _.inc(-1) / _.remove()                 // 更新
whereJson: { name: new RegExp('关键词') }          // 模糊查询
```

> 完整操作符表参见 [database.md](references/database.md)  

## 前端调用示例

```js
// 云函数模式
let data = await vk.callFunction({
  url: 'client/order/kh/getList',
  title: '加载中...',
  data: { pageIndex: 1, pageSize: 10 },
});

// 云对象模式
const orderObj = uni.vk.importObject('client/order', { easy: true });
let data = await orderObj.getList({ pageIndex: 1, pageSize: 10 });
```

> 完整前端调用模式参见 [frontend-call.md](references/frontend-call.md)  

## 标准返回格式

```js
return { code: 0, msg: 'success', data: result };  // 成功
return { code: -1, msg: '错误信息' };                // 失败
// 分页查询自动返回: { code: 0, msg: '', rows: [], total: 0, hasMore: false }
```

## Common Mistakes

| 错误 | 正确做法 |  
|------|----------|  
| 用 `find()` 查单条 | 用 `findById()` 或 `findByWhereJson()` |  
| 用原生 `uniCloud.database()` | 用 `vk.baseDao` |  
| 用原生 `uniCloud.callFunction` | 用 `vk.callFunction` |  
| pub 目录直接取 `uid` | pub 目录需前端传 `need_user_info: true`，否则 uid 不可信 |  
| 云对象函数名无前缀（默认 kh）却想公开访问 | 加 `pub_` 前缀 |  
| `regExp` 用 `*` 作通配符 | `*` 是正则量词，匹配任意字符用 `(.*)` |  
| kh 目录传 `need_user_info: false` 后读 `userInfo` | 传 false 后 uid 可用，但 userInfo 为空 |  
| 事务超过 10 秒未提交 | 事务操作必须在 10 秒内完成 |  

## 参考文档

| 文件 | 内容 |  
|------|------|  
| [database.md](references/database.md) | 数据库完整参考（CRUD、连表、分组、事务、条件语法、操作符） |  
| [cloud-function-patterns.md](references/cloud-function-patterns.md) | 云函数模式（event 对象、Dao 2.0、公共函数） |  
| [cloud-object-patterns.md](references/cloud-object-patterns.md) | 云对象模式（this API、权限、拦截器、跨模式调用） |  
| [middleware.md](references/middleware.md) | 过滤器/中间件（router 级拦截，云函数和云对象通用） |  
| [frontend-call.md](references/frontend-call.md) | 前端调用（vk.callFunction、importObject、API 封装） |  
| [userCenter.md](references/userCenter.md) | 用户中心（登录/注册/手机/邮箱/Token） |  
| [jsapi.md](references/jsapi.md) | 工具函数（防抖/节流/日期/树操作/校验/导航/弹窗） |  
| [cache.md](references/cache.md) | 云端缓存 API（db/redis 双模式） |  
| [weixin.md](references/weixin.md) | 微信小程序服务端 API（登录/小程序码/订阅消息） |  
| [config.md](references/config.md) | app.config.js 完整配置说明 |  
| [quickstart.md](references/quickstart.md) | 安装步骤、框架初始化、UI 组件库集成 |  
