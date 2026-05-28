# vk.userCenter 用户中心 API

**仅适用于前端使用，无法在云函数中使用。**

nvue/支付宝/百度小程序需用 `uni.vk` 替代 `vk`，或在 script 首行加 `var vk = uni.vk;`

## 公共请求参数

| 参数 | 说明 | 类型 |
|------|------|------|
| data | 发送到云函数的参数 | Object |
| title | 遮罩层提示语 | String |
| loading | 自定义 loading | Boolean/Object |
| needAlert | 请求错误时是否弹窗，默认 true | Boolean |
| success | 成功回调 | Function |
| fail | 失败回调 | Function |
| complete | 完成回调 | Function |

## 监听

### vk.onRefreshToken（监听 token 更新）

```js
// App.vue 全局监听
onLaunch() {
  uni.vk.onRefreshToken((data) => {
    if (data.token) console.log('token更新', data);
    else console.log('token失效', data);
  });
}
```

### vk.offRefreshToken（移除监听）

```js
onUnload() {
  uni.vk.offRefreshToken(this.onRefreshToken);
}
```

## 通用 API

### vk.userCenter.register（注册）
```js
vk.userCenter.register({
  data: { username: '', password: '' },
  success: (data) => { /* data.token, data.userInfo, data.uid */ },
});
```

### vk.userCenter.login（登录）
```js
vk.userCenter.login({
  data: { username: '', password: '' },
  success: (data) => {},
});
```

### vk.userCenter.updatePwd（修改密码）
```js
vk.userCenter.updatePwd({
  data: { oldPassword: '123456', newPassword: '654321', password_confirmation: '654321' },
  success: (data) => {},
});
```

### vk.userCenter.logout（登出）
```js
vk.userCenter.logout({ success: (data) => {} });
```

### vk.userCenter.resetPwd（重置密码）
```js
vk.userCenter.resetPwd({ data: { password: '123456' }, success: (data) => {} });
```

### vk.userCenter.setAvatar（设置头像）
```js
vk.userCenter.setAvatar({
  data: { avatar: 'https://xxx/1.jpg', deleteOldFile: false },
  success: (data) => {},
});
```

### vk.userCenter.updateUser（设置昵称等）
```js
vk.userCenter.updateUser({
  data: { nickname: '昵称' },
  success: (data) => {},
});
```

### vk.userCenter.getCurrentUserInfo（获取用户信息）
```js
vk.userCenter.getCurrentUserInfo({
  loading: false,
  success: (data) => { /* data.userInfo */ },
});
```

### vk.userCenter.loginByToken（刷新 token，每日登录统计）
```js
vk.userCenter.loginByToken(); // 一天内重复调用只有第一次生效
```

### vk.checkToken（本地校验，无网络请求）
```js
if (!vk.checkToken()) {
  // 未登录
} else {
  // 已登录
}
```

### vk.getToken / vk.saveToken / vk.deleteToken
```js
let token = vk.getToken();
vk.saveToken({ token: 'xxx', tokenExpired: timestamp });
vk.deleteToken();
```

### vk.handleAutoLoginToken（跨应用无感登录）
写在 App.vue 的 onLaunch 第一行：
```js
onLaunch(options) {
  uni.vk.handleAutoLoginToken(options);
}
```

### vk.userCenter.closeAccount（账号注销，需 ≥ 2.20.0）
首次注销有 7 天冷静期，可通过 openAccount 恢复。

### vk.userCenter.getCoolingStatus（获取注销冷静期状态）
```js
vk.userCenter.getCoolingStatus({
  success: (res) => {
    console.log(res.status);       // 4=已注销
    console.log(res.duration);     // 冷静期剩余时长(ms)
  },
});
```

## 手机号相关

### vk.userCenter.bindMobile / unbindMobile / bindNewMobile
```js
vk.userCenter.bindMobile({ data: { mobile: '', code: '' }, success: (data) => {} });
vk.userCenter.unbindMobile({ data: { mobile: '', code: '' }, success: (data) => {} });
vk.userCenter.bindNewMobile({ data: { oldMobile: '', oldMobileCode: '', mobile: '', code: '' }, success: (data) => {} });
```

### vk.userCenter.loginBySms（手机号登录）
```js
vk.userCenter.loginBySms({
  data: { mobile: '', code: '', type: 'login' }, // type: login/register/不传
  success: (data) => {},
});
```

### vk.userCenter.sendSmsCode（发送验证码）
```js
vk.userCenter.sendSmsCode({
  data: { mobile: '', type: 'login' }, // type: login/register/bind/unbind/reset-pwd
  success: (data) => {},
});
```

### vk.userCenter.resetPasswordByMobile（手机验证码重置密码）
```js
vk.userCenter.resetPasswordByMobile({
  data: { password: '123456', code: '', mobile: '' },
  success: (data) => {},
});
```

### vk.userCenter.loginByUniverify（APP 一键登录）
仅 APP 端可用，配合 `univerifyStyle` 自定义样式。

## 邮箱相关

### vk.userCenter.bindEmail / unbindEmail / bindNewEmail
```js
vk.userCenter.bindEmail({ data: { email: '', code: '' }, success: (data) => {} });
```

### vk.userCenter.loginByEmail（邮箱登录）
```js
vk.userCenter.loginByEmail({
  data: { email: '', code: '', type: 'login' },
  success: (data) => {},
});
```

### vk.userCenter.sendEmailCode（发送邮箱验证码）
```js
vk.userCenter.sendEmailCode({
  data: { email: '', type: 'login' },
  success: (data) => {},
});
```

## 微信登录

### vk.userCenter.loginByWeixin（微信登录）
```js
vk.userCenter.loginByWeixin({
  data: { inviteCode: '' },
  success: (data) => {},
});
```

### vk.userCenter.loginByWeixinPhoneNumber（微信手机号快速验证）
```js
vk.userCenter.loginByWeixinPhoneNumber({
  data: { encryptedData: '', iv: '' },
  success: (data) => {},
});
```

## Token 介绍

- 框架自动保存 token，无需手动操作
- kh 目录下的云函数自动校验 token 并获取 uid/userInfo
- pub 目录下传 `need_user_info: true` 可获取 userInfo
- token 过期后自动清除本地登录态
