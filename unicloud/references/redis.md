# Redis 扩展库

> 2021年11月18日起，腾讯云和阿里云均支持

## 简介

Redis 是基于 key/value 的内存数据库，通常作为 MongoDB 等磁盘数据库的补充搭配使用。

**核心优势：** 快（内存操作）、不耗费云数据库读写次数。

## 常见场景

- 缓存高频数据（首页列表、banner、热门排行）
- 秒杀/抢购（防止超卖）
- IP 黑名单
- 其他数据库操作速度不满足需求的场景

## 开通与启用

1. 在 uniCloud 控制台开通 Redis 服务（需购买）
2. 在云函数目录右键 → 管理公共模块和扩展库依赖 → 选择 `uni-cloud-redis`

```js
// 使用方式
const redis = uniCloud.redis()
await redis.set('key', 'value')
const value = await redis.get('key')
```

> 调用 `uniCloud.redis()` 返回一个连接实例，多次调用时如存在未断开连接则复用。

## 数据类型

### String 字符串

最简单的类型，Redis 无 number 类型，number 存入后也会转为 string。

### List 列表

类似 JS 数组（基于链表实现），头部插入效率高。

> List 为空时对应键会被删除，Redis 内不存在空 List。

### Hash 哈希表

类似 JS Object。

### Set 集合

String 的无序排列，元素不可重复。

### SortedSet 有序集合

String 元素集合，不允许重复，每个元素有 double 类型分数用于排序。

### HyperLogLog 基数统计

统计集合中不重复元素的个数。

### Transaction 事务

一次执行多个命令。

### BitMap 位图

连续的二进制数组，通过偏移量定位元素。

## API

### String 操作

```js
const redis = uniCloud.redis()

// get — 获取
const value = await redis.get('key')  // 不存在返回 null

// set — 设置
await redis.set('key', 'value')                    // 基础设置
await redis.set('key', 'value', 'EX', 60)          // 60秒过期
await redis.set('key', 'value', 'PX', 60000)       // 60000毫秒过期
await redis.set('key', 'value', 'NX')              // 不存在时才设置
await redis.set('key', 'value', 'XX')              // 存在时才设置

// setex — 设置并指定过期时间（秒）
await redis.setex('key', 60, 'value')

// setnx — 不存在时设置
await redis.setnx('key', 'value')

// mget — 批量获取
const values = await redis.mget('key1', 'key2', 'key3')

// mset — 批量设置
await redis.mset('key1', 'v1', 'key2', 'v2')

// getrange — 截取子字符串
await redis.getrange('key', 0, -1)

// strlen — 字符串长度
await redis.strlen('key')

// incr / decr — 自增/自减
await redis.incr('counter')        // +1
await redis.incrby('counter', 5)   // +5
await redis.decr('counter')        // -1
await redis.decrby('counter', 3)   // -3

// incrbyfloat — 浮点数增减
await redis.incrbyfloat('price', 1.5)

// append — 追加
await redis.append('key', '-suffix')
```

### Key 操作

```js
// del — 删除
await redis.del('key')  // 返回 1 成功，0 不存在

// exists — 判断存在
await redis.exists('key')  // 返回 1 存在，0 不存在

// expire — 设置过期时间（秒）
await redis.expire('key', 60)

// ttl — 获取剩余过期时间（秒）
await redis.ttl('key')  // -1 永久，-2 不存在/已过期

// persist — 移除过期时间
await redis.persist('key')

// keys — 查找匹配的 key（支付宝云不支持，用 scan 替代）
const keys = await redis.keys('user:*')

// scan — 迭代 key（推荐）
const [cursor, result] = await redis.scan(0)

// rename — 改名
await redis.rename('old-key', 'new-key')

// type — 获取值类型
await redis.type('key')  // 'string' | 'list' | 'set' | 'zset' | 'hash' | 'none'
```

### List 操作

```js
// lpush / rpush — 头部/尾部追加
await redis.lpush('list', 'item')
await redis.rpush('list', 'item')

// lpop / rpop — 头部/尾部弹出
const item = await redis.lpop('list')
const item = await redis.rpop('list')

// llen — 长度
const len = await redis.llen('list')

// lrange — 范围查询
const items = await redis.lrange('list', 0, -1)  // 全部

// lindex — 按下标获取
const item = await redis.lindex('list', 0)

// lset — 按下标设置
await redis.lset('list', 0, 'new-value')

// linsert — 指定位置插入
await redis.linsert('list', 'BEFORE', 'pivot', 'new-item')

// lrem — 删除指定值
await redis.lrem('list', 1, 'item')  // count=1 从头开始

// ltrim — 修剪
await redis.ltrim('list', 0, 49)  // 保留前 50 个

// blpop / brpop — 阻塞弹出
const [key, value] = await redis.blpop('list', 5)  // 超时 5 秒
```

### Hash 操作

```js
// hset / hget — 设置/获取字段
await redis.hset('user', 'name', '张三')
const name = await redis.hget('user', 'name')

// hmset / hmget — 批量设置/获取
await redis.hmset('user', 'name', '张三', 'age', '25')
const [name, age] = await redis.hmget('user', 'name', 'age')

// hgetall — 获取全部
const all = await redis.hgetall('user')

// hdel — 删除字段
await redis.hdel('user', 'age')

// hexists — 判断字段存在
await redis.hexists('user', 'name')  // 1 存在，0 不存在

// hkeys / hvals — 获取所有字段/值
const fields = await redis.hkeys('user')
const values = await redis.hvals('user')

// hlen — 字段数量
await redis.hlen('user')

// hincrby — 字段自增
await redis.hincrby('user', 'age', 1)

// hsetnx — 不存在时设置
await redis.hsetnx('user', 'email', 'x@x.com')
```

### Set 操作

```js
// sadd — 添加成员
await redis.sadd('tags', 'js', 'node', 'uniapp')

// smembers — 获取所有成员
const members = await redis.smembers('tags')

// sismember — 判断成员存在
await redis.sismember('tags', 'js')  // 1 存在，0 不存在

// scard — 成员数量
await redis.scard('tags')

// srem — 删除成员
await redis.srem('tags', 'js')

// sdiff / sinter / sunion — 差集/交集/并集
const diff = await redis.sdiff('set1', 'set2')
const inter = await redis.sinter('set1', 'set2')
const union = await redis.sunion('set1', 'set2')

// smove — 移动成员
await redis.smove('source', 'dest', 'member')
```

## 注意事项

- Redis key 以冒号分隔（如 `user:123`），控制台会以 tree 方式显示
- 避免使用 `uni:`、`dcloud:`、`unicloud:` 前缀（官方保留）
- Redis 在云函数内网中，只能在云端访问（HBuilderX 3.4.10+ 支持本地通过代理访问）
- 开启 Redis 扩展会影响云函数固定 IP 功能
- 腾讯云 node12+ 使用 Redis 时注意 `keepRunningAfterReturn` 配置
- 使用完毕后断开连接：`redis.quit()`

## 计费

Redis 按容量和使用时长计费，访问不耗费云数据库读写次数。
