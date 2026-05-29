<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const product = ref(null)
const alsoBought = ref([])
const quantity = ref(1)
let startTime = 0

async function load() {
  const { data } = await api.get(`/products/${route.params.id}`)
  product.value = data.product
  alsoBought.value = data.also_bought
  startTime = Date.now()
}

function addCart() {
  if (!auth.isLoggedIn) { router.push('/login'); return }
  cart.addToCart(product.value.id, quantity.value)
}

function goProduct(id) {
  router.push('/product/' + id)
}

onMounted(async () => {
  await load()
})

onBeforeUnmount(() => {
  const duration = Math.floor((Date.now() - startTime) / 1000)
  if (product.value && duration > 0) {
    fetch('/api/browse-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: product.value.id,
        category_id: product.value.category_id,
        duration_seconds: duration,
      }),
      keepalive: true,
    })
  }
})
</script>

<template>
  <div class="detail" v-if="product">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <span @click="router.push('/')">首页</span>
      <span>/</span>
      <span>{{ product.category_name }}</span>
      <span>/</span>
      <span>{{ product.name }}</span>
    </div>

    <div class="detail-main">
      <div class="detail-img">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
        <el-icon v-else size="140"><Goods /></el-icon>
      </div>
      <div class="detail-info">
        <h1>{{ product.name }}</h1>
        <p class="detail-desc">{{ product.description }}</p>
        <div class="detail-price-box">
          <span class="label">价格</span>
          <span class="detail-price">&yen;{{ product.price }}</span>
        </div>
        <div class="detail-meta">
          <span>库存：<b>{{ product.stock }}</b> 件</span>
          <span>分类：<el-tag size="small">{{ product.category_name }}</el-tag></span>
          <span>上架时间：{{ new Date(product.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="detail-actions">
          <el-input-number v-model="quantity" :min="1" :max="product.stock" size="large" />
          <el-button type="danger" size="large" @click="addCart" :disabled="product.stock <= 0" class="add-cart-btn">
            <el-icon><ShoppingCart /></el-icon>加入购物车
          </el-button>
          <el-button size="large" @click="cart.addToCart(product.id, quantity); router.push('/cart')" :disabled="product.stock <= 0">
            立即购买
          </el-button>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="recommend" v-if="alsoBought.length">
      <h2>看了又看</h2>
      <div class="rec-grid">
        <div v-for="p in alsoBought" :key="p.id" class="rec-card" @click="goProduct(p.id)">
          <div class="rec-img">
            <img v-if="p.image_url" :src="p.image_url" :alt="p.name" />
            <el-icon v-else size="32"><Goods /></el-icon>
          </div>
          <p class="rec-price">&yen;{{ p.price }}</p>
          <p class="rec-name">{{ p.name }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail { max-width: 900px; margin: 0 auto; }

.breadcrumb {
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}
.breadcrumb span { cursor: pointer; }
.breadcrumb span:hover { color: var(--jd-red); }
.breadcrumb span:nth-child(even) { cursor: default; margin: 0 6px; }

.detail-main {
  display: flex;
  gap: 30px;
  background: #fff;
  padding: 30px;
  border-radius: 4px;
  margin-bottom: 20px;
}
.detail-img {
  width: 380px; height: 380px;
  flex-shrink: 0;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
}
.detail-img img {
  width: 100%; height: 100%; object-fit: contain;
}

.detail-info h1 {
  font-size: 20px;
  line-height: 1.4;
  margin-bottom: 12px;
}
.detail-desc { color: #999; font-size: 13px; margin-bottom: 16px; }
.detail-price-box {
  background: #fff5f5;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}
.detail-price-box .label { font-size: 12px; color: #999; margin-right: 12px; }
.detail-price {
  font-size: 28px;
  color: var(--jd-red);
  font-weight: bold;
}
.detail-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #999;
  margin-bottom: 20px;
}
.detail-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.add-cart-btn {
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
}

.recommend {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
}
.recommend h2 {
  font-size: 16px;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid var(--jd-red);
}
.rec-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.rec-card {
  width: 140px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.rec-card:hover { opacity: 0.8; }
.rec-card * {
  pointer-events: none;
}
.rec-img {
  width: 140px; height: 140px;
  background: #fafafa;
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
  border: 1px solid #eee;
}
.rec-img img {
  width: 100%; height: 100%; object-fit: cover;
}
.rec-price {
  font-size: 14px;
  color: var(--jd-red);
  font-weight: bold;
}
.rec-name {
  font-size: 11px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
