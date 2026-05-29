import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  async function fetchCart() {
    try {
      const { data } = await api.get('/cart')
      items.value = data.cart
    } catch {
      items.value = []
    }
  }

  async function addToCart(productId, quantity = 1) {
    await api.post('/cart', { product_id: productId, quantity })
    ElMessage.success('已添加到购物车')
    await fetchCart()
  }

  async function updateQuantity(itemId, quantity) {
    await api.put(`/cart/${itemId}`, { quantity })
    await fetchCart()
  }

  async function removeItem(itemId) {
    await api.delete(`/cart/${itemId}`)
    ElMessage.success('已从购物车移除')
    await fetchCart()
  }

  async function checkout() {
    const { data } = await api.post('/checkout')
    items.value = []
    ElMessage.success('下单成功！')
    return data
  }

  return { items, fetchCart, addToCart, updateQuantity, removeItem, checkout }
})
