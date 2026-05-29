<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'

const auth = useAuthStore()

onMounted(() => {
  auth.fetchUser()
})
</script>

<template>
  <NavBar />
  <main>
    <router-view />
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-col">
        <h4>购物指南</h4>
        <a href="#">购物流程</a>
        <a href="#">支付方式</a>
        <a href="#">常见问题</a>
      </div>
      <div class="footer-col">
        <h4>配送服务</h4>
        <a href="#">配送范围</a>
        <a href="#">配送时效</a>
        <a href="#">物流查询</a>
      </div>
      <div class="footer-col">
        <h4>售后服务</h4>
        <a href="#">退换政策</a>
        <a href="#">退款说明</a>
        <a href="#">联系客服</a>
      </div>
      <div class="footer-col">
        <h4>关于我们</h4>
        <p>网络应用开发课程设计</p>
        <p>电商大数据分析平台</p>
      </div>
    </div>
    <div class="footer-bottom">
      <p>2026 网络应用开发课程设计 - 电商平台</p>
    </div>
  </footer>
</template>

<style>
:root {
  --jd-red: #c91623;
  --jd-red-light: #e4393c;
  --jd-orange: #f60;
  --jd-bg: #f4f4f4;
  --jd-border: #e8e8e8;
  --jd-text: #333;
  --jd-text-light: #999;
  --jd-white: #fff;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background: var(--jd-bg);
  color: var(--jd-text);
  font-size: 14px;
}

main {
  min-height: calc(100vh - 140px);
  max-width: 1210px;
  margin: 0 auto;
  padding: 20px 10px;
}

a { text-decoration: none; color: var(--jd-text); }

.site-footer {
  background: #fafafa;
  border-top: 2px solid var(--jd-red);
  margin-top: 30px;
  padding: 30px 0 0;
}
.footer-inner {
  max-width: 1210px;
  margin: 0 auto;
  display: flex;
  justify-content: space-around;
  padding: 0 10px 20px;
}
.footer-col h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #666;
}
.footer-col a, .footer-col p {
  display: block;
  font-size: 12px;
  color: #999;
  line-height: 22px;
}
.footer-bottom {
  text-align: center;
  padding: 15px 0;
  border-top: 1px solid var(--jd-border);
  font-size: 12px;
  color: #ccc;
}
</style>
