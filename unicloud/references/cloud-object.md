# 云对象 (Cloud Object)

> 新增于 HBuilderX 3.4.0

## 简介

云对象是对云函数的升级，将传统的 JSON 接口通信升级为模块化的对象调用。服务端编写 API 对象，客户端直接导入并调用方法。

- 入口文件：`index.obj.js`
- 客户端调用：`uniCloud.importObject('objectName')`

## 核心优势

- 更清晰的逻辑（面向对象而非面向接口）
- 更精简的代码（减少约 50% 代码量）
- IDE 内完善的代码提示
- 默认支持 uniCloud 响应体规范

## 基本结构

```js
// index.obj.js — 云对象 todo
module.exports = {
  _before() {},   // 预处理（可选）
  _after() {},    // 后处理（可选）

  async add(title, content) {
    const db = uniCloud.database()
    const res = await db.collection('todos').add({ title, content })
    return { errCode: 0, errMsg: 'success', data: res }
  },

  async get() {
    const db = uniCloud.database()
    const res = await db.collection('todos').get()
    return res.data
  }
}
```

## 客户端调用

```js
// 基础调用
const todo = uniCloud.importObject('todo')
const result = await todo.add('标题', '内容')

// 错误处理 — try catch
try {
  const result = await todo.add('标题', '内容')
} catch (e) {
  console.error(e.errCode, e.errMsg)
}

// 错误处理 — then catch
todo.add('标题', '内容')
  .then(res => console.log(res))
  .catch(e => console.error(e.errCode, e.errMsg))
```

### importObject 参数

```js
const todo = uniCloud.importObject('todo', {
  customUI: true,           // 关闭自动 UI（loading/toast）
  loadingOptions: {         // 自定义 loading
    title: '加载中...',
    mask: true
  },
  errorOptions: {           // 自定义错误提示
    type: 'toast',          // 'modal' | 'toast'
    title: '操作失败'
  }
})
```

## 云对象 API（this 对象）

### getClientInfo()

获取客户端信息（基于 `uni.getSystemInfo` 扩展）。

```js
const clientInfo = this.getClientInfo()
```

| 属性 | 类型 | 说明 |
|------|------|------|
| clientIP | string | 客户端 IP |
| userAgent | string | 客户端 UA |
| source | string | 调用来源：`client` / `function` / `http` / `timing` / `server` |
| requestId | string | 请求 ID |
| scene | string | 场景值 |

> 注意：除 clientIP 外，其他客户端信息仅 uni-app 客户端以云对象方式调用时才有。

### getCloudInfo()

获取云端信息。

```js
const cloudInfo = this.getCloudInfo()
```

| 属性 | 类型 | 说明 |
|------|------|------|
| provider | string | 供应商：`alipay` / `aliyun` / `tencent` |
| spaceId | string | 服务空间 ID |
| functionName | string | 云对象名称 |
| functionType | string | 固定为 `cloudobject` |
| runtimeEnv | string | `local` / `cloud` |

### getUniIdToken()

获取客户端 token（自动管理）。

```js
const token = this.getUniIdToken()
```

### getMethodName()

获取当前调用的方法名（主要用于 `_before` 拦截器）。

```js
const methodName = this.getMethodName()
```

### getParams()

获取当前参数列表（主要用于 `_before` 拦截器）。

```js
const params = this.getParams()
```

### getUniCloudRequestId()

获取当前请求 ID。

```js
const requestId = this.getUniCloudRequestId()
```

### getHttpInfo()

获取 URL 化时的 HTTP 信息（仅 URL 化场景可用）。

```js
const httpInfo = this.getHttpInfo()
// httpInfo: { path, httpMethod, headers, queryParameters, body, ... }
```

## 内置特殊方法

### _before — 预处理

在调用常规方法之前执行，一般用于拦截器、身份验证、参数校验。

```js
module.exports = {
  _before() {
    const methodName = this.getMethodName()
    if (methodName === 'add') {
      // 校验 token
      const token = this.getUniIdToken()
      if (!token) {
        throw new Error('未登录')
      }
    }
  },
  async add(title) {
    // 已通过 _before 校验
    // ...
  }
}
```

### _after — 后处理

对方法返回结果或抛出的错误进行再加工。

```js
module.exports = {
  _after(err, result) {
    if (err) {
      // 统一错误处理
      console.error(err)
      return { errCode: -1, errMsg: '服务器内部错误' }
    }
    // 对返回结果加工
    return result
  }
}
```

### _timing — 定时运行

> 新增于 HBuilderX 3.5.2

配置定时触发器后，定时执行此方法。

```js
module.exports = {
  async _timing() {
    // 定时执行的逻辑
    console.log('定时任务执行', new Date())
  }
}
```

> 定时触发云对象时，`_before` 和 `_after` 均**不执行**。

## 返回值规范

```js
// 正常返回
return { errCode: 0, data: result }

// 主动报错（遵循 uniCloud 响应体规范）
return { errCode: 'todo-not-found', errMsg: '待办事项不存在' }
```

客户端错误对象属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| errCode | string/number | 错误码 |
| errMsg | string | 错误信息 |
| requestId | string | 请求 ID |
| detail | Object | 完整错误响应（仅符合响应体规范时） |

## 云对象互调

```js
// 云对象 A 中调用云对象 B
const objB = uniCloud.importObject('object-b')
const result = await objB.someMethod()
```

## 跨服务空间调用

```js
// 获取其他服务空间的实例
const otherSpace = uniCloud.init({ spaceId: 'other-space-id' })
const otherObj = otherSpace.importObject('other-object')
const result = await otherObj.someMethod()
```

> 云端 `uniCloud.init` 仅腾讯、支付宝云支持，且仅能获取同账号下的服务空间。

## 多方法共享逻辑

云对象导出的不同方法之间不能互相调用，需将共享逻辑抽到导出对象外部：

```js
function sharedLogic(param) {
  // 共享逻辑
}

module.exports = {
  async methodA() {
    return sharedLogic('a')
  },
  async methodB() {
    return sharedLogic('b')
  }
}
```

## 参数体积上限

| 云厂商 | 上限 |
|--------|------|
| 支付宝云 | 6 MB |
| 阿里云 | 2 MB |
| 腾讯云 | 5 MB |

## 注意事项

- 云对象导出的方法**不可以是箭头函数**（会导致 this 指向不正确）
- 所有 `_` 开头的方法都是私有方法，客户端不可访问
- 云对象也可以引用公共模块或 npm 包
- 云对象内不可存在 `index.js`，云函数内不可存在 `index.obj.js`
