# HTTP 请求

## uniCloud.httpclient.request

云函数中请求其他 HTTP 服务，无需额外依赖。返回 [urllib](https://github.com/node-modules/urllib) 实例。

### 基本用法

```js
const result = await uniCloud.httpclient.request('https://api.example.com/data', {
  method: 'GET',
  dataType: 'json'
})
console.log(result.data)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| method | String | GET | 请求方法：GET, POST, DELETE, PUT |
| data | Object | — | 发送的数据 |
| content | String/Buffer | — | 手动设置请求 payload |
| contentType | String | — | 如设为 `json`，自动设置 Content-Type |
| dataType | String | — | `'json'`（自动解析）、`'text'`、`''`（buffer，默认） |
| headers | Object | — | 请求头 |
| timeout | Number/Array | 5000 | 超时时间，数组时 [请求超时, 返回超时] |
| auth | String | — | Basic Auth，`user:password` 格式 |
| gzip | Boolean | false | 支持 gzip 响应 |
| followRedirect | Boolean | false | 是否自动重定向 |
| streaming | Boolean | false | 是否返回响应流 |

### GET 请求

```js
const result = await uniCloud.httpclient.request('https://api.example.com/data', {
  method: 'GET',
  data: { page: 1, size: 10 },
  dataType: 'json',
  timeout: 10000
})
```

### POST JSON

```js
const result = await uniCloud.httpclient.request('https://api.example.com/submit', {
  method: 'POST',
  data: { name: 'test', value: 123 },
  contentType: 'json',
  dataType: 'json'
})
```

### POST 表单

```js
const result = await uniCloud.httpclient.request('https://api.example.com/form', {
  method: 'POST',
  data: { field1: 'value1', field2: 'value2' },
  dataType: 'json'
})
```

> 默认 `dataAsQueryString` 为 true，POST 表单数据会自动转换为 query string。

### 上传文件

```js
const result = await uniCloud.httpclient.request('https://api.example.com/upload', {
  method: 'POST',
  files: fileBuffer,  // ReadStream/Buffer/String
  dataType: 'json'
})
```

### 注意事项

- 默认不处理返回数据（返回 buffer），需设置 `dataType: 'json'` 自动解析 JSON
- 设置 `content` 后会忽略 `data`
- 设置 `files` 后自动使用 `multipart/form-data` 格式

## uniCloud.request

> 新增于 HBuilderX 3.8.10

简化版 HTTP 请求，类似 `uni.request`。

```js
const res = await uniCloud.request({
  url: 'https://api.example.com/data',
  method: 'GET',
  data: { page: 1 },
  dataType: 'json',
  timeout: 60000
})
console.log(res.statusCode)
console.log(res.data)
console.log(res.header)
```

### 参数

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| url | String | — | 服务器接口地址（必填） |
| data | Object/String/ArrayBuffer | — | 请求参数 |
| header | Object | — | 请求头 |
| method | String | GET | 请求方法 |
| timeout | Number | 60000 | 超时时间（ms） |
| dataType | String | json | `json` 时自动 JSON.parse |
| responseType | String | text | `text` 或 `buffer` |
| sslVerify | Boolean | true | 验证 SSL 证书 |

### 返回值

| 属性 | 类型 | 说明 |
|------|------|------|
| statusCode | number | 响应状态码 |
| data | Object/String/ArrayBuffer | 响应结果 |
| header | Object | 响应头 |

## 发送 FormData

微信小程序等服务端接口常需要 FormData 格式：

```js
const result = await uniCloud.httpclient.request('https://api.weixin.qq.com/imgSecCheck', {
  method: 'POST',
  data: {
    media: {
      value: imageBuffer,
      options: {
        filename: 'image.png',
        contentType: 'image/png'
      }
    }
  },
  dataType: 'json'
})
```

## WebSocket

### 连接 WebSocket

```js
const socketTask = uniCloud.connectSocket({
  url: 'wss://example.com/ws',
  header: { 'Authorization': 'Bearer xxx' },
  protocols: ['protocol1']
})
```

### SocketTask API

```js
// 监听连接打开
socketTask.onOpen((data) => {
  console.log('连接已打开')
})

// 监听消息
socketTask.onMessage((data) => {
  console.log('收到消息:', data.data)
})

// 发送数据
socketTask.send({ data: 'Hello' })

// 监听关闭
socketTask.onClose((data) => {
  console.log('连接关闭:', data.code, data.reason)
})

// 监听错误
socketTask.onError((err) => {
  console.error('错误:', err.errMsg)
})

// 关闭连接
socketTask.close({ code: 1000, reason: '正常关闭' })
```

## 阿里云固定出口 IP

> 新增于 HBuilderX 3.5.5

阿里云必须使用 `uniCloud.httpProxyForEip` 发送请求才能固定出口 IP：

```js
// GET 请求
const result = await uniCloud.httpProxyForEip({
  url: 'https://weixin.qq.com/api',
  method: 'GET',
  dataType: 'json'
})

// POST JSON
const result = await uniCloud.httpProxyForEip({
  url: 'https://weixin.qq.com/api',
  method: 'POST',
  data: { key: 'value' },
  dataType: 'json'
})
```

> 当前仅支持 `weixin.qq.com` 泛域名。代理请求超时 5 秒。
