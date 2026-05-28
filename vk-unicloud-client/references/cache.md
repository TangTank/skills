# 云端数据缓存（新版）

需 vk-unicloud ≥ 2.18.1

## 介绍

通过 key-value 键值对进行数据存储，支持空间内置数据库和 Redis 数据库，可自由切换。

特性：分布式缓存（同云空间不同云函数共享）、有效期设置、丰富的 API。

## 初始化

```js
const cacheManage = vk.getCacheManage();
// 指定存储模式
const cacheManage = vk.getCacheManage({ mode: 'db' });    // 空间内置数据库
const cacheManage = vk.getCacheManage({ mode: 'redis' });  // Redis 数据库
```

配置文件 `uni-config-center/vk-unicloud/index.js`：
```js
"cacheManage": { "mode": "db" }  // 或 "redis"
```

## API

### get（获取缓存）
```js
let value = await cacheManage.get(key);
```

### set（设置缓存）
```js
await cacheManage.set(key, value, second); // second=0 永不过期
// 返回 { code: 0, msg, mode: 'add'|'update', key }
```

### setnx（不存在才设置）
```js
let res = await cacheManage.setnx(key, value, second);
```

### del（删除缓存）
```js
let count = await cacheManage.del(key);
```

### clear（清空缓存）
```js
let count = await cacheManage.clear(prefix); // 按前缀清空
```

### count（获取缓存数量）
```js
let count = await cacheManage.count(prefix);
```

### exists（判断缓存是否存在）
```js
let exists = await cacheManage.exists(key); // 1=存在 0=不存在
```

### expire（修改过期时间）
```js
let res = await cacheManage.expire(key, seconds); // 1=成功 0=失败
```

### ttl（获取剩余过期秒数）
```js
let seconds = await cacheManage.ttl(key);
```

### pttl（获取剩余过期毫秒数）
```js
let ms = await cacheManage.pttl(key);
```

## 注意

- 以上 API 均只能在云端运行
- 前端本地缓存使用 `vk.localStorage` 或 `vuex`
