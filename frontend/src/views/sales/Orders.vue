<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const orders = ref([])

async function load() {
  const { data } = await api.get('/sales/orders')
  orders.value = data.orders
}

async function updateStatus(order, status) {
  await api.put(`/sales/orders/${order.id}`, { status })
  ElMessage.success('订单状态已更新')
  await load()
}

const statusColors = { pending: 'info', paid: 'success', shipped: 'warning', completed: '' }
const statusText = { pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成' }

onMounted(load)
</script>

<template>
  <div class="page">
    <h2>订单管理</h2>
    <el-table :data="orders" stripe>
      <el-table-column prop="id" label="订单号" width="80" />
      <el-table-column prop="username" label="客户" width="120" />
      <el-table-column prop="total_amount" label="金额" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusColors[row.status]">{{ statusText[row.status] || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="商品">
        <template #default="{ row }">
          <span v-for="item in row.items" :key="item.id" style="margin-right:8px">
            {{ item.product_name }} x{{ item.quantity }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button v-if="row.status === 'paid'" size="small" type="warning" @click="updateStatus(row, 'shipped')">发货</el-button>
          <el-button v-if="row.status === 'shipped'" size="small" @click="updateStatus(row, 'completed')">完成</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; }
h2 { margin-bottom: 16px; }
</style>
