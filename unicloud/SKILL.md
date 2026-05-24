---
name: unicloud
version: 1.0.0
description: "uniCloud Serverless 云开发技能，覆盖云函数、云对象、JQL 数据库操作、ClientDB、数据库触发器、Redis、URL化、定时触发等核心能力。基于 DCloud 官方文档，适用于 uni-app 开发者。"
provides:
  - capability: cloud-function
    methods: [callFunction, main]
  - capability: cloud-object
    methods: [importObject, getClientInfo, getCloudInfo, _before, _after, _timing]
  - capability: database
    methods: [add, get, update, remove, where, field, orderBy, limit, skip, count]
  - capability: db-schema
    methods: [permission, validator, foreignKey, parentKey, fieldRules, defaultValue, forceDefaultValue]
  - capability: jql
    methods: [where, field, orderBy, groupBy, getTree, getTreePath, geoNear, multiSend]
  - capability: clientdb
    methods: [databaseForJQL, unicloud-db-component]
  - capability: database-trigger
    methods: [beforeRead, afterRead, beforeCreate, afterCreate, beforeUpdate, afterUpdate, beforeDelete, afterDelete]
  - capability: redis
    methods: [get, set, del, hset, hget, lpush, rpush, sadd, smembers]
  - capability: url-trigger
    methods: [httpAccess, integrationResponse]
  - capability: timer-trigger
    methods: [cronTrigger]
  - capability: httpclient
    methods: [request, connectSocket]
---

# uniCloud Skill

uniCloud 是 DCloud 推出的 Serverless 云开发平台，深度集成 uni-app 生态。本 skill 覆盖云函数、云对象、数据库、JQL、ClientDB、数据库触发器、公共模块、URL化、定时触发、Redis、HTTP 请求等核心能力。

## When to use this skill

Use this skill whenever the user wants to:

- Set up or configure a uniCloud project / service space (including CLI projects)
- Create a new uniCloud project or integrate uniCloud into existing uni-app project
- Work with cloud databases (CRUD, queries, indexes, aggregation, transactions)
- Use JQL syntax to operate databases
- Create, deploy, or debug cloud functions or cloud objects
- Use clientDB to operate databases directly from the frontend
- Design or configure DB Schema (field types, validators, permissions, foreignKey, parentKey)
- Configure database triggers (schema.ext.js)
- Use cloud storage for file uploads, downloads, or management
- Configure URL access (HTTP triggers) for cloud functions/objects
- Set up timer triggers (cron jobs)
- Use Redis for caching or high-performance scenarios
- Make HTTP requests from cloud functions
- Implement uniCloud response format standards
- Handle cloud function permissions, security, or error handling
- Integrate uni-app frontend with uniCloud backend services
- Use `<unicloud-db>` component for data binding
- Use common modules to share code between cloud functions

## How to use this skill

1. **Start with the reference index below** to find the relevant module
2. **Open the corresponding reference file** in `references/` for detailed docs with code examples
3. **Check the provider differences table** when targeting specific cloud vendors (Alibaba Cloud, Tencent Cloud, Alipay Cloud)

### Reference Files

| Module | File | Description |
|--------|------|-------------|
| Quickstart | [references/quickstart.md](references/quickstart.md) | Project setup, CLI usage, first cloud object, web console tips |
| Cloud Function | [references/cloud-function.md](references/cloud-function.md) | Lifecycle, cold/hot start, invocation, recursion, concurrency, return policy |
| Cloud Object | [references/cloud-object.md](references/cloud-object.md) | this API, _before/_after/_timing, client invocation |
| Database Operations | [references/database.md](references/database.md) | CRUD, query/update commands, GEO, transactions |
| ClientDB | [references/clientdb.md](references/clientdb.md) | Frontend direct database access, unicloud-db component |
| DB Schema | [references/db-schema.md](references/db-schema.md) | Schema structure, field types, validators, permissions, foreignKey, parentKey |
| JQL Syntax | [references/jql.md](references/jql.md) | Query syntax, joins, tree queries, groupBy, multiSend |
| Database Triggers | [references/database-trigger.md](references/database-trigger.md) | schema.ext.js, trigger timings, action replacement |
| Common Modules | [references/common-module.md](references/common-module.md) | Shared code extraction and references |
| URL Access | [references/url-trigger.md](references/url-trigger.md) | HTTP access, integration response, cookies |
| Timer Triggers | [references/timer-trigger.md](references/timer-trigger.md) | Cron expressions, scheduled tasks |
| Redis | [references/redis.md](references/redis.md) | Data types, full API reference |
| HTTP Requests | [references/httpclient.md](references/httpclient.md) | httpclient, uniCloud.request, WebSocket |
| package.json | [references/package-json.md](references/package-json.md) | Cloud function config, runtime, extensions |

## Core Concepts

### Cloud Function vs Cloud Object vs ClientDB

| Feature | Cloud Function (callFunction) | Cloud Object (importObject) | ClientDB |
|---------|------------------------------|----------------------------|----------|
| Entry file | `index.js` | `index.obj.js` | Frontend direct call |
| Communication | `uniCloud.callFunction()` | `uniCloud.importObject()` | `uniCloud.databaseForJQL()` |
| Server code required | Yes | Yes | No (DB Schema permissions) |
| Recommendation | ⚠️ Not for new projects | ✅ Recommended | ✅ Best for DB operations |

### Decision Guide

1. **Pure database operations** → ClientDB (zero server code)
2. **Need server logic** (email, external API, complex computation) → Cloud Object
3. **Need URL access / timer triggers** → Cloud Object (HBuilderX 3.5.2+)
4. **Legacy projects** → Cloud Function (consider migrating to Cloud Object)

### Provider Differences

| Feature | Alibaba Cloud | Tencent Cloud | Alipay Cloud |
|---------|--------------|---------------|--------------|
| Default Node | Node 16 | Node 16 | Node 18 |
| Function limit | 99 | 149 | 499 |
| Min trigger interval | 1 min | 1 sec | 1 sec |
| Max trigger timeout | 600s | 900s | 3 hours |
| Timezone | UTC+0 | UTC+0 | UTC+8 |
| Instance recycle | 15 min | 30 min | 60 sec |

### uniCloud Response Format

```js
// Success
return { errCode: 0, errMsg: 'success', data: result }

// Error
return { errCode: 'uni-id-account-banned', errMsg: 'Account banned' }
```

- `errCode`: `0` for success, string for error (plugin market plugins must contain `-`)
- `errMsg`: Error description
- `newToken`: Optional, for token auto-renewal

### Common uniCloud APIs

| API | Description |
|-----|-------------|
| `uniCloud.database()` | Get database instance |
| `uniCloud.databaseForJQL()` | ClientDB frontend JQL query (recommended) |
| `uniCloud.databaseJQL()` | JQL in cloud functions (requires extension) |
| `uniCloud.redis()` | Use Redis (requires extension) |
| `uniCloud.uploadFile()` | Upload file to cloud storage |
| `uniCloud.downloadFile()` | Download from cloud storage |
| `uniCloud.deleteFile()` | Delete cloud storage file |
| `uniCloud.callFunction()` | Call another cloud function |
| `uniCloud.importObject()` | Import cloud object |
| `uniCloud.httpclient` | HTTP requests to external services |
| `uniCloud.sendSms()` | Send SMS (requires extension) |
| `uniCloud.init()` | Get specific service space instance |
| `uniCloud.logger` | Log to Web console |
| `uniCloud.getClientInfos()` | Get client info list |

## JQL Quick Reference

JQL (Javascript Query Language) is the recommended database query syntax for uniCloud.

```js
// Frontend query
const db = uniCloud.databaseForJQL()
const res = await db.collection('todos')
  .where('done == false && priority == "high"')
  .field('title, createTime as time')
  .orderBy('createTime desc')
  .limit(20)
  .get()

// Join query (requires schema foreignKey config)
const order = db.collection('order').where('uid == $cloudEnv_uid').getTemp()
const book = db.collection('book').field('_id, title').getTemp()
const res = await db.collection(order, book).get()

// Tree query (requires schema parentKey config)
const res = await db.collection('department').get({
  getTree: { limitLevel: 5, startWith: 'name == "HQ"' }
})

// Group statistics
const res = await db.collection('score')
  .groupBy('class')
  .groupField('count(*) as total, avg(score) as avg')
  .get()
```

> Full JQL syntax → [references/jql.md](references/jql.md)

## Best Practices

1. **Security**: Always configure DB Schema permissions. Never trust client-side data.
2. **Performance**: Use indexes for frequently queried fields. Prefer ClientDB over cloud functions for DB operations.
3. **Cost**: Optimize cloud function execution time. Merge low-frequency functions into high-frequency ones.
4. **Error handling**: Use `try/catch` or `.then/.catch` for all cloud operations. Follow uniCloud response format.
5. **Data validation**: Validate data in DB Schema validators, database triggers, or `_before` interceptors.
6. **Stateless**: Cloud functions are stateless. Use Redis for dynamic global variables, uni-config-center for static config.
7. **Code reuse**: Extract shared logic into common modules.
8. **Provider awareness**: Check provider differences when using timer triggers, URL access, or timezone-sensitive operations.

## Notes

- Cloud functions use CommonJS (`require`/`module.exports`), not `import`/`export`
- Same-name cloud functions in the same service space will overwrite each other
- Single cloud function size limit: **10MB** (including node_modules)
- Alibaba Cloud does not support relative file paths; use `path.resolve(__dirname, './file')`
- Cloud functions are **stateless**; global variables persist across requests during instance reuse
- Client-reported info can theoretically be tampered with; always validate

## Keywords

unicloud, uniCloud, 云开发, 云函数, 云对象, 云数据库, JQL, clientDB, 数据库触发器, Redis, URL化, 定时触发, 云存储, serverless, uni-app, DCloud, 公共模块, DB Schema, schema, foreignKey, parentKey, groupBy, getTree, permission, validator, bsonType, fieldRules, schema2code, openDB
