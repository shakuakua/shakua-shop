<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import VChart from 'vue-echarts'
import 'echarts'

const anomalies = ref([])
const stats = ref({ mean_amount: 0, std_amount: 0, threshold: 0 })
const lowStock = ref([])
const topCategory = ref(null)

async function load() {
  const { data } = await api.get('/admin/monitor')
  anomalies.value = data.anomalies
  stats.value = data.stats
  lowStock.value = data.low_stock
  topCategory.value = data.top_category
}

const scatterOption = () => ({
  tooltip: { trigger: 'item' },
  xAxis: { type: 'category', data: anomalies.value.map(a => `#${a.id}`) },
  yAxis: { type: 'value', name: '金额' },
  series: [{
    type: 'scatter',
    data: anomalies.value.map(a => a.total_amount),
    symbolSize: 16,
    itemStyle: { color: '#e74c3c' },
    markLine: {
      data: [{ yAxis: stats.value.threshold, name: '异常阈值' }],
      lineStyle: { type: 'dashed', color: '#e74c3c' },
    },
  }],
})

onMounted(load)
</script>

<template>
  <div class="monitor">
    <h2>异常监控</h2>

    <!-- Stats -->
    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6">
        <el-card><el-statistic title="均值" :value="stats.mean_amount" prefix="¥" :precision="2" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="标准差" :value="stats.std_amount" :precision="2" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="异常阈值" :value="stats.threshold" prefix="¥" :precision="2" /></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="异常订单" :value="anomalies.length" /></el-card>
      </el-col>
    </el-row>

    <!-- Anomaly Chart -->
    <el-card class="chart-card" v-if="anomalies.length">
      <h3>异常订单分布</h3>
      <v-chart :option="scatterOption()" style="height:300px" autoresize />
    </el-card>

    <!-- Anomaly List -->
    <el-card class="chart-card" v-if="anomalies.length">
      <h3>异常订单列表</h3>
      <el-table :data="anomalies" stripe>
        <el-table-column prop="id" label="订单号" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="z_score" label="Z-Score" />
        <el-table-column prop="status" label="状态" />
      </el-table>
    </el-card>

    <!-- Low Stock -->
    <el-card class="chart-card" v-if="lowStock.length">
      <h3>低库存预警 (库存 < 5)</h3>
      <el-table :data="lowStock" stripe>
        <el-table-column prop="name" label="商品" />
        <el-table-column prop="stock" label="库存" />
        <el-table-column prop="category_name" label="分类" />
      </el-table>
    </el-card>

    <!-- Top Category -->
    <el-card class="chart-card" v-if="topCategory">
      <h3>热销趋势</h3>
      <p>最热门分类: <b>{{ topCategory.name }}</b> — 销量: {{ topCategory.quantity }}</p>
    </el-card>
  </div>
</template>

<style scoped>
.monitor { max-width: 1000px; margin: 0 auto; }
h2, h3 { margin-bottom: 12px; }
.chart-card { margin-bottom: 20px; }
</style>
