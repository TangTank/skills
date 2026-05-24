# 公共模块 (Common Module)

## 简介

云函数支持公共模块。多个云函数/云对象的共享部分可以抽离为公共模块，被多个云函数引用。

## 目录结构

```
cloudfunctions/
├── common/
│   └── hello-common/          # 公共模块
│       ├── index.js           # 入口文件
│       └── package.json       # 配置（不要修改 name 字段）
├── function-a/
│   ├── index.js
│   └── package.json
└── function-b/
    ├── index.js
    └── package.json
```

## 创建步骤

1. 在 `cloudfunctions` 目录下创建 `common` 目录
2. 在 `common` 目录右键创建公用模块目录（如 `hello-common`），自动创建 `index.js` 和 `package.json`
3. 在 `hello-common` 右键上传公用模块
4. 在云函数上右键选择「管理公共模块依赖」，添加依赖

## 使用方式

### 公共模块导出

```js
// common/hello-common/index.js

// 方式一：导出对象
module.exports = {
  sayHello(name) {
    return `Hello, ${name}!`
  },
  formatDate(date) {
    return date.toISOString()
  }
}

// 方式二：仅导出一个函数
module.exports = function(name) {
  return `Hello, ${name}!`
}
```

### 云函数中引用

```js
// function-a/index.js
const helloCommon = require('hello-common')

exports.main = async (event, context) => {
  const greeting = helloCommon.sayHello('uniCloud')
  return greeting
}
```

### 公共模块嵌套引用

公共模块可以引用其他公共模块：

```js
// common/utils/index.js
const base = require('base-utils')
module.exports = {
  ...base,
  customUtil() { /* ... */ }
}
```

## 更新依赖

更新所有依赖某公共模块的云函数：在 `common` 目录下的公共模块目录右键选择「更新依赖本模块的云函数」。

## 注意事项

- 公共模块命名**不可与 Node.js 内置模块重名**
- 从插件市场导入可能导致 npm 软链接失效，需删除 `node_modules` 和 `package-lock.json` 重新 `npm install`
- 公共模块通过 `exports` 导出，云函数通过 `require` 引用
