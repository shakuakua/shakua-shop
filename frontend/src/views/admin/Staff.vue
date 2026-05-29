<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const staff = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ username: '', email: '', password: '', role: 'sales' })

async function load() {
  const { data } = await api.get('/admin/staff')
  staff.value = data.staff
}

function openAdd() {
  editing.value = null
  form.value = { username: '', email: '', password: '', role: 'sales' }
  dialogVisible.value = true
}

function openEdit(s) {
  editing.value = s
  form.value = { username: s.username, email: s.email, password: '', role: s.role }
  dialogVisible.value = true
}

async function save() {
  if (editing.value) {
    await api.put(`/admin/staff/${editing.value.id}`, {
      username: form.value.username,
      email: form.value.email,
    })
    ElMessage.success('员工信息已更新')
  } else {
    await api.post('/admin/staff', form.value)
    ElMessage.success('员工已创建')
  }
  dialogVisible.value = false
  await load()
}

async function resetPwd(s) {
  const { value } = await ElMessageBox.prompt('新密码', '重置密码', { inputType: 'password' })
  if (value) {
    await api.post(`/admin/staff/${s.id}/reset-password`, { new_password: value })
    ElMessage.success('密码已重置')
  }
}

async function remove(s) {
  await ElMessageBox.confirm(`确定删除员工 "${s.username}"？`, '确认', { type: 'warning' })
  await api.delete(`/admin/staff/${s.id}`)
  ElMessage.success('员工已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="header">
      <h2>员工管理</h2>
      <el-button type="primary" @click="openAdd">添加员工</el-button>
    </div>

    <el-table :data="staff" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'warning'">{{ row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" @click="resetPwd(row)">重置密码</el-button>
          <el-button size="small" type="danger" @click="remove(row)" v-if="row.role !== 'admin'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑员工' : '添加员工'" width="450">
      <el-form>
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="销售" value="sales" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editing" label="密码">
          <el-input v-model="form.password" type="password" show-password />
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
