# 微信小程序服务端 API

**此非前端 API，请在云函数内调用。**

## 配置文件

打开 `uniCloud/cloudfunctions/common/uni-config-center/uni-id/config.json`，配置：

```json
{
  "mp-weixin": {
    "oauth": {
      "weixin": { "appid": "", "appsecret": "" }
    }
  },
  "app-plus": {
    "tokenExpiresIn": 604800,
    "oauth": {
      "weixin": { "appid": "", "appsecret": "" }
    }
  },
  "h5-weixin": {
    "oauth": {
      "weixin": { "appid": "", "appsecret": "" }
    }
  }
}
```

配置完需上传 `uni-config-center` 公共模块。

## 授权相关

### 获取 access_token（带缓存1小时）
```js
let access_token = await vk.openapi.weixin.auth.getAccessToken();
```

### code 换取 openid
```js
let res = await vk.openapi.weixin.auth.code2Session({ js_code });
// res.openid, res.session_key
```

### 获取微信绑定的手机号
```js
// 方式一：通过 code（推荐）
let res = await vk.openapi.weixin.decrypt.getPhoneNumber({ code });
// 方式二：通过 encryptedData + iv + sessionKey
let res = await vk.openapi.weixin.decrypt.getPhoneNumber({ encryptedData, iv, sessionKey });
```

### 获取小程序码（永久有效，数量无限制）
```js
let getUnlimitedRes = await vk.openapi.weixin.wxacode.getUnlimited({
  page: 'pages/index/index',
  scene: 'id=123',       // 最大32个可见字符
  check_path: false,     // false 允许 page 不存在
  env_version: 'develop', // release/trial/develop
  width: 430,            // 280-1280px
});
// 返回二进制，需转 base64
let base64 = Buffer.from(getUnlimitedRes, 'binary').toString('base64');
// → "data:image/png;base64,..."
```

### 获取 scheme 码
```js
let res = await vk.openapi.weixin.urlscheme.generate({
  jump_wxa: { path: 'pages/index/index', query: 'a=1', env_version: 'develop' },
  is_expire: true,
  expire_type: 1,
  expire_interval: 30, // 最大30天
});
// res.openlink
```

### 获取 URL Link
```js
let res = await vk.openapi.weixin.urllink.generate({
  path: 'pages/index/index',
  query: 'a=1&b=2',
  is_expire: true,
  expire_interval: 30,
});
// res.url_link
```

## 内容安全

### 检测文本
```js
let res = await vk.openapi.weixin.security.msgSecCheck({
  content: '要检测的文本',
  openid: '用户openid',
  scene: 3,    // 1资料 2评论 3论坛 4社交日志
  version: 2,  // 建议用 v2
});
```

### 检测图片
```js
let res = await vk.openapi.weixin.security.imgSecCheck({
  base64: base64String, // 图片 ≤ 1M
  openid: '用户openid',
  scene: 3,
  version: 2,
});
// V2 结果异步返回，需开启消息推送
```

## 订阅消息

### 发送订阅消息
```js
let res = await vk.openapi.weixin.subscribeMessage.send({
  touser: openid,
  template_id: '订阅模板ID',
  page: 'pages/index/index', // 不要 / 开头
  data: {
    character_string1: { value: '202103040830158485629163994677' },
    name2: { value: '中通快递' },
    thing6: { value: '商品名称' },
  },
  miniprogram_state: 'formal', // developer/trial/formal
});
```

前端需先订阅：
```js
uni.requestSubscribeMessage({ tmplIds: ['订阅模板ID'] });
```

常见错误码：
| 值 | 说明 |
|---|------|
| 40003 | openid 不正确 |
| 40037 | 模板 id 不正确 |
| 43101 | 用户拒绝接受消息 |
| 47003 | 模板参数不准确 |
| 41030 | page 路径不正确 |

### 公众号模板消息
```js
// 用小程序 openid 发公众号模板消息（需同主体+认证服务号+关注）
let res = await vk.openapi.weixin.uniformMessage.send({
  touser: openid,
  template_id: '模板ID',
  miniprogram: { appid: '', pagepath: 'pages/order/order?id=aaa' },
  data: {
    first: { value: '您的订单已发货', color: '#173177' },
    keyword1: { value: 'D201803111235825' },
  },
});
```

### 单独公众号模板消息
```js
let res = await vk.openapi.weixin.h5.templateMessage.send({
  touser: '公众号openid', // 只能是公众号 openid
  template_id: '模板ID',
  url: 'https://xxx.com',
  data: { ... },
});
```
