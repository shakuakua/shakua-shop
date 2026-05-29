<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const stats = ref({
  today_orders: 0,
  today_revenue: 0,
  product_count: 0,
  total_orders: 0,
})

async function load() {
  const { data } = await api.get('/sales/dashboard')
  stats.value = data
}

onMounted(load)
</script>

<template>
  <div class="dashboard">
    <h2>销售人员工作台</h2>
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="6">
        <el-card><el-statistic title="今日订单" :value="stats.today_orders" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="今日营收" :value="stats.today_revenue" prefix="¥" :precision="2" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="商品总数" :value="stats.product_count" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="总订单数" :value="stats.total_orders" /></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 10px; }
</style>
