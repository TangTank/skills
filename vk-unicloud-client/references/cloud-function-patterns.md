# 云函数高级模式

本文档涵盖 vk-unicloud-router 云函数路由模式的完整用法，包括 event 对象、模板、过滤器/中间件、Dao 2.0 和公共工具函数。

> 云对象路由模式请参见 [cloud-object-patterns.md](cloud-object-patterns.md)

## 目录

- [完整 event 对象](#完整-event-对象)
- [云函数模板](#云函数模板)
- [目录约定与权限](#目录约定与权限)
- [过滤器/中间件](#过滤器中间件)（独立文档：[middleware.md](middleware.md)）
- [Dao 2.0 数据访问层](#dao-20-数据访问层)
- [云函数间调用](#云函数间调用)
- [公共工具函数](#公共工具函数)

---

## 完整 event 对象

```js
let { data = {}, userInfo, util, filterResponse, originalParam } = event;
let { customUtil, uniID, config, pubFun, vk, db, _, $ } = util;
let { uid } = data;
```

### 参数详解

| 参数 | 说明 | 备注 |
|---|---|---|
| `data` | 前端传过来的请求参数 | 总是可用 |
| `userInfo` | 当前登录用户信息 | kh 目录自动注入；pub 目录需前端传 `need_user_info:true` |
| `uid` | 从 `data.uid` 获取当前登录用户 ID | kh 目录可信（从 token 解密）；pub 目录不解析 token |
| `util` | 工具包对象 | 总是可用 |
| `vk` | vk 实例（含 baseDao、pubfn 等） | 核心对象 |
| `db` | 数据库对象 | 一般通过 vk.baseDao 操作，不直接使用 |
| `_` | `db.command` 操作符 | 用于 `_.gt()`、`_.inc()` 等 |
| `$` | `db.command.aggregate` 聚合操作符 | 用于 `$.sum()`、`$.first()` 等 |
| `pubFun` | 公共函数 | 文件位于 `router/util/pubFunction.js` |
| `customUtil` | 自定义工具包 | 开发者自定义 |
| `uniID` | uni-id 实例对象 | 用于用户体系操作 |
| `config` | 全局配置 | 来自 `router/config.js` |
| `filterResponse` | 过滤器返回的数据 | 可获取过滤器注入的额外信息 |
| `originalParam` | 原始请求参数 | 含 event 和 context |

### originalParam.context 常用属性

| 属性 | 说明 |
|------|------|
| OS | 客户端系统：android/ios |
| PLATFORM | 运行平台：mp-weixin/app-plus/h5 |
| APPID | manifest.json 中的 appid |
| CLIENTIP | 客户端 IP |
| CLIENTUA | 客户端 User-Agent |
| DEVICEID | 客户端标识 |
| SPACEINFO | 环境信息 { spaceId, provider } |
| SOURCE | 调用方式：client/http/timing/server/function |
| RUNTIME_ENV | 运行环境：local/cloud |

```js
let clientIP = originalParam.context.CLIENTIP;
let platform = originalParam.context.PLATFORM;
let os = originalParam.context.OS;
```

### need_user_info 机制

**kh 目录：** 默认自动获取 userInfo。如果云函数不需要用户信息，前端传 `need_user_info: false` 可减少一次数据库查询（快约 100ms），但 uid 仍然可用（从 token 解密）。

```js
vk.callFunction({
  url: 'client/order/kh/getList',
  data: {
    need_user_info: false,    // 注意：放在 data 内部，不是与 data 同级
    pageIndex: 1,
  },
});
```

**pub 目录：** 默认不获取 userInfo 也不获取 uid。如需获取，前端传 `need_user_info: true`：

```js
vk.callFunction({
  url: 'client/product/pub/getDetail',
  data: {
    need_user_info: true,     // 放在 data 内部
    product_id: 'xxx',
  },
});
```

---

## 云函数模板

### 完整模板（推荐）

```js
'use strict';
module.exports = {
  /**
   * 函数描述
   * @url client/moduleName/kh/functionName 前端调用的url参数地址
   * @description 详细描述
   * @param {Object} data 请求参数
   * @param {String} uniIdToken 用户token
   * @param {String} userInfo 当前登录用户信息（仅kh目录有此值）
   * @param {Object} util 公共工具包
   * @param {Object} filterResponse 过滤器返回的数据
   * @param {Object} originalParam 原始请求参数
   */
  main: async (event) => {
    let { data = {}, userInfo, util, filterResponse, originalParam } = event;
    let { customUtil, uniID, config, pubFun, vk, db, _, $ } = util;
    let { uid } = data;
    let res = { code: 0, msg: '' };
    // 业务逻辑开始-----------------------------------------------------------

    // 业务逻辑结束-----------------------------------------------------------
    return res;
  },
};
```

### 简易模板

```js
'use strict';
module.exports = {
  /**
   * 函数描述
   * @url client/moduleName/pub/functionName
   */
  main: async (event) => {
    let { data = {}, userInfo, util, originalParam } = event;
    let { customUtil, config, pubFun, vk, db, _, $ } = util;
    let res = { code: 0, msg: '' };
    // 业务逻辑开始-----------------------------------------------------------

    // 业务逻辑结束-----------------------------------------------------------
    return res;
  },
};
```

### 分页查询示例

```js
main: async (event) => {
  let { data = {}, util } = event;
  let { vk, _ } = util;
  let { uid, pageIndex = 1, pageSize = 10, status } = data;
  let res = { code: 0, msg: '' };

  let whereJson = { user_id: uid };
  if (status !== undefined) whereJson.status = status;

  res = await vk.baseDao.select({
    dbName: 'orders',
    pageIndex,
    pageSize,
    getCount: true,
    whereJson,
    sortArr: [{ name: '_add_time', type: 'desc' }],
  });

  return res;
};
```

---

## 目录约定与权限

| 目录 | 访问权限 | userInfo/uid 可用 | 典型场景 |
|---|---|---|---|
| `pub/` | 所有人可访问 | 否（除非传 `need_user_info:true`） | 登录、注册、公开数据查询 |
| `kh/` | 必须登录 | 是（自动注入） | 用户个人操作、订单、收藏等 |
| `sys/` | 必须登录 + 需管理员权限 | 是（自动注入） | 后台管理、系统设置 |

---

## 过滤器/中间件

过滤器是 router 级别的请求拦截机制，对云函数和云对象都生效。

> 完整文档参见 [middleware.md](middleware.md)

---

## Dao 2.0 数据访问层

Dao 2.0 通过类继承封装表操作，推荐在正式项目中使用。

### 表名配置

```js
// dao/config.js
module.exports = {
  Tables: {
    user: 'uni-id-users',
    order: 'orders',
    product: 'products',
    shop: 'shops',
  },
};
```

### 编写 Dao 类

```js
// dao/modules/orderDao.js（文件名必须以 Dao.js 结尾）
const { BaseDao, Tables } = require('../base.js');

class OrderDao extends BaseDao {
  constructor(obj) {
    super(obj);
    this.tableName = Tables.order;
  }

  async getByOrderNo(orderNo) {
    return await this.findByWhereJson({
      whereJson: { order_no: orderNo },
    });
  }

  async getUserOrders(userId, pageIndex = 1, pageSize = 10) {
    return await this.select({
      pageIndex,
      pageSize,
      whereJson: { user_id: userId },
      sortArr: [{ name: '_add_time', type: 'desc' }],
      getCount: true,
    });
  }
}

module.exports = OrderDao;
```

### BaseDao 继承的方法

所有 `vk.baseDao` 的方法都可在 Dao 类中调用（不需要传 `dbName`）：

```js
this.add(dataJson)          this.adds(dataArray)
this.findById(id)           this.findByWhereJson(whereJson)
this.select(params)         this.selects(params)
this.count(whereJson)       this.updateById(id, dataJson)
this.update(whereJson, dataJson)
this.updateAndReturn(whereJson, dataJson)
this.deleteById(id)         this.del(whereJson)
this.setById(dataJson)
this.sum/max/min/avg({ fieldName, whereJson })
```

### 调用方式

```js
// 简易调用
let order = await vk.daoCenter.orderDao.findById(orderId);

// 完整调用（支持事务）
let order = await vk.daoCenter.orderDao.findById({
  db: transaction,
  id: orderId,
  fieldJson: { order_no: true, amount: true },
});

// 自定义方法
let order = await vk.daoCenter.orderDao.getByOrderNo('ORD20240101');
```

---

## 云函数间调用

```js
// 云函数 A 调用云函数 B
let res = await vk.callFunction({
  url: '其他云函数路径',
  data: { a: 1 },
});
```

url 化后参数在 `originalParam.event.body` 中（JSON 字符串），请求头在 `originalParam.event.headers` 中。

---

## 公共工具函数

### vk.pubfn 常用方法

```js
// 获取常用时间
let {
  todayStart, todayEnd,
  weekStart, weekEnd,
  monthStart, monthEnd,
  yearStart, yearEnd,
} = vk.pubfn.getCommonTime();

// 生成唯一 ID
let id = vk.pubfn.createOrderNo();

// 日期格式化
let str = vk.pubfn.timeFormat(Date.now(), 'yyyy-MM-dd hh:mm:ss');
```

### pubFunction.js 自定义公共函数

```js
// router/util/pubFunction.js
module.exports = {
  async myFunction(vk, params) {
    // ...
  },
};
```

在云函数中使用：`pubFun.myFunction(vk, params)`

> 更多 vk.pubfn 工具函数参见 [jsapi.md](jsapi.md)
