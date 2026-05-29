<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const stats = ref({
  total_users: 0, total_products: 0, total_orders: 0,
  total_revenue: 0, orders_by_status: {},
})

async function load() {
  const { data } = await api.get('/admin/dashboard')
  stats.value = data
}

onMounted(load)
</script>

<template>
  <div class="dashboard">
    <h2>管理员总览</h2>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="6">
        <el-card><el-statistic title="用户总数" :value="stats.total_users" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="商品总数" :value="stats.total_products" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="订单总数" :value="stats.total_orders" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="总营收" :value="stats.total_revenue" prefix="¥" :precision="2" /></el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top:20px">
      <h3>订单状态分布</h3>
      <el-row :gutter="20" style="margin-top:16px">
        <el-col :span="6" v-for="(count, status) in stats.orders_by_status" :key="status">
          <el-statistic :title="status" :value="count" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
h2, h3 { margin-bottom: 10px; }
</style>
