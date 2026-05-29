<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)

async function doLogin() {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    if (auth.isAdmin) router.push('/admin/dashboard')
    else if (auth.isSales) router.push('/sales/dashboard')
    else router.push('/')
  } catch { } finally { loading.value = false }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-banner">
      <div class="banner-content">
        <h1>电商大数据平台</h1>
        <p>智能推荐 · 数据分析 · 一站购物</p>
      </div>
    </div>
    <div class="login-box">
      <div class="login-header">
        <span class="active">账号登录</span>
      </div>
      <el-form @submit.prevent="doLogin" class="login-form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="danger" native-type="submit" :loading="loading" size="large" class="login-btn">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span>还没有账号？<router-link to="/register">立即注册</router-link></span>
      </div>
      <div class="test-accounts">
        <p>测试账号</p>
        <p>管理员：admin / admin123</p>
        <p>销售：sales1 / sales123</p>
        <p>顾客：user1 / 123456</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  display: flex;
  max-width: 900px;
  margin: 40px auto;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 20px rgba(0,0,0,0.06);
}
.login-banner {
  width: 400px;
  background: linear-gradient(135deg, var(--jd-red), #a00f18);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  text-align: center;
}
.banner-content h1 { font-size: 28px; margin-bottom: 10px; }
.banner-content p { font-size: 14px; opacity: 0.85; }
.login-box {
  flex: 1;
  padding: 50px 40px;
}
.login-header {
  margin-bottom: 30px;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}
.login-form { margin-bottom: 16px; }
.login-btn {
  width: 100%;
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
  font-size: 16px;
  letter-spacing: 6px;
  height: 44px;
}
.login-footer {
  text-align: center;
  font-size: 13px;
  color: #999;
}
.login-footer a { color: var(--jd-red); }
.test-accounts {
  margin-top: 20px;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 11px;
  color: #bbb;
  line-height: 1.6;
}
.test-accounts p:first-child { color: #999; font-weight: bold; margin-bottom: 4px; }
@media (max-width: 750px) {
  .login-banner { display: none; }
  .login-box { padding: 30px 24px; }
}
</style>
