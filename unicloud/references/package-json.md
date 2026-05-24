# 云函数 package.json 配置

## 简介

从 HBuilderX 3.0 起，云函数目录下的 `package.json` 可用于配置云函数。本地编写后上传，设置自动在云端生效。

> package.json 是标准 JSON 文件，**不可带注释**。

## 完整示例

```json
{
  "name": "function-name",
  "version": "1.0.0",
  "description": "云函数描述",
  "main": "index.js",
  "dependencies": {
    "some-package": "^1.0.0"
  },
  "cloudfunction-config": {
    "runtime": "Nodejs16",
    "memory": 256,
    "timeout": 60,
    "keepRunningAfterReturn": false,
    "triggers": [
      {
        "name": "my-trigger",
        "config": "0 0 2 * * * *"
      }
    ],
    "extensions": {
      "uni-cloud-jql": true,
      "uni-cloud-redis": true,
      "uni-cloud-sms": false,
      "uni-cloud-verify": false,
      "uni-cloud-push": false
    }
  }
}
```

## cloudfunction-config 字段说明

### runtime — Node 版本

| 云厂商 | 可选值 | 默认值 |
|--------|--------|--------|
| 阿里云 | Nodejs12, 14, 16, 18, 20 | Nodejs16 |
| 腾讯云 | Nodejs12, 16, 18 | Nodejs16 |
| 支付宝云 | Nodejs16, 18 | Nodejs18 |

> 仅在首次上传云函数时生效，后续修改需删除云端云函数重新上传。

### memory — 运行内存

单个云函数实例使用的内存（MB）。

| 云厂商 | 默认值 |
|--------|--------|
| 支付宝云 | 512 MB |
| 阿里云正式版 | 512 MB |
| 腾讯云 | 256 MB |

> 阿里云不建议设置 128 MB（数据库访问可能缓慢）。

### timeout — 超时时间

非定时触发时的超时时间（秒）。

| 云厂商 | 默认超时 | 定时触发最大超时 |
|--------|----------|-----------------|
| 支付宝云 | 180 秒 | 3 小时 |
| 阿里云 | 120 秒 | 600 秒 |
| 腾讯云 | 60 秒 | 900 秒 |

### keepRunningAfterReturn

> 新增于 HBuilderX 3.5.1

控制云函数 return 后是否继续执行。

| 值 | 说明 |
|----|------|
| `true` | return 后继续执行（腾讯云 node12+ 默认行为） |
| `false` | return 后终止（阿里云/腾讯云 node8 默认行为） |

**使用场景：**

```js
exports.main = async (event, context) => {
  // 如果此云函数需要在 return 后继续发网络请求
  setTimeout(() => {
    console.log('延迟执行')
  }, 5000)

  return { done: true }
  // 阿里云：setTimeout 不会执行
  // 腾讯云 node12 + keepRunningAfterReturn:true：会执行，计费时间包含
}
```

**腾讯云 node12 + Redis 注意：**

```js
// 配置 keepRunningAfterReturn: false 时
// Redis 连接不会中断，下次请求可复用

// 配置 keepRunningAfterReturn: true 时
// 使用完毕需手动断开：redis.quit()
// 否则连接占用实例直到超时，产生额外费用
```

### triggers — 定时触发器

```json
{
  "triggers": [
    {
      "name": "daily-task",
      "config": "0 0 2 * * * *"
    },
    {
      "name": "hourly-check",
      "config": "0 0 * * * * *"
    }
  ]
}
```

> Cron 表达式统一 7 位格式，支付宝云/阿里云第七位设为 `*`。

### extensions — 扩展库

控制云函数加载哪些扩展库。

| 扩展库 | 配置 key | 说明 |
|--------|----------|------|
| JQL | `uni-cloud-jql` | JQL 语法操作数据库 |
| Redis | `uni-cloud-redis` | 使用 Redis |
| 短信 | `uni-cloud-sms` | 发送短信 |
| 一键登录 | `uni-cloud-verify` | 获取手机号 / 实人认证 |
| 推送 | `uni-cloud-push` | uni-push |

```json
{
  "extensions": {
    "uni-cloud-jql": true,
    "uni-cloud-redis": true
  }
}
```

> 未引用扩展库的，使用对应 API 时会报错。

## 配置同步

- 本地编写 → 上传云函数 → 自动在云端生效
- Web 控制台修改 → HBuilderX 下载云函数 → 自动写入 package.json
- 上传时 package.json 包含配置 → 同时更新云端配置

## 注意事项

- package.json 只有**云端部署**才生效，本地运行不生效
- `cloudfunction-config` **不可删除**云端配置（删除 package.json 中的 trigger 不会删掉云端触发器）
- `runtime` 仅在**创建时**生效，不可通过更新修改
- 插件作者发布插件时，应将特殊设置放入 package.json
- 云函数大小限制 **10 MB**（含 node_modules）
