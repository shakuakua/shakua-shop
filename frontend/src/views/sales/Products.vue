<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const products = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({
  name: '', description: '', price: 0, stock: 0, image_url: '', category_id: null,
})

async function loadProducts() {
  const { data } = await api.get('/sales/products')
  products.value = data.products
}

async function loadCategories() {
  const { data } = await api.get('/sales/categories')
  categories.value = data.categories
}

function openAdd() {
  editing.value = null
  form.value = { name: '', description: '', price: 0, stock: 0, image_url: '', category_id: null }
  dialogVisible.value = true
}

function openEdit(p) {
  editing.value = p
  form.value = {
    name: p.name, description: p.description, price: p.price,
    stock: p.stock, image_url: p.image_url, category_id: p.category_id,
  }
  dialogVisible.value = true
}

async function save() {
  const payload = { ...form.value, price: parseFloat(form.value.price), stock: parseInt(form.value.stock) }
  if (editing.value) {
    await api.put(`/sales/products/${editing.value.id}`, payload)
    ElMessage.success('商品已更新')
  } else {
    await api.post('/sales/products', payload)
    ElMessage.success('商品已添加')
  }
  dialogVisible.value = false
  await loadProducts()
}

async function remove(p) {
  await ElMessageBox.confirm(`确定删除商品 "${p.name}"？`, '确认', { type: 'warning' })
  await api.delete(`/sales/products/${p.id}`)
  ElMessage.success('商品已删除')
  await loadProducts()
}

onMounted(() => { loadProducts(); loadCategories() })
</script>

<template>
  <div class="page">
    <div class="header">
      <h2>商品管理</h2>
      <el-button type="primary" @click="openAdd">添加商品</el-button>
    </div>

    <el-table :data="products" stripe>
      <el-table-column prop="id" label="ID" width="50" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑商品' : '添加商品'" width="500">
      <el-form>
        <el-form-item label="商品名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="form.price" :min="0" :step="0.01" style="width:100%" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="form.stock" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="form.image_url" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page { max-width: 1000px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
