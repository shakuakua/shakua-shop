<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()
const searchText = ref('')

const activeMenu = computed(() => {
  if (route.path.startsWith('/admin')) return '/admin/dashboard'
  if (route.path.startsWith('/sales')) return '/sales/dashboard'
  return '/'
})

function doSearch() {
  if (searchText.value.trim()) {
    router.push({ path: '/', query: { search: searchText.value.trim() } })
  }
}

function goHome() {
  if (auth.isAdmin) router.push('/admin/dashboard')
  else if (auth.isSales) router.push('/sales/dashboard')
  else router.push('/')
}
</script>

<template>
  <div class="jd-header">
    <!-- Top bar -->
    <div class="header-top">
      <div class="header-top-inner">
        <span class="top-left">
          <span v-if="!auth.isLoggedIn">
            欢迎来到电商平台
            <router-link to="/login" class="top-link">请登录</router-link>
            <router-link to="/register" class="top-link top-register">免费注册</router-link>
          </span>
          <span v-else>
            你好，<b>{{ auth.user?.username }}</b>
            <span class="top-link" v-if="auth.isCustomer" @click="router.push('/orders')">我的订单</span>
            <span class="top-link" @click="auth.logout(); router.push('/')">退出</span>
          </span>
        </span>
        <span class="top-right">
          <span class="top-link" v-if="auth.isCustomer || !auth.isLoggedIn" @click="router.push('/cart')">
            购物车 {{ cart.items.length > 0 ? `(${cart.items.length})` : '' }}
          </span>
          <span class="top-link" v-if="auth.isAdmin || auth.isSales" @click="goHome">后台管理</span>
        </span>
      </div>
    </div>

    <!-- Main header with logo and search -->
    <div class="header-main">
      <div class="header-main-inner">
        <div class="logo" @click="goHome">
          <span class="logo-icon">JD</span>
          <span class="logo-text">电商平台</span>
        </div>

        <div class="search-bar" v-if="auth.isCustomer || !auth.isLoggedIn">
          <el-input
            v-model="searchText"
            placeholder="搜索商品"
            size="large"
            @keyup.enter="doSearch"
            class="search-input"
          >
            <template #append>
              <el-button @click="doSearch" class="search-btn">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- Admin indicator -->
        <div class="role-badge" v-if="auth.isAdmin">
          <el-tag type="danger" size="large">管理员模式</el-tag>
        </div>
        <div class="role-badge" v-if="auth.isSales">
          <el-tag type="warning" size="large">销售模式</el-tag>
        </div>

        <div class="header-cart" v-if="auth.isCustomer || !auth.isLoggedIn">
          <el-badge :value="cart.items.length" :hidden="!cart.items.length" :max="99">
            <el-button size="large" @click="router.push('/cart')" class="cart-btn">
              <el-icon size="20"><ShoppingCart /></el-icon>
              购物车
            </el-button>
          </el-badge>
        </div>
      </div>
    </div>

    <!-- Customer category navigation -->
    <div class="header-nav" v-if="auth.isCustomer || !auth.isLoggedIn">
      <div class="header-nav-inner">
        <div class="nav-category">全部商品分类</div>
        <div class="nav-items">
          <span :class="{ active: route.path === '/' }" @click="router.push('/')">首页</span>
          <span @click="router.push({ path: '/', query: { sort: 'newest' } })">新品上市</span>
          <span @click="router.push({ path: '/', query: { sort: 'price_desc' } })">精品推荐</span>
        </div>
      </div>
    </div>

    <!-- Admin/Sales navigation -->
    <div class="header-nav header-nav-admin" v-if="auth.isAdmin">
      <div class="header-nav-inner">
        <div class="nav-category">管理员菜单</div>
        <div class="nav-items">
          <span :class="{ active: route.path.startsWith('/admin/dashboard') }" @click="router.push('/admin/dashboard')">管理总览</span>
          <span :class="{ active: route.path.startsWith('/admin/staff') }" @click="router.push('/admin/staff')">员工管理</span>
          <span :class="{ active: route.path.startsWith('/admin/reports') }" @click="router.push('/admin/reports')">销售报表</span>
          <span :class="{ active: route.path.startsWith('/admin/monitor') }" @click="router.push('/admin/monitor')">异常监控</span>
        </div>
        <div class="nav-right">
          <el-button size="small" @click="router.push('/')">切换到前台</el-button>
        </div>
      </div>
    </div>

    <div class="header-nav header-nav-sales" v-if="auth.isSales">
      <div class="header-nav-inner">
        <div class="nav-category">销售菜单</div>
        <div class="nav-items">
          <span :class="{ active: route.path.startsWith('/sales/dashboard') }" @click="router.push('/sales/dashboard')">工作台</span>
          <span :class="{ active: route.path.startsWith('/sales/categories') }" @click="router.push('/sales/categories')">分类管理</span>
          <span :class="{ active: route.path.startsWith('/sales/products') }" @click="router.push('/sales/products')">商品管理</span>
          <span :class="{ active: route.path.startsWith('/sales/orders') }" @click="router.push('/sales/orders')">订单管理</span>
          <span :class="{ active: route.path.startsWith('/sales/logs') }" @click="router.push('/sales/logs')">日志查看</span>
        </div>
        <div class="nav-right">
          <el-button size="small" @click="router.push('/')">切换到前台</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jd-header {
  background: var(--jd-white);
  border-bottom: 2px solid var(--jd-red);
}

/* Top bar */
.header-top {
  background: #f5f5f5;
  font-size: 12px;
  color: #999;
  border-bottom: 1px solid #eee;
}
.header-top-inner {
  max-width: 1210px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
}
.top-link {
  color: #999;
  margin: 0 8px;
  cursor: pointer;
}
.top-link:hover { color: var(--jd-red); }
.top-register {
  color: var(--jd-red);
  font-weight: bold;
}

/* Main header: logo + search + cart */
.header-main {
  background: var(--jd-white);
  padding: 15px 10px;
}
.header-main-inner {
  max-width: 1210px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 30px;
}
.logo {
  cursor: pointer;
  display: flex;
  align-items: baseline;
  gap: 4px;
  flex-shrink: 0;
}
.logo-icon {
  background: var(--jd-red);
  color: #fff;
  font-size: 28px;
  font-weight: 900;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: -1px;
}
.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: var(--jd-red);
}
.search-bar {
  flex: 1;
  max-width: 550px;
}
.search-input :deep(.el-input__wrapper) {
  border: 2px solid var(--jd-red);
  border-radius: 0;
  box-shadow: none;
}
.search-input :deep(.el-input__wrapper:focus),
.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--jd-red);
}
.search-btn {
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
  color: #fff !important;
  border-radius: 0;
  width: 60px;
}
.search-btn:hover {
  background: #b0121e !important;
}
.header-cart { flex-shrink: 0; }
.cart-btn {
  border-color: #eee;
  color: var(--jd-red);
  min-width: 140px;
}
.cart-btn:hover { border-color: var(--jd-red); }

/* Nav */
.header-nav {
  background: var(--jd-red);
  color: #fff;
}
.header-nav-inner {
  max-width: 1210px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 40px;
  font-size: 14px;
  padding: 0 10px;
}
.nav-category {
  background: #a00f18;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  font-weight: bold;
  margin-right: 10px;
}
.nav-items {
  display: flex;
  gap: 8px;
}
.nav-items span {
  padding: 0 14px;
  height: 40px;
  line-height: 40px;
  cursor: pointer;
}
.nav-items span:hover,
.nav-items span.active { background: rgba(255,255,255,0.15); }
.nav-right { margin-left: auto; }
.nav-right button { font-weight: bold; }

/* Admin & Sales nav variants */
.header-nav-admin {
  background: #1a1a2e;
}
.header-nav-admin .nav-category {
  background: #16213e;
}
.header-nav-sales {
  background: #e67e22;
}
.header-nav-sales .nav-category {
  background: #d35400;
}

/* Role badge in header */
.role-badge {
  flex: 1;
  display: flex;
  justify-content: center;
}
</style>
