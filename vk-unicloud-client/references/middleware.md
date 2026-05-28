# 过滤器/中间件

过滤器是 router 级别的请求拦截机制，对**云函数和云对象都生效**。通过 regExp 匹配 URL，在业务代码执行前后进行统一拦截。

> 过滤器文件放在 `router/middleware/modules/` 下，所有 `.js` 文件自动加载。每个文件导出一个数组。

## 配置结构

```js
module.exports = [
  {
    id: 'myFilter',                     // 全局唯一 ID（相同 ID 会覆盖）
    regExp: '^client/shop/manage',      // 正则匹配 URL
    description: '过滤器描述',
    index: 250,                         // 执行顺序（越小越先执行）
    mode: 'onActionExecuting',          // 执行模式
    enable: true,                       // 是否启用
    main: async function(event) {
      let { util, data, filterResponse, url } = event;
      let { vk, db, _ } = util;

      // 拦截: 返回 code 非 0
      // return { code: -1, msg: '拦截原因' };

      // 放行: 返回 code 0
      return { code: 0, msg: 'ok' };
    },
  },
];
```

## 参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `id` | String | 全局唯一 ID |
| `regExp` | String/Array | 正则匹配规则。字符串或字符串数组 |
| `description` | String | 描述 |
| `index` | Number | 执行顺序（越小越先执行） |
| `mode` | String | 执行模式（见下表） |
| `enable` | Boolean | 是否启用 |
| `main` | Function | 执行函数 |
| `returnMode` | Number | 返回值模式：0=Object.assign 合并，1=完全替换 |

## 执行模式

| mode | 说明 | 典型场景 |
|---|---|---|
| `onActionExecuting` | action 执行前（最常用） | 权限检查、参数验证 |
| `onActionExecuted` | action 执行后 | 结果转换、日志记录 |
| `onActionIntercepted` | action 被其他中间件拦截后 | 资源清理 |
| `onActionError` | action 异常时 | 异常处理、日志 |

## 框架内置过滤器

| ID | regExp | index | 说明 |
|---|---|---|---|
| pub | `/pub/` | 100 | 放行所有请求 |
| kh | `/kh/` | 200 | 检测 token，注入 userInfo/uid |
| sys | `/sys/` | 300 | 检测登录 + 管理员权限 |

自定义过滤器的 `index` 必须根据需要设置：
- 在 kh 之后执行：index > 200
- 在 sys 之后执行：index > 300

## regExp 写法

```js
// 匹配所有
regExp: '(.*)'

// 匹配 kh 目录
regExp: '/kh/'

// 匹配指定模块
regExp: '^client/shop/manage'

// 精确匹配
regExp: '^client/order/kh/getList$'

// 多个匹配
regExp: ['^client/order/kh/add$', '^client/order/kh/update$']

// 匹配范围
regExp: '^client/(order|product)/(kh|sys)/(.*)'
```

**重要：** regExp 使用标准正则语法，`*` 是量词（匹配前一字符零次或多次），不是通配符。匹配任意字符用 `(.*)`。

## 过滤器注入数据

过滤器可以向 `filterResponse` 注入数据，后续业务代码通过 `event.filterResponse` 或 `this.getClientInfo().filterResponse` 获取：

```js
// 过滤器中
filterResponse.shop = shopData;

// 云函数中
let { filterResponse } = event;
let shop = filterResponse.shop;

// 云对象中
let { filterResponse } = this.getClientInfo();
let shop = filterResponse.shop;
```

## 自定义过滤器示例

### 店铺权限过滤器

```js
module.exports = [
  {
    id: 'shopManage',
    regExp: '^client/shop/manage',
    description: '店铺管理接口权限检测',
    index: 250,
    mode: 'onActionExecuting',
    enable: true,
    main: async function(event) {
      let { util, filterResponse } = event;
      let { vk } = util;
      let { uid, userInfo = {} } = filterResponse;

      let shop = await vk.baseDao.findByWhereJson({
        dbName: 'shops',
        whereJson: { owner_id: uid },
      });
      if (!shop) return { code: -1, msg: '无店铺管理权限' };

      filterResponse.shop = shop;
      return { code: 0, msg: 'ok' };
    },
  },
];
```

### 多店铺权限过滤器

```js
module.exports = [
  {
    id: 'shopManage',
    regExp: ['^client/business/(.*)kh/', '^client/business/(.*)sys/'],
    description: '多店铺权限检测',
    index: 310,
    mode: 'onActionExecuting',
    enable: true,
    main: async function(event) {
      let { data = {}, util, filterResponse } = event;
      let { vk, db, _ } = util;
      let { uid, userInfo = {} } = filterResponse;
      let { shop_ids = [] } = userInfo;
      let { shop_id } = data;
      if (vk.pubfn.isNull(shop_id)) return { code: -1, msg: '店铺id不能为空' };
      if (shop_ids.indexOf(shop_id) === -1) return { code: -1, msg: '无权限操作此店铺' };
      return { code: 0, msg: 'ok' };
    },
  },
];
```

### 加密通信过滤器

```js
module.exports = [
  {
    id: 'encryptFilter',
    regExp: ['^template/test/pub/testEncryptRequest$', '^template/encrypt/(.*)'],
    description: '加密函数拦截器',
    index: 10,
    mode: 'onActionExecuting',
    enable: true,
    main: async function(event) {
      if (!event.encrypt) return { code: 413, msg: '请求非法，请求参数未加密' };
      return { code: 0, msg: 'ok' };
    },
  },
];
```

### 后置过滤器（修改返回值）

```js
module.exports = [
  {
    id: 'modifyResponse',
    regExp: '^xxx/kh',
    index: 310,
    mode: 'onActionExecuted',
    main: async function(event, serviceRes) {
      serviceRes.msg = '被过滤器修改后的值';
      return serviceRes;
    },
  },
];
```

## 使用场景

1. 权限校验
2. 统一加解密
3. 写日志
4. 请求参数过滤处理
5. 返回数据过滤处理
