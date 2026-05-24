# 快速上手 (Quickstart)

## Hello uniCloud 示例

官方示例，演示 uniCloud 各种能力。

- 源码：[插件市场 #4082](https://ext.dcloud.net.cn/plugin?id=4082)
- H5 演示（支付宝云）：https://hellounicloud.dcloud.net.cn/alipay/
- H5 演示（阿里云）：https://hellounicloud.dcloud.net.cn/
- H5 演示（腾讯云）：https://hellounicloud.dcloud.net.cn/tcb/

## 创建 uniCloud 项目

### 方式一：新建项目（推荐）

1. HBuilderX → 新建项目 → 选择 uni-app → **勾选启用 uniCloud**
2. 选择服务供应商（支付宝云 / 阿里云 / 腾讯云）
3. 项目创建后弹出 **uniCloud 初始化向导**
4. 创建/选择服务空间
5. 按向导上传云函数、数据库 schema，执行 db_init 初始化

> 初次体验推荐**支付宝云或阿里云**（有免费开发者版空间）。推荐 Vue3 版本（编译更快）。

### 方式二：现有 uni-app 项目集成

1. 导入项目至 HBuilderX
2. 项目根目录右键 → 创建 uniCloud 云开发环境
3. uniCloud 目录右键 → 关联服务空间
4. uniCloud 目录右键 → 初始化向导 → 上传云函数和 schema

### 方式三：CLI 项目

1. 将 CLI 项目导入 HBuilderX
2. 打开 `src/manifest.json` → 基础配置 → 重新获取 AppID
3. 项目根目录（src 同级）右键 → 创建 uniCloud 云开发环境
4. uniCloud 目录右键 → 关联服务空间

> 注意：
> - 运行与发行云函数只能使用 HBuilderX 菜单
> - uniCloud 对安全性要求极高，仅支持 HBuilderX 开发
> - HBuilderX 也支持 CLI：https://hx.dcloud.net.cn/cli/README

## 第一个云对象

```js
// uniCloud/cloudfunctions/helloco/index.obj.js
module.exports = {
  async sum(a, b) {
    return a + b
  }
}
```

```vue
<!-- 前端调用 -->
<script setup>
import helloco from '@/uniCloud/cloudfunctions/helloco/index.obj.js'

async function handleClick() {
  const res = await helloco.sum(1, 2)
  console.log(res) // 3
}
</script>
```

## 服务空间

- 一个开发者可拥有多个服务空间，每个是独立的 Serverless 云环境
- 不同服务空间之间的云函数、数据库、存储**完全隔离**
- 支付宝云 / 阿里云：每账号可有 1 个免费开发者版空间（仅测试）
- 腾讯云：无免费空间
- 首次创建支付宝云需支付宝扫码授权

## Web 控制台

地址：https://unicloud.dcloud.net.cn

### 编辑数据库特殊类型

#### 添加日期

在 Web 控制台输入 `"2020-12-02 12:12:12"` 会变成**字符串**而非日期。正确方式：

```json
{
  "createTime": {
    "$date": "2020-12-02T12:12:12.000Z"
  }
}
```

> 时间戳无需特殊处理，直接输入不加引号的数字即可。

#### 添加地理位置点

```json
{
  "location": {
    "type": "Point",
    "coordinates": [116.397428, 39.90923]
  }
}
```

## 项目结构

```
project/
├── uniCloud/
│   ├── cloudfunctions/          # 云函数目录
│   │   ├── common/              # 公共模块
│   │   ├── function-name/       # 云函数
│   │   │   ├── index.js
│   │   │   └── package.json
│   │   └── object-name/         # 云对象
│   │       ├── index.obj.js
│   │       └── package.json
│   └── database/                # 数据库目录
│       ├── table.schema.json    # 表 Schema
│       ├── table.schema.ext.js  # Schema 扩展（触发器）
│       ├── table.init_data.json # 初始化数据
│       ├── table.index.json     # 索引配置
│       └── validateFunction/    # 扩展校验函数
└── pages/                       # 前端页面
```
