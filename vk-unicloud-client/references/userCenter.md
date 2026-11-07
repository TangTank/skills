# vk.userCenter 用户中心 API

**下述 `vk.userCenter` API 仅适用于前端，无法在云函数中使用；文末 H5 登录排查同时涉及前后端配置。**

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

## H5 账号密码登录排查

适用于 vk + uni-id 项目提示“服务未配置 / 服务尚未配置”、返回 `CONFIGURATION`，或账号密码在提交前被长度校验拦截。先区分配置加载、服务空间连接、业务校验和真实凭据验证，避免把所有失败都当成密码错误。

### 1. 补齐真实的 uni-id 私有配置

- 常见源码路径为 `src/uni_modules/uni-config-center/uniCloud/cloudfunctions/common/uni-config-center/uni-id/config.json`。实际位置以当前项目结构为准，只有 `config.example.json` 不足以完成认证。
- 核对 `dcloudAppid` 与 manifest 源配置一致；H5 按当前 SDK 的平台选择规则配置 `preferedWebPlatform`（本次验证值为 `"h5"`），不要把其他项目的 AppID、云空间或微信配置整体复制过来。
- 已有账号的密码摘要依赖原 `passwordSecret`，配置缺失时应找回与这些账号兼容的密钥；只有明确沿用同一批账号及密码摘要时，参考配置中的密码密钥才可能适用。新账号空间使用独立密钥。
- `tokenSecret` 与密码密钥分开管理；补建配置时使用本项目独立值，已有运行空间则保留现有值。不要为解决配置加载失败而随意轮换密钥、重置账号密码或改变角色。
- `config.json` 应保存在 Git 忽略的私有配置中，不在技能、日志或示例里记录实际密钥。

### 2. 补齐认证公共模块的本地依赖

配置文件存在但本地 SDK 仍加载失败时，检查 `uni-id`、`uni-id-common` 声明的 `uni-config-center` 等依赖是否可被 Node 正常解析。对于源码位于 `src/uni_modules/` 的项目，可在项目根目录执行：

```powershell
npm install --prefix src/uni_modules/uni-id/uniCloud/cloudfunctions/common/uni-id --ignore-scripts --package-lock=false --no-audit --no-fund
npm install --prefix src/uni_modules/uni-id-common/uniCloud/cloudfunctions/common/uni-id-common --ignore-scripts --package-lock=false --no-audit --no-fund
```

其他目录布局先调整路径。无需为此改写 SDK 源码、替换认证实现或升级全项目依赖。

### 3. 用 HBuilderX 启动并核对云端部署

- 对依赖 HBuilderX 注入 uniCloud 服务空间的项目，从 HBuilderX 启动 H5；普通 Vite 服务能打开页面，不能证明空间配置已注入。补齐配置或依赖后重启旧 H5 和本地云函数调试进程。
- 可使用已确认安装位置的 HBuilderX CLI。以下变量分别取实际 CLI 路径及 HBuilderX 中的项目名：

```powershell
& $hbuilderCli launch web --project $projectName --browser Built
```

- 在当前任务授权的目标空间同步 `uni-config-center`、受影响的认证公共模块及 `router`；确认应用实际请求的空间与部署目标一致，不因参考 TopService 而改用其业务空间。
- CLI 下载或上传公共模块可能使用根目录 `uni_modules/`，而真实源码在 `src/uni_modules/`。核对实际打包位置和云端配置内容，不能只凭上传成功判断真实配置已包含；临时部署副本在核验后清理，不加入 Git。

### 4. 前后端密码策略保持一致

仅当用户明确要求取消“至少 8 位”时，同时检查登录页、管理员设置密码表单、登录云接口及设置密码云接口的校验与提示。HeidiEnglish 本次采用“密码非空白、最多 128 位”；这属于该项目要求，不是 vk 框架的统一默认规则。

使用 `trim()` 判断是否全为空白，但将原密码交给标准认证 SDK，避免改变有效密码。保留账号必填、错误凭据拒绝、管理员授权、密码加密和修改后的会话撤销。

### 5. 分层验证与清理

- 用不存在的测试账号确认请求已进入账号校验。本次 SDK 返回 `10002`，且不再返回 `CONFIGURATION`；这证明配置加载和认证调用已恢复，不代表正式账号登录成功。其他版本需按实际错误码含义判断。
- 正式账号由用户输入密码验证成功；不要为调试索要或打印明文密码，也不要直接输出包含登录参数的 HBuilderX 云函数日志。诊断只保留脱敏错误类型和错误码，完成后删除临时参数及诊断代码。
- 调整长度规则时覆盖短密码、边界长度、空白、超长、错误密码及既有会话行为；本次覆盖 1、7、8、128 位与 129 位拒绝，28 项回归、修改文件 ESLint 和类型检查通过。账号密码登录结果与微信 code 登录、设备验收分别记录。

本节来自 2026-10-22 HeidiEnglish 对照 TopService 的实际修复：补齐私有配置及本地依赖、从 HBuilderX 启动、同步目标空间配置与 router，再取消前后端 8 位下限后，用户确认账号密码登录成功。迁移时复用排查顺序，按目标项目实际身份、凭据来源和密码规则执行。
