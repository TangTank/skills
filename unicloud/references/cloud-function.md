# 云函数 (Cloud Function)

## 简介

云函数是运行在云端的 JavaScript 代码，基于 Node.js 扩展。每个云函数是一个 JS 包，由 Serverless 调度系统分配硬件资源启动 Node 环境运行。

- 入口文件：`index.js`
- 云函数目录：`uniCloud/cloudfunctions/`
- 每个云函数是一个目录，可包含 `index.js`、`package.json` 及其他依赖文件

## 基本结构

```
cloudfunctions/
├── common/                      # 公共模块目录
│   └── hello-common/
│       ├── index.js
│       └── package.json
├── function-name/               # 云函数目录
│   ├── index.js                 # 入口文件
│   └── package.json             # 配置
└── object-name/                 # 云对象目录
    ├── index.obj.js             # 入口文件
    └── package.json
```

## 最简云函数

```js
// index.js
'use strict';
exports.main = async (event, context) => {
  return { errCode: 0, errMsg: 'success', data: 'Hello uniCloud' }
}
```

## 客户端调用方式

### callFunction 方式

```js
const res = await uniCloud.callFunction({
  name: 'function-name',
  data: { key: 'value' }
})
console.log(res.result)
```

### callFunction 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | String | 是 | 云函数名称 |
| data | Object | 否 | 云函数参数 |

### callFunction 响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errCode | String | 状态码，成功时不返回 |
| errMsg | String | 错误描述 |
| result | Object | 云函数执行结果 |
| requestId | String | 请求序列号，用于错误排查 |

## 云函数入参

```js
exports.main = async (event, context) => {
  // event — 客户端传入的参数
  // context — 请求上下文信息
  console.log(event)
  console.log(context)
}
```

### context 属性

| 属性 | 说明 |
|------|------|
| requestId | 当前请求 ID |
| FUNCTION_NAME | 云函数名 |
| FUNCTION_VERSION | 云函数版本 |
| ENV | 环境 ID |
| SOURCE | 调用来源 |

## 云函数间调用

```js
// 在云函数 A 中调用云函数 B
const res = await uniCloud.callFunction({
  name: 'function-B',
  data: { key: 'value' }
})
```

> 注意：云函数互调时通过公网访问，速度不如直接将逻辑放在调用方执行。调用方无法获取被调用方的客户端信息（如 uni-id-token），需手动传递。

## 递归调用

云函数可以递归调用自身，适用于任务拆分场景（如给10万用户发短信，单次最多50个）。

```js
exports.main = async (event, context) => {
  const { startIndex = 0, batchSize = 50 } = event
  const users = await getUsers(startIndex, batchSize)
  await sendSms(users)

  if (hasMoreUsers()) {
    await uniCloud.callFunction({
      name: 'same-function',
      data: { startIndex: startIndex + batchSize, batchSize }
    })
  }
  return { done: true }
}
```

## 冷启动与热启动

### 冷启动
云函数初次被触发时的完整流程：
1. Serverless 实例化计算实例
2. 加载函数代码
3. 启动 Node
4. 执行云函数代码

耗时一般在 1 秒左右。

### 热启动
实例被复用时，只执行云函数代码，毫秒级响应。

### 实例回收时间

| 云厂商 | 回收时间 |
|--------|----------|
| 支付宝云 | 60 秒 |
| 阿里云 | 15 分钟 |
| 腾讯云 | 30 分钟 |

### 减少冷启动建议

- 优先使用 clientDB
- 合并低频云函数到高频云函数中
- 使用定时任务持续运行低频函数
- 支付宝云/阿里云支持单实例多并发配置

## 单实例多并发

> 仅支付宝云与阿里云支持

在 uniCloud Web 控制台配置并发度（1-100），一个实例可同时处理多个请求。

### 适用场景

| 场景 | 适用性 | 理由 |
|------|--------|------|
| 函数中等待下游响应时间长 | ✅ 适用 | 等待不消耗资源，可并发节省费用 |
| 函数中有共享状态且不能并发访问 | ❌ 不适用 | 并发修改共享状态可能出错 |
| 单请求消耗大量 CPU/内存 | ❌ 不适用 | 并发会争抢资源 |

### 注意

- 并发度过高可能导致内存不足（OOM）
- 并发操作数据库性能不佳
- 全局变量可能被并发请求污染

## 无状态与全局变量

云函数中的全局变量是**伪全局变量**，在实例有效期内的多次请求中会复用。

```js
// ⚠️ 危险：count 在实例复用时会累加
let count = 0
exports.main = async (event, context) => {
  count++  // 可能返回 1, 2, 3...
  return count
}
```

### 正确的全局变量方案

- **静态全局变量** → 使用 `uni-config-center`
- **动态全局变量** → 使用 Redis

## return 策略

| 云厂商 | 行为 |
|--------|------|
| 阿里云 | return 后立即终止，包括 setTimeout 等异步操作 |
| 腾讯云 node8 | return 后不继续执行 |
| 腾讯云 node12 | 可配置 `keepRunningAfterReturn` |
| 支付宝云 | return 后还会继续执行异步逻辑 |
| 本地运行 | return 后可继续执行 300ms |

## Node 版本

| 云厂商 | 默认版本 | 可选版本 |
|--------|----------|----------|
| 支付宝云 | Node 18 | Node 16, 18 |
| 阿里云 | Node 16 | Node 12, 14, 16, 18, 20 |
| 腾讯云 | Node 16 | Node 12, 16, 18 |

> Node 版本仅在首次上传时生效，后续修改需删除云端云函数重新上传。

## 时区

| 云厂商 | 时区 |
|--------|------|
| 支付宝云 | UTC+8 |
| 阿里云 | UTC+0 |
| 腾讯云 | UTC+0 |

> 建议统一使用时间戳规避时区问题。

## 临时存储空间

每次执行的宿主环境可能不同，不建议使用 `fs` 文件系统。建议通过云数据库、云存储、Redis 替代。

## 异步行为

```js
// 使用 util.promisify 转换 callback 为 promise
const util = require('util')
const fs = require('fs')
const readFile = util.promisify(fs.readFile)

exports.main = async (event, context) => {
  const data = await readFile('./file.txt')
  return data
}
```

如果想在云函数内使用回调形式，可以让云函数返回一个 promise：

```js
exports.main = async (event, context) => {
  return new Promise((resolve, reject) => {
    someCallbackFunction((err, result) => {
      if (err) reject(err)
      else resolve(result)
    })
  })
}
```
