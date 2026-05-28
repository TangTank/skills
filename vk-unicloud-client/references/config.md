# app.config.js 参数说明

## 完整配置示例

```js
import myPubFunction from "@/common/function/myPubFunction.js";
export default {
  // 开发模式启用调试（请求时打印日志）
  debug: process.env.NODE_ENV !== "production",
  // 主云函数名称
  functionName: "router",
  // 登录页面路径
  login: { url: "/pages_template/uni-id/login/index/index" },
  // 首页路径
  index: { url: "/pages/index/index" },
  // 404 页面路径
  error: { url: "/pages/error/404/404" },
  // 前端默认时区（中国为8）
  targetTimezone: 8,
  // 日志风格
  logger: { colorArr: ["#0095f8", "#67C23A"] },
  // 主题颜色（可通过 vk.getVuex('$app.config.color.main') 获取）
  color: { main: "#ff4444", secondary: "#555555" },

  // 需要检查登录的页面列表
  checkTokenPages: {
    // mode=0 自动检测, mode=1 list内需登录, mode=2 list内不需登录
    mode: 2,
    list: ["/pages_template/*", "/pages/login/*", "/pages/index/*", "/pages/error/*"],
    // 注意：list 内是通配符表达式，非正则
    // 需用 vk.navigateTo 代替 uni.navigateTo 才生效
  },

  // 需要检查分享的页面列表（仅小程序）
  checkSharePages: {
    mode: 0, // 0=不处理, 1=list内可分享, 2=list内不可分享
    menus: ["shareAppMessage"],
    list: ["/pages/index/*", "/pages/goods/*"],
  },

  // 需要加密通信的云函数
  checkEncryptRequest: {
    mode: 1, // 0=不处理, 1=list内需要加密
    list: [
      "^template/test/pub/testEncryptRequest$",
      "^template/encrypt/(.*)",
    ],
  },

  // 静态资源 URL
  staticUrl: { logo: "/static/logo.png" },

  // 自定义公共函数（通过 vk.myfn.xxx() 调用）
  myfn: myPubFunction,

  // 第三方服务配置
  service: {
    cloudStorage: {
      defaultProvider: "unicloud", // unicloud/extStorage/aliyun
      unicloud: {},
      extStorage: {
        provider: "qiniu",
        dirname: "public",
        authAction: "user/pub/getUploadFileOptionsForExtStorage",
        domain: "",
        groupUserId: false,
      },
      aliyun: {
        uploadData: { OSSAccessKeyId: "", policy: "", signature: "" },
        action: "https://xxx.oss-cn-hangzhou.aliyuncs.com",
        dirname: "public",
        host: "https://xxx.xxx.com",
        groupUserId: false,
      },
    },
  },

  // 全局异常码自定义
  globalErrorCode: {
    "cloudfunction-unusual-timeout": "请求超时，但请求还在执行",
    "cloudfunction-timeout": "请求超时，请重试！",
    "cloudfunction-system-error": "网络开小差了！",
    "cloudfunction-reaches-burst-limit": "系统繁忙，请稍后再试。",
  },

  // 自定义拦截器
  interceptor: {
    // login: function(obj) { ... },
    // fail: function(obj) { return false; } // 返回false取消框架内置fail逻辑
  },
};
```

## 配置注入 Vuex

config 已注入 vuex，可通过以下方式获取：
```js
vk.getVuex('$app.config')           // 获取完整配置（不含函数）
vk.getVuex('$app.config.color.main') // 获取主色
```
