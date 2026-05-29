<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cart = useCartStore()
const loading = ref(false)
const total = cart.items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0).toFixed(2)

async function doCheckout() {
  loading.value = true
  try {
    await cart.checkout()
    router.push('/orders')
  } catch { } finally { loading.value = false }
}
</script>

<template>
  <div class="checkout-page">
    <h2>确认订单</h2>
    <div class="checkout-card">
      <div class="section">
        <h3>收货信息</h3>
        <p class="address">默认收货地址</p>
        <p class="address-detail">收货人：用户 | 联系电话：138****8888</p>
      </div>
      <el-divider />
      <div class="section">
        <h3>订单商品</h3>
        <div v-for="item in cart.items" :key="item.id" class="order-item">
          <img v-if="item.product?.image_url" :src="item.product.image_url" class="oi-img" />
          <span class="oi-name">{{ item.product?.name }}</span>
          <span class="oi-qty">x{{ item.quantity }}</span>
          <span class="oi-price">&yen;{{ ((item.product?.price || 0) * item.quantity).toFixed(2) }}</span>
        </div>
      </div>
      <el-divider />
      <div class="section total-section">
        <span>应付总额</span>
        <span class="total-price">&yen;{{ total }}</span>
      </div>
      <el-button
        type="danger"
        size="large"
        @click="doCheckout"
        :loading="loading"
        class="pay-btn"
      >
        确认支付
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.checkout-page { max-width: 700px; margin: 0 auto; }
h2 { margin-bottom: 20px; font-size: 18px; }
.checkout-card {
  background: #fff;
  padding: 30px;
  border-radius: 4px;
  border: 1px solid #eee;
}
.section { margin-bottom: 10px; }
.section h3 { font-size: 14px; margin-bottom: 10px; color: #333; }
.address { font-weight: bold; margin-bottom: 4px; }
.address-detail { font-size: 13px; color: #999; }
.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  font-size: 13px;
}
.oi-img { width: 50px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #eee; }
.oi-name { flex: 1; }
.oi-qty { color: #999; }
.oi-price { font-weight: bold; color: var(--jd-red); }
.total-section {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}
.total-price { font-size: 24px; color: var(--jd-red); font-weight: bold; }
.pay-btn {
  margin-top: 20px;
  width: 100%;
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
  height: 46px;
  font-size: 16px;
  letter-spacing: 4px;
}
</style>
