<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const categories = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ name: '', description: '' })

async function load() {
  const { data } = await api.get('/sales/categories')
  categories.value = data.categories
}

function openAdd() {
  editing.value = null
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

function openEdit(cat) {
  editing.value = cat
  form.value = { name: cat.name, description: cat.description }
  dialogVisible.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/sales/categories/${editing.value.id}`, form.value)
    ElMessage.success('分类已更新')
  } else {
    await api.post('/sales/categories', form.value)
    ElMessage.success('分类已创建')
  }
  dialogVisible.value = false
  await load()
}

async function remove(cat) {
  await ElMessageBox.confirm(`确定删除分类 "${cat.name}"？`, '确认', { type: 'warning' })
  await api.delete(`/sales/categories/${cat.id}`)
  ElMessage.success('分类已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="openAdd">添加分类</el-button>
    </div>

    <el-table :data="categories" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '添加分类'" width="450">
      <el-form>
        <el-form-item label="分类名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
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
.page { max-width: 900px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
