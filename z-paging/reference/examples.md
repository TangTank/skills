# z-paging Code Examples

## 基本使用 (Vue2 选项式API)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>

<script>
export default {
  data() {
    return { dataList: [] };
  },
  methods: {
    async queryList(pageNo, pageSize) {
      try {
        const res = await uni.request({
          url: '/api/list',
          data: { pageNo, pageSize }
        });
        this.$refs.paging.complete(res.data.list);
      } catch (e) {
        this.$refs.paging.complete(false);
      }
    }
  }
};
</script>
```

## 基本使用 (Vue3 组合式API)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>

<script setup>
import { ref } from 'vue';

const paging = ref(null);
const dataList = ref([]);

const queryList = async (pageNo, pageSize) => {
  try {
    const res = await uni.request({
      url: '/api/list',
      data: { pageNo, pageSize }
    });
    paging.value.complete(res.data.list);
  } catch (e) {
    paging.value.complete(false);
  }
};
</script>
```

## 使用fetch极简写法 (v2.7.8+)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" :fetch="queryList" :fetch-params="{ type: tabIndex + 1 }">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>

<script>
import { queryList } from '../../http/request.js';

export default {
  data() {
    return { queryList, dataList: [], tabIndex: 0 };
  }
};
</script>
```

## 延迟加载列表 (先获取tabs再加载)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" :auto="false" @query="queryList">
    <!-- tabs -->
    <scroll-view scroll-x>
      <view v-for="(tab, i) in tabList" :key="i" @click="tabChange(i)">{{ tab.name }}</view>
    </scroll-view>
    <!-- list -->
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>

<script>
export default {
  data() {
    return { tabList: [], dataList: [] };
  },
  onLoad() {
    this.loadTabs();
  },
  methods: {
    async loadTabs() {
      const res = await uni.request({ url: '/api/tabs' });
      this.tabList = res.data;
      this.$refs.paging.reload(); // tabs加载完后触发列表
    },
    async queryList(pageNo, pageSize) {
      const res = await uni.request({
        url: '/api/list',
        data: { pageNo, pageSize, tab: this.tabList[this.currentTab].id }
      });
      this.$refs.paging.complete(res.data.list);
    }
  }
};
</script>
```

## 仅使用下拉刷新

```vue
<template>
  <z-paging ref="paging" refresher-only @onRefresh="onRefresh">
    <view>页面内容</view>
  </z-paging>
</template>

<script>
export default {
  methods: {
    onRefresh() {
      setTimeout(() => {
        this.$refs.paging.complete();
      }, 1500);
    }
  }
};
</script>
```

## 本地分页

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>

<script>
export default {
  data() { return { dataList: [] }; },
  methods: {
    async queryList() {
      const res = await uni.request({ url: '/api/all-data' });
      this.$refs.paging.setLocalPaging(res.data.list);
    }
  }
};
</script>
```

## 数据缓存

```vue
<template>
  <z-paging ref="paging" v-model="dataList" use-cache cache-key="goodsList" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>
```

## 自定义下拉刷新view

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <template #refresher="{ refresherStatus }">
      <view class="custom-refresher">
        <text v-if="refresherStatus === 'default'">下拉刷新</text>
        <text v-else-if="refresherStatus === 'release-to-refresh'">松手刷新</text>
        <text v-else-if="refresherStatus === 'loading'">刷新中...</text>
        <text v-else-if="refresherStatus === 'complete'">刷新成功</text>
      </view>
    </template>
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>
```

## 自定义加载更多状态

```vue
<template>
  <z-paging ref="paging" v-model="dataList" loading-more-no-more-text="我也是有底线的！" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <view class="item-title">{{ item.title }}</view>
    </view>
  </z-paging>
</template>
```

## 虚拟列表

```vue
<template>
  <z-paging ref="paging" v-model="dataList" use-virtual-list @query="queryList">
    <template #cell="{ item, index }">
      <view class="item">
        <text>{{ item.title }}</text>
      </view>
    </template>
  </z-paging>
</template>

<script>
export default {
  data() { return { dataList: [] }; },
  methods: {
    async queryList(pageNo, pageSize) {
      const res = await uni.request({ url: '/api/list', data: { pageNo, pageSize } });
      this.$refs.paging.complete(res.data.list);
    }
  }
};
</script>
```

## 虚拟列表 - 动态高度 + 非内置列表写法 (Vue3推荐)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" use-virtual-list cell-height-mode="dynamic" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <text>{{ item.title }}</text>
    </view>
  </z-paging>
</template>
```

## 聊天记录模式

```vue
<template>
  <z-paging ref="paging" v-model="chatList" use-chat-record-mode @query="queryChatList">
    <template #cell="{ item }">
      <view class="chat-bubble" :class="{ 'chat-bubble-mine': item.isMine }">
        <text>{{ item.content }}</text>
      </view>
    </template>
    <template #bottom>
      <view class="chat-input-bar">
        <input v-model="inputText" />
        <button @click="send">发送</button>
      </view>
    </template>
  </z-paging>
</template>

<script>
export default {
  data() { return { chatList: [], inputText: '' }; },
  methods: {
    async queryChatList(pageNo, pageSize) {
      const res = await uni.request({ url: '/api/chat', data: { pageNo, pageSize } });
      this.$refs.paging.complete(res.data.list);
    },
    send() {
      const newMsg = { content: this.inputText, isMine: true };
      this.$refs.paging.addChatRecordData(newMsg);
      this.inputText = '';
    }
  }
};
</script>
```

## 下拉进入二楼 (v2.7.7+)

```vue
<template>
  <z-paging ref="paging" v-model="dataList" refresher-f2-enabled @query="queryList">
    <template #refresherF2>
      <view class="f2-hint">
        <text>松手可以进入二楼哦 (*╹▽╹*)</text>
      </view>
    </template>
    <template #f2>
      <second-floor @close="onCloseF2" />
    </template>
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <text>{{ item.title }}</text>
    </view>
  </z-paging>
</template>

<script>
export default {
  methods: {
    onCloseF2() {
      this.$refs.paging.closeF2();
    }
  }
};
</script>
```

## 页面滚动模式

```vue
<template>
  <z-paging ref="paging" v-model="dataList" :use-page-scroll="true" @query="queryList">
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <text>{{ item.title }}</text>
    </view>
  </z-paging>
</template>

<script>
import ZPMixins from '@/uni_modules/z-paging/components/z-paging/js/z-paging-mixins';

export default {
  mixins: [ZPMixins],
  data() { return { dataList: [] }; },
  methods: {
    async queryList(pageNo, pageSize) {
      const res = await uni.request({ url: '/api/list', data: { pageNo, pageSize } });
      this.$refs.paging.complete(res.data.list);
    }
  }
};
</script>
```

## 在弹窗中使用 (非fixed布局)

```vue
<template>
  <view class="popup" v-if="show">
    <view class="popup-content" style="height: 600rpx;">
      <z-paging ref="paging" :fixed="false" v-model="dataList" @query="queryList">
        <view class="item" v-for="(item, index) in dataList" :key="index">
          <text>{{ item.title }}</text>
        </view>
      </z-paging>
    </view>
  </view>
</template>
```

## 带顶部tabs的列表

```vue
<template>
  <z-paging ref="paging" v-model="dataList" @query="queryList">
    <template #top>
      <view class="tabs">
        <view v-for="(tab, i) in tabs" :key="i"
              :class="{ active: currentTab === i }"
              @click="switchTab(i)">
          {{ tab.name }}
        </view>
      </view>
    </template>
    <view class="item" v-for="(item, index) in dataList" :key="index">
      <text>{{ item.title }}</text>
    </view>
  </z-paging>
</template>

<script>
export default {
  data() {
    return { tabs: [], currentTab: 0, dataList: [] };
  },
  methods: {
    switchTab(i) {
      this.currentTab = i;
      this.$refs.paging.reload();
    },
    async queryList(pageNo, pageSize) {
      const res = await uni.request({
        url: '/api/list',
        data: { pageNo, pageSize, tabId: this.tabs[this.currentTab].id }
      });
      this.$refs.paging.complete(res.data.list);
    }
  }
};
</script>
```

## 全局配置 (main.js)

```js
// main.js
uni.$zp = {
  config: {
    'default-page-size': 15,
    'empty-view-text': '暂无数据',
    'loading-more-no-more-text': '没有更多了',
    'refresher-default-text': '继续下拉刷新',
    'refresher-pulling-text': '松开立即刷新',
    'refresher-refreshing-text': '正在刷新...',
  }
}
```

## 全局错误处理 (main.js)

```js
// 请求失败时全局通知z-paging
uni.$emit('z-paging-error-emit', '请求失败原因(可选)');

// 请求成功时全局通知z-paging
uni.$emit('z-paging-complete-emit', resultArray);
```

## 拦截器 (main.js)

```js
import ZPInterceptor from '@/uni_modules/z-paging/components/z-paging/js/z-paging-interceptor';

// 拦截@query参数
ZPInterceptor.handleQuery((pageNo, pageSize, from) => {
  return [pageNo, pageSize, from]; // 可修改后return
});

// 拦截fetch参数和响应
ZPInterceptor.handleFetchParams((params, extraParams) => {
  return { pageNo: params.pageNo, pageSize: params.pageSize, ...extraParams };
}).handleFetchResult((fetchResult, paging) => {
  fetchResult.then(res => {
    paging.complete(res.data.list);
  }).catch(err => {
    paging.complete(false);
  });
});
```
