<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const total = () => cart.items.reduce((s, i) => s + (i.product?.price || 0) * i.quantity, 0).toFixed(2)
const selectedCount = () => cart.items.reduce((s, i) => s + i.quantity, 0)

function goCheckout() { router.push('/checkout') }

onMounted(() => {
  if (auth.isLoggedIn) cart.fetchCart()
})
</script>

<template>
  <div class="cart-page">
    <h2>我的购物车</h2>
    <el-empty v-if="!cart.items.length" description="购物车还是空的">
      <el-button type="danger" @click="router.push('/')">去逛逛</el-button>
    </el-empty>

    <template v-else>
      <div class="cart-header">
        <span class="ch-name">商品信息</span>
        <span class="ch-price">单价</span>
        <span class="ch-qty">数量</span>
        <span class="ch-total">小计</span>
        <span class="ch-action">操作</span>
      </div>
      <div v-for="item in cart.items" :key="item.id" class="cart-item">
        <div class="item-img">
          <img v-if="item.product?.image_url" :src="item.product.image_url" :alt="item.product.name" />
          <el-icon v-else size="48"><Goods /></el-icon>
        </div>
        <div class="item-name">
          <p class="p-name">{{ item.product?.name }}</p>
          <p class="p-cat">{{ item.product?.category_name }}</p>
        </div>
        <div class="item-price">&yen;{{ item.product?.price }}</div>
        <div class="item-qty">
          <el-input-number
            v-model="item.quantity"
            :min="1"
            :max="item.product?.stock || 1"
            size="small"
            @change="cart.updateQuantity(item.id, item.quantity)"
          />
        </div>
        <div class="item-total">&yen;{{ ((item.product?.price || 0) * item.quantity).toFixed(2) }}</div>
        <div class="item-action">
          <el-button type="danger" size="small" plain @click="cart.removeItem(item.id)">删除</el-button>
        </div>
      </div>

      <div class="cart-footer">
        <div class="cf-left">
          已选 <span class="cf-count">{{ selectedCount() }}</span> 件
        </div>
        <div class="cf-right">
          <span class="cf-total">合计：<b>&yen;{{ total() }}</b></span>
          <el-button type="danger" size="large" @click="goCheckout" class="checkout-btn">去结算</el-button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cart-page { max-width: 950px; margin: 0 auto; }
h2 { margin-bottom: 20px; font-size: 18px; }

.cart-header {
  display: flex;
  align-items: center;
  background: #fafafa;
  padding: 12px 16px;
  font-size: 12px;
  color: #999;
  border: 1px solid #eee;
  border-bottom: 2px solid var(--jd-red);
}

.cart-item {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 16px;
  border: 1px solid #eee;
  border-top: none;
  gap: 16px;
}
.item-img {
  width: 80px; height: 80px;
  flex-shrink: 0;
  background: #fafafa;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
  display: flex; align-items: center; justify-content: center;
}
.item-img img { width: 100%; height: 100%; object-fit: cover; }
.item-name { flex: 1; min-width: 0; }
.p-name { font-size: 13px; margin-bottom: 4px; }
.p-cat { font-size: 11px; color: #bbb; }

.ch-name, .item-name { flex: 1; }
.ch-price, .item-price { width: 100px; text-align: center; color: #333; font-weight: bold; }
.ch-qty, .item-qty { width: 120px; display: flex; justify-content: center; }
.ch-total, .item-total { width: 100px; text-align: center; font-weight: bold; color: var(--jd-red); }
.ch-action, .item-action { width: 80px; text-align: center; }

.cart-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 16px;
  border: 1px solid #eee;
  border-top: 2px solid #eee;
  margin-top: -1px;
}
.cf-count { color: var(--jd-red); font-weight: bold; font-size: 18px; }
.cf-right { display: flex; align-items: center; gap: 20px; }
.cf-total b { color: var(--jd-red); font-size: 20px; margin-left: 8px; }
.checkout-btn {
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
  font-size: 16px;
  padding: 0 32px;
}
</style>
