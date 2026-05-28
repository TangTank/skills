# JS API 文档大全

`vk.pubfn.` 可在 js 和 template 中使用（template 中可用简写 `$fn`）。
nvue 中用 `uni.vk.pubfn`，支付宝/百度/抖音小程序需在 script 首行加 `var vk = uni.vk;`

## 前后端通用

### 防抖/节流
```js
vk.pubfn.debounce(fn, time, isImmediate, timeoutName)
vk.pubfn.throttle(fn, time, isImmediate, timeoutName)
```

### 树操作
```js
// 数组转树
let treeData = vk.pubfn.arrayToTree(arrayData, { id: '_id', parent_id: 'parent_id', children: 'children' });
// 树转数组
let arrayData = vk.pubfn.treeToArray(treeData, { id: '_id', parent_id: 'parent_id', children: 'children' });
```

### 休眠
```js
await vk.pubfn.sleep(1000); // 毫秒
```

### 日期时间
```js
// 格式化
let str = vk.pubfn.timeFormat(new Date(), 'yyyy-MM-dd hh:mm:ss'); // → "2024-01-01 10:10:10"
let str = vk.pubfn.timeFormat(new Date(), 'yyyy年MM月dd日 hh时mm分ss秒');
let str = vk.pubfn.timeFormat(new Date(), 'yyyy-MM-dd hh:mm:ss.S'); // 带毫秒
let str = vk.pubfn.timeFormat(new Date(), 'yyyy-MM-ddThh:mm:ssZ', 8); // 指定时区

// 解析日期属性
let { year, month, day, hour, minute, second, week, quarter } = vk.pubfn.getDateInfo(new Date());

// 获取时间范围
let { todayStart, todayEnd, monthStart, monthEnd, yearStart, yearEnd, weekStart, weekEnd } = vk.pubfn.getCommonTime(new Date());

// 时间偏移
let timestamp = vk.pubfn.getOffsetTime(new Date(), { hour: 1, mode: 'after' });
let timestamp = vk.pubfn.getOffsetTime(new Date(), { day: 7, mode: 'before' });

// 获取指定日/周/月/季/年的起止
let { startTime, endTime } = vk.pubfn.getDayOffsetStartAndEnd(0);    // 今日
let { startTime, endTime } = vk.pubfn.getWeekOffsetStartAndEnd(-1);  // 上周
let { startTime, endTime } = vk.pubfn.getMonthOffsetStartAndEnd(0);  // 本月
let { startTime, endTime } = vk.pubfn.getQuarterOffsetStartAndEnd(0); // 本季度
let { startTime, endTime } = vk.pubfn.getYearOffsetStartAndEnd(0);   // 今年
```

### 校验
```js
vk.pubfn.test(str, type, allowEmpty);
// type: mobile/tel/card/email/money/url/ip/date/dateTime/number/english/chinese/username/pwd/paypwd/...
```

### 对象操作
```js
let newObj = vk.pubfn.objectAssign(obj1, obj2);    // 浅拷贝合并
let newObj = vk.pubfn.copyObject(obj);              // 复制对象（无映射）
let newObj = vk.pubfn.deepClone(obj);               // 深度克隆（支持函数）
let value = vk.pubfn.getData(dataObj, 'a.b.c[1].d', defaultValue); // 根据路径取值
vk.pubfn.setData(dataObj, 'a.b.c', value);          // 根据路径设值
```

### 空值检测
```js
vk.pubfn.isNull(value)           // undefined/null/{}/[]/"" → true
vk.pubfn.isNotNull(value)        // 结果与isNull相反
vk.pubfn.isNullOne(v1, v2, v3)   // 至少有一个为空
vk.pubfn.isNullAll(v1, v2, v3)   // 全部为空
vk.pubfn.isNotNullAll(v1, v2, v3) // 全部不为空
let nullKey = vk.pubfn.isNullOneByObject({ title, content }); // 返回首个空值的属性名
```

### 数组操作
```js
let arr = vk.pubfn.arr_concat(arr1, arr2, '_id');   // 合并去重
let item = vk.pubfn.getListItem(list, '_id', '001'); // 根据键值获取item
let index = vk.pubfn.getListIndex(list, '_id', '001');
let { item, index } = vk.pubfn.getListItemIndex(list, '_id', '001');
let obj = vk.pubfn.arrayToJson(list, '_id');          // 数组转JSON对象
let newList = vk.pubfn.arrayObjectGetArray(list, '_id'); // 提取指定字段成新数组
```

### 其他工具
```js
let n = vk.pubfn.random(6);                           // 6位随机数
let n = vk.pubfn.random(6, 'abcdefghijklmnopqrstuvwxyz0123456789'); // 指定字符范围
let newStr = vk.pubfn.hidden('15200000001', 3, 4);    // → "152****0001"
vk.pubfn.checkArrayIntersection(arr1, arr2);          // 两数组是否有交集
```

## 仅前端可用

### 页面跳转
```js
vk.navigateTo({ url: '/pages/xxx/xxx', query: { id: '1' } });
vk.redirectTo({ url: '/pages/xxx/xxx' });
vk.switchTab({ url: '/pages/index/index' });
vk.navigateBack();
```

### 弹窗
```js
vk.alert('提示');
vk.confirm('确认？').then(() => {}).catch(() => {});
vk.showToast('提示');
vk.showLoading('加载中...');
vk.hideLoading();
```

### 本地缓存（vk.localStorage）
```js
vk.localStorage.set('key', value);
let value = vk.localStorage.get('key');
vk.localStorage.remove('key');
vk.localStorage.clear();
```

### Vuex
```js
vk.setVuex('user.info', data);       // 设置
let info = vk.getVuex('user.info');  // 获取
```
