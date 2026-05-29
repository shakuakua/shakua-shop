<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/api'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const cart = useCartStore()
const auth = useAuthStore()

const products = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pages = ref(1)
const search = ref('')
const categoryId = ref(null)
const sort = ref('newest')

async function loadProducts() {
  const { data } = await api.get('/products', {
    params: {
      search: search.value,
      category_id: categoryId.value || undefined,
      sort: sort.value,
      page: page.value,
    },
  })
  products.value = data.products
  total.value = data.total
  pages.value = data.pages
}

async function loadCategories() {
  const { data } = await api.get('/categories')
  categories.value = data.categories
}

function goDetail(id) {
  router.push(`/product/${id}`)
}

function onSearch() {
  page.value = 1
  loadProducts()
}

function addCart(productId) {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  cart.addToCart(productId)
}

watch(sort, () => { page.value = 1; loadProducts() })
watch(() => route.query, (q) => {
  if (q.search) { search.value = q.search; loadProducts() }
  if (q.sort) sort.value = q.sort
}, { immediate: true })
watch(page, loadProducts)
watch(categoryId, () => { page.value = 1; loadProducts() })

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>

<template>
  <div class="home">
    <!-- Category sidebar + main -->
    <div class="home-layout">
      <aside class="side-categories">
        <div
          v-for="c in categories"
          :key="c.id"
          :class="{ active: categoryId === c.id }"
          @click="categoryId = categoryId === c.id ? null : c.id"
        >
          {{ c.name }}
        </div>
        <div :class="{ active: categoryId === null }" @click="categoryId = null">全部分类</div>
      </aside>

      <div class="main-content">
        <!-- Sort bar -->
        <div class="sort-bar">
          <span
            v-for="opt in [{k:'newest',v:'最新'},{k:'price_asc',v:'价格↑'},{k:'price_desc',v:'价格↓'}]"
            :key="opt.k"
            :class="{ active: sort === opt.k }"
            @click="sort = opt.k"
          >{{ opt.v }}</span>
          <span class="result-count">共 {{ total }} 件商品</span>
        </div>

        <!-- Product grid -->
        <div class="product-grid" v-if="products.length">
          <div v-for="p in products" :key="p.id" class="product-card" @click="goDetail(p.id)">
            <div class="product-img">
              <img v-if="p.image_url" :src="p.image_url" :alt="p.name" />
              <el-icon v-else size="64"><Goods /></el-icon>
            </div>
            <div class="product-info">
              <p class="price"><span>&yen;</span>{{ p.price }}</p>
              <p class="name" :title="p.name">{{ p.name }}</p>
              <p class="meta">
                <span>{{ p.category_name }}</span>
                <span class="sold">已售 {{ Math.floor(Math.random() * 100) }}+</span>
              </p>
            </div>
            <div class="card-hover">
              <el-button round type="danger" size="small" @click.stop="addCart(p.id)" :disabled="p.stock <= 0">
                <el-icon><ShoppingCart /></el-icon>加入购物车
              </el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无商品" />

        <div class="pagination" v-if="pages > 1">
          <el-pagination
            v-model:current-page="page"
            :total="total"
            :page-size="12"
            layout="prev, pager, next"
            background
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 1210px;
  margin: 0 auto;
}
.home-layout {
  display: flex;
  gap: 12px;
}

/* Side categories */
.side-categories {
  width: 200px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 8px 0;
}
.side-categories div {
  padding: 10px 20px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.15s;
}
.side-categories div:hover { color: var(--jd-red); background: #fff5f5; }
.side-categories div.active {
  color: var(--jd-red);
  font-weight: bold;
  background: #fff0f0;
}

/* Main content */
.main-content { flex: 1; }

/* Sort bar */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff;
  padding: 10px 16px;
  margin-bottom: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 13px;
}
.sort-bar span {
  cursor: pointer;
  color: #666;
  padding: 2px 4px;
}
.sort-bar span:hover,
.sort-bar span.active { color: var(--jd-red); font-weight: bold; }
.result-count { color: #999; margin-left: auto; cursor: default !important; }

/* Product grid */
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
@media (max-width: 1100px) {
  .product-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 800px) {
  .side-categories { display: none; }
  .product-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Product card */
.product-card {
  position: relative;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}
.product-card:hover {
  border-color: var(--jd-red);
  box-shadow: 0 2px 12px rgba(201, 22, 35, 0.12);
}
.product-card:hover .card-hover {
  opacity: 1;
  transform: translateY(0);
}
.product-img {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
  overflow: hidden;
}
.product-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.product-card:hover .product-img img { transform: scale(1.05); }
.product-info {
  padding: 12px;
}
.price {
  font-size: 20px;
  color: var(--jd-red);
  font-weight: bold;
  margin-bottom: 6px;
}
.price span { font-size: 14px; }
.name {
  font-size: 13px;
  color: #333;
  line-height: 1.4;
  height: 36px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
}
.meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #bbb;
}
.sold { color: #e0e0e0; }

/* Hover button */
.card-hover {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(201,22,35,0.9));
  padding: 20px 12px 12px;
  display: flex;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.2s;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
