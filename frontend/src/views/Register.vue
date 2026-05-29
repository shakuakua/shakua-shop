<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', email: '', password: '', password2: '', region: '' })
const loading = ref(false)

async function doRegister() {
  if (!form.value.username || !form.value.email || !form.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.value.password !== form.value.password2) {
    ElMessage.warning('两次密码不一致')
    return
  }
  loading.value = true
  try {
    await auth.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      region: form.value.region,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch { } finally { loading.value = false }
}
</script>

<template>
  <div class="register-wrapper">
    <div class="reg-box">
      <h2>用户注册</h2>
      <el-form @submit.prevent="doRegister" class="reg-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-input v-model="form.username" placeholder="用户名" size="large" />
          </el-col>
          <el-col :span="12">
            <el-input v-model="form.email" placeholder="邮箱" size="large" />
          </el-col>
        </el-row>
        <el-row :gutter="16" style="margin-top:16px">
          <el-col :span="12">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password size="large" />
          </el-col>
          <el-col :span="12">
            <el-input v-model="form.password2" type="password" placeholder="确认密码" show-password size="large" />
          </el-col>
        </el-row>
        <div style="margin-top:16px">
          <el-select v-model="form.region" placeholder="选择地区（可选）" clearable size="large" style="width:100%">
            <el-option v-for="r in ['北京','上海','广州','深圳','杭州','成都','武汉','南京']" :key="r" :label="r" :value="r" />
          </el-select>
        </div>
        <div style="margin-top:20px">
          <el-button type="danger" native-type="submit" :loading="loading" size="large" class="reg-btn">
            注 册
          </el-button>
        </div>
      </el-form>
      <p class="reg-tip">已有账号？<router-link to="/login">去登录</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.register-wrapper {
  max-width: 560px;
  margin: 40px auto;
}
.reg-box {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.06);
}
.reg-box h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 20px;
  color: #333;
}
.reg-btn {
  width: 100%;
  background: var(--jd-red) !important;
  border-color: var(--jd-red) !important;
  height: 44px;
  font-size: 16px;
  letter-spacing: 6px;
}
.reg-tip { text-align: center; color: #999; font-size: 13px; margin-top: 16px; }
.reg-tip a { color: var(--jd-red); }
</style>
