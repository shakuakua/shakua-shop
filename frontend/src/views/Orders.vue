<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const orders = ref([])

async function load() {
  const { data } = await api.get('/orders')
  orders.value = data.orders
}

const statusMap = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'success' },
  shipped: { text: '已发货', type: '' },
  completed: { text: '已完成', type: 'info' },
}

onMounted(load)
</script>

<template>
  <div class="orders-page">
    <h2>我的订单</h2>
    <el-empty v-if="!orders.length" description="暂无订单" />
    <div v-for="o in orders" :key="o.id" class="order-card">
      <div class="order-header">
        <span class="order-id">订单号：{{ o.id }}</span>
        <span class="order-time">{{ new Date(o.created_at).toLocaleString() }}</span>
        <el-tag :type="statusMap[o.status]?.type || 'info'" size="small">
          {{ statusMap[o.status]?.text || o.status }}
        </el-tag>
      </div>
      <div class="order-body">
        <div v-for="item in o.items" :key="item.id" class="order-item">
          <span class="oi-name">{{ item.product_name }}</span>
          <span class="oi-qty">x{{ item.quantity }}</span>
          <span class="oi-price">&yen;{{ (item.unit_price * item.quantity).toFixed(2) }}</span>
        </div>
      </div>
      <div class="order-footer">
        <span>合计：<b>&yen;{{ o.total_amount }}</b></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.orders-page { max-width: 750px; margin: 0 auto; }
h2 { margin-bottom: 20px; font-size: 18px; }
.order-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 16px 20px;
  margin-bottom: 14px;
}
.order-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}
.order-id { font-weight: bold; }
.order-time { color: #999; margin-left: auto; }
.order-body { padding: 10px 0; }
.order-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
  font-size: 13px;
}
.oi-name { flex: 1; }
.oi-qty { color: #999; width: 60px; text-align: center; }
.oi-price { color: var(--jd-red); width: 90px; text-align: right; font-weight: bold; }
.order-footer {
  text-align: right;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
  font-size: 14px;
}
.order-footer b { color: var(--jd-red); font-size: 18px; }
</style>
