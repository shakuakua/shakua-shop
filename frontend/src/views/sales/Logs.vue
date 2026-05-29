<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const logs = ref([])
const logType = ref('browse')
const page = ref(1)
const total = ref(0)

async function load() {
  const { data } = await api.get('/sales/logs', { params: { type: logType.value, page: page.value } })
  logs.value = data.logs
  total.value = data.total
}

function switchType(type) {
  logType.value = type
  page.value = 1
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <h2>日志查看</h2>
    <el-tabs v-model="logType" @tab-change="switchType">
      <el-tab-pane label="浏览日志" name="browse" />
      <el-tab-pane label="操作日志" name="operation" />
    </el-tabs>

    <el-table :data="logs" stripe>
      <template v-if="logType === 'browse'">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="duration_seconds" label="浏览时长(秒)" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ row.timestamp }}</template>
        </el-table-column>
      </template>
      <template v-else>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="operation_type" label="操作类型" width="100" />
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ row.timestamp }}</template>
        </el-table-column>
      </template>
    </el-table>

    <el-pagination
      v-if="total > 20"
      v-model:current-page="page"
      :total="total"
      :page-size="20"
      layout="prev, pager, next"
      background
      style="margin-top:16px;justify-content:center"
      @current-change="load"
    />
  </div>
</template>

<style scoped>
.page { max-width: 1000px; margin: 0 auto; }
h2 { margin-bottom: 10px; }
</style>
