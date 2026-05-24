# URL化 (HTTP 触发)

## 简介

云函数/云对象 URL化 是 uniCloud 提供的 HTTP 访问服务，让开发者通过 HTTP URL 方式访问云函数或云对象。

**使用场景：**
- App 端微信支付需要服务器回调地址
- 非 uni-app 系统需要连接 uniCloud
- 需要传统 HTTP 接口的任何场景

## 操作步骤

1. 登录 [uniCloud 后台](https://unicloud.dcloud.net.cn/)，选择服务空间
2. 点击左侧菜单【云函数】，进入云函数页面
3. 点击需要配置的云函数的【详情】按钮，配置访问路径

> 配置路径为 `/test` 时，`/test`、`/test/a`、`/test/b` 都会执行此云函数

### 绑定自定义域名

1. 点击【域名绑定】查看默认域名及自定义域名列表
2. 点击【添加域名】进行配置
3. 配置 CNAME 解析

**注意：**
- 腾讯云/阿里云每个服务空间最多绑定 1 个自定义域名，支付宝最多 3 个
- 绑定的域名必须已备案
- 阿里云使用默认域名在浏览器访问会触发下载

## 普通云函数 URL化

### 访问方式

```
GET/POST https://${云函数Url化域名}/${path}
```

### 入参结构（集成请求）

```js
exports.main = async (event, context) => {
  // event 结构如下：
  // {
  //   path: '/test',           // 访问路径
  //   httpMethod: 'GET',       // HTTP 方法
  //   headers: { ... },        // 请求头
  //   queryParameters: { ... }, // GET 参数
  //   body: '...',             // POST body
  //   isBase64Encoded: false
  // }
}
```

示例 — GET `https://${域名}/test?a=1&b=2`：

```js
event = {
  path: '/test',
  httpMethod: 'GET',
  queryParameters: { a: '1', b: '2' },
  headers: { ... }
}
```

## 云对象 URL化

> 新增于 HBuilderX 3.5.2

### 访问方式

以 URL化路径/云对象方法名 访问：

```
GET/POST https://${域名}/todo/addTodo?title=xxx&content=xxx
```

- `/todo/addTodo` → 调用 `addTodo` 方法
- `/todo/addTodo/self` 和 `/todo/addTodo/group` → 也会调用 `addTodo` 方法（多段路径）
- 方法名区分大小写，不可含 `/`

### 入参

URL 内 query 部分转换为方法入参：

```js
// 访问 /todo/addTodo?title=todo-title&content=todo-content
async addTodo(title, content) {
  console.log(title)   // 'todo-title'
  console.log(content) // 'todo-content'
}
```

> URL 解析出的参数均为**字符串类型**

### 获取 POST 数据

使用 `this.getHttpInfo()` 获取完整的 HTTP 请求信息。

> URL化调用云对象时，`_before` 和 `_after` 均正常执行。

## 返回值

### 返回字符串或数字

```js
return 'Hello'
// HTTP 响应：Hello
```

### 返回 Object

```js
return { code: 200, data: 'ok' }
// HTTP 响应头 Content-Type: application/json
// HTTP 响应体：{"code":200,"data":"ok"}
```

### 集成响应

```js
return {
  statusCode: 200,
  headers: {
    'Content-Type': 'text/html',
    'Set-Cookie': 'token=xxx'
  },
  body: '<h1>Hello</h1>'
}
```

#### 返回 HTML

```js
return {
  statusCode: 200,
  headers: { 'Content-Type': 'text/html' },
  body: '<h1>Hello uniCloud</h1>'
}
```

#### 返回二进制文件

```js
return {
  statusCode: 200,
  headers: { 'Content-Type': 'image/png' },
  isBase64Encoded: true,
  body: imageBase64String
}
```

#### 自定义状态码/重定向

```js
return {
  statusCode: 302,
  headers: {
    'Location': 'https://example.com'
  },
  body: ''
}
```

## 处理 Cookie

云函数中使用 Cookie 需要依赖 `cookie` npm 包：

```js
// 普通云函数
const cookie = require('cookie')
exports.main = async (event, context) => {
  const cookies = cookie.parse(event.headers.cookie || '')
  return {
    headers: {
      'Set-Cookie': cookie.serialize('token', 'xxx', { httpOnly: true })
    },
    body: 'ok'
  }
}
```

## 请求/响应限制

| 云厂商 | 请求 Body | 响应 Body |
|--------|----------|----------|
| 阿里云 | ≤ 2 MB | ≤ 2 MB |
| 腾讯云 | 文本 ≤ 100 KB，二进制 ≤ 20 MB | ≤ 6 MB |
| 支付宝云 | ≤ 32 MB | ≤ 32 MB |

## 注意事项

- URL化场景无法获取客户端平台等信息，但可获取 clientIP 和 userAgent
- POST 请求体可能被转成 base64，需进行转换
- `event.path` / `httpInfo.path` 表示以配置的 URL化路径为根路径的访问路径
- 安全：需在代码中做好权限控制，避免未授权访问
