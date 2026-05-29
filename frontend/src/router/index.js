import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/product/:id',
    name: 'product-detail',
    component: () => import('../views/ProductDetail.vue'),
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('../views/Cart.vue'),
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('../views/Checkout.vue'),
  },
  {
    path: '/orders',
    name: 'orders',
    component: () => import('../views/Orders.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/Profile.vue'),
  },
  {
    path: '/sales/dashboard',
    name: 'sales-dashboard',
    component: () => import('../views/sales/Dashboard.vue'),
  },
  {
    path: '/sales/categories',
    name: 'sales-categories',
    component: () => import('../views/sales/Categories.vue'),
  },
  {
    path: '/sales/products',
    name: 'sales-products',
    component: () => import('../views/sales/Products.vue'),
  },
  {
    path: '/sales/orders',
    name: 'sales-orders',
    component: () => import('../views/sales/Orders.vue'),
  },
  {
    path: '/sales/logs',
    name: 'sales-logs',
    component: () => import('../views/sales/Logs.vue'),
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: () => import('../views/admin/Dashboard.vue'),
  },
  {
    path: '/admin/staff',
    name: 'admin-staff',
    component: () => import('../views/admin/Staff.vue'),
  },
  {
    path: '/admin/reports',
    name: 'admin-reports',
    component: () => import('../views/admin/Reports.vue'),
  },
  {
    path: '/admin/monitor',
    name: 'admin-monitor',
    component: () => import('../views/admin/Monitor.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
