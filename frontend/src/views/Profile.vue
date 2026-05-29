<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const auth = useAuthStore()
const stats = ref({ order_count: 0, browse_count: 0 })
const userProfile = ref(null)

async function load() {
  const { data } = await api.get('/profile')
  stats.value = data.stats
  try { const res = await api.get('/data/user-profile'); userProfile.value = res.data } catch { }
}

onMounted(load)
</script>

<template>
  <div class="profile-page">
    <h2>个人中心</h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="info-card">
          <div class="avatar">
            <el-icon size="48"><UserFilled /></el-icon>
          </div>
          <h3>{{ auth.user?.username }}</h3>
          <p class="role-tag"><el-tag size="small">顾客</el-tag></p>
          <el-divider />
          <div class="info-list">
            <p><span>邮箱</span><span>{{ auth.user?.email }}</span></p>
            <p><span>地区</span><span>{{ auth.user?.region || '未设置' }}</span></p>
            <p><span>注册时间</span><span>{{ auth.user?.created_at ? new Date(auth.user?.created_at).toLocaleDateString() : '-' }}</span></p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card class="stats-card">
          <h3>数据统计</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <span class="stat-num">{{ stats.order_count }}</span>
                <span class="stat-label">订单数</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <span class="stat-num">{{ stats.browse_count }}</span>
                <span class="stat-label">浏览记录</span>
              </div>
            </el-col>
            <el-col :span="8" v-if="userProfile">
              <div class="stat-item">
                <span class="stat-num">&yen;{{ userProfile.avg_order_value }}</span>
                <span class="stat-label">平台平均客单价</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="stats-card" v-if="userProfile?.category_preferences?.length">
          <h3>热门分类排行</h3>
          <div class="cat-list">
            <div v-for="(c, i) in userProfile.category_preferences" :key="c.name" class="cat-row">
              <span class="cat-rank" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
              <span class="cat-name">{{ c.name }}</span>
              <span class="cat-views">{{ c.views }} 次浏览</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.profile-page { max-width: 900px; margin: 0 auto; }
h2 { margin-bottom: 20px; font-size: 18px; }

.info-card { text-align: center; }
.avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px;
  color: #ccc;
}
.info-card h3 { font-size: 16px; margin-bottom: 6px; }
.role-tag { margin-bottom: 10px; }
.info-list p {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 6px 0;
  color: #666;
}

.stats-card { margin-bottom: 16px; }
.stats-card h3 { font-size: 14px; margin-bottom: 16px; padding-left: 8px; border-left: 3px solid var(--jd-red); }
.stat-item {
  text-align: center;
  padding: 16px 0;
}
.stat-num {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: var(--jd-red);
}
.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.cat-list { margin-top: 8px; }
.cat-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.cat-rank {
  width: 22px; height: 22px;
  line-height: 22px;
  text-align: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: #fff;
  background: #999;
  margin-right: 12px;
}
.rank-1 { background: #e4393c; }
.rank-2 { background: #f60; }
.rank-3 { background: #f90; }
.cat-name { flex: 1; }
.cat-views { color: #bbb; }
</style>
