import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.error || '请求失败'
    ElMessage.error(msg)
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
    }
    return Promise.reject(err)
  }
)

export default api
