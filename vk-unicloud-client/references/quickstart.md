# 快速上手 - 安装步骤

> 下载地址：https://ext.dcloud.net.cn/plugin?id=2204

## 后端（云端）安装步骤

`uniCloud` 目录为云端目录（此目录内的文件不会被打包到前端）

1. 右键 `uniCloud` 目录，再点击【云服务空间初始化向导】
2. 等待初始化完成

**注意：**
- 开发微信小程序和 APP 微信登录需要额外配置 `manifest.json` 以及 `uniCloud/cloudfunctions/common/uni-config-center/uni-id/config.json`，改动配置后需重新上传公共模块和 router 函数。
- 需要安装 Node.js

## 前端（页面）安装步骤

### Vue2.0 版本

`main.js` 引入 vk 框架：

```js
import Vue from 'vue';
import App from './App';
import store from './store';
import config from '@/app.config.js';

// 引入 vk框架前端
import vk from './uni_modules/vk-unicloud';
Vue.use(vk);

// 初始化 vk框架
Vue.prototype.vk.init({
  Vue,
  config,
});

Vue.config.productionTip = false;
App.mpType = 'app';
const app = new Vue({ store, ...App });
app.$mount();
```

### Vue3.0 版本

```js
import App from './App';
import store from './store';
import config from '@/app.config.js';
import vk from './uni_modules/vk-unicloud';
import { createSSRApp } from 'vue';

export function createApp() {
  const app = createSSRApp(App);
  app.use(store);
  app.use(vk);
  app.config.globalProperties.vk.init({
    Vue: app,
    config,
  });
  return { app };
}
```

### UI 组件库集成

自 client 端框架 2.6.0 起，不再内置任何 UI 框架，可选择：

- **vk-uview-ui**（推荐，vue2/vue3 均支持）：https://ext.dcloud.net.cn/plugin?id=6692
- **tmui**（支持 nvue）：vue2 版 https://ext.dcloud.net.cn/plugin?id=5949 / vue3 版 https://ext.dcloud.net.cn/plugin?id=8372
- **uview-ui**（nvue2.0）：https://ext.dcloud.net.cn/plugin?id=1593

集成 vk-uview-ui（vue2）步骤：
1. `main.js` 引入：`import uView from './uni_modules/vk-uview-ui'; Vue.use(uView);`
2. `App.vue` 样式：`<style lang="scss">@import './uni_modules/vk-uview-ui/index.scss';</style>`
3. `uni.scss` 引入：`@import '@/uni_modules/vk-uview-ui/theme.scss';`
