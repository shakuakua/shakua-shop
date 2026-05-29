<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import VChart from 'vue-echarts'
import 'echarts'

const reports = ref(null)
const trendData = ref([])
const trendPeriod = ref('week')

async function loadReports() {
  const { data } = await api.get('/admin/reports')
  reports.value = data
}

async function loadTrend() {
  const { data } = await api.get('/data/sales-trend', { params: { period: trendPeriod.value } })
  trendData.value = data.data
}

const salesTrendOption = () => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: trendData.value.map(d => d.label) },
  yAxis: { type: 'value' },
  series: [
    { name: '订单数', type: 'line', data: trendData.value.map(d => d.count), smooth: true },
    { name: '营收', type: 'line', data: trendData.value.map(d => d.revenue), smooth: true },
  ],
  legend: { data: ['订单数', '营收'] },
})

const leaderboardOption = () => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (reports.value?.leaderboard || []).map(l => l.name) },
  yAxis: { type: 'value' },
  series: [
    { name: '销量', type: 'bar', data: (reports.value?.leaderboard || []).map(l => l.sold_count) },
  ],
})

const categoryPieOption = () => ({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: (reports.value?.category_sales || []).map(c => ({ name: c.name, value: c.total_qty })),
  }],
})

function switchTrend(period) {
  trendPeriod.value = period
  loadTrend()
}

onMounted(() => { loadReports(); loadTrend() })
</script>

<template>
  <div class="reports">
    <h2>销售报表</h2>

    <!-- Sales Trend -->
    <el-card class="chart-card">
      <div class="chart-header">
        <h3>销售趋势</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="switchTrend">
          <el-radio-button value="day">日</el-radio-button>
          <el-radio-button value="week">周</el-radio-button>
          <el-radio-button value="month">月</el-radio-button>
        </el-radio-group>
      </div>
      <v-chart :option="salesTrendOption()" style="height:350px" autoresize />
    </el-card>

    <!-- Leaderboard -->
    <el-card class="chart-card">
      <h3>商品销量排行榜</h3>
      <v-chart :option="leaderboardOption()" style="height:350px" autoresize />
    </el-card>

    <!-- Category Distribution -->
    <el-card class="chart-card">
      <h3>分类销售分布</h3>
      <v-chart :option="categoryPieOption()" style="height:350px" autoresize />
    </el-card>

    <!-- Sales Performance Table -->
    <el-card class="chart-card" v-if="reports?.sales_performance?.length">
      <h3>销售人员业绩</h3>
      <el-table :data="reports.sales_performance" stripe>
        <el-table-column prop="username" label="销售员" />
        <el-table-column prop="order_count" label="订单数" />
        <el-table-column prop="total_sales" label="销售额" />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.reports { max-width: 1000px; margin: 0 auto; }
.chart-card { margin-bottom: 20px; }
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.chart-header h3 { margin: 0; }
h2 { margin-bottom: 20px; }
</style>
