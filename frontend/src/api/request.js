import axios from 'axios';
import { ElMessage } from 'element-plus';

import { appConfig } from '@/utils/config';

const request = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 30000,
});

const getToken = () => localStorage.getItem('hr-system-token') || '';
const getRefreshToken = () => localStorage.getItem('hr-system-refresh-token') || '';

request.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config || {};
    if (error.response?.status === 401 && !originalRequest._retry && getRefreshToken()) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await axios.post(`${appConfig.apiBaseUrl}/auth/refresh`, {
          refresh_token: getRefreshToken(),
        });
        localStorage.setItem('hr-system-token', refreshResponse.data.data.token);
        localStorage.setItem('hr-system-refresh-token', refreshResponse.data.data.refreshToken);
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.data.token}`;
        return request(originalRequest);
      } catch {
        localStorage.removeItem('hr-system-token');
        localStorage.removeItem('hr-system-refresh-token');
        if (!originalRequest.skipAuthRedirect) {
          window.location.href = '/login';
        }
      }
    }
    const message = error.response?.status === 401 && originalRequest.skipAuthRedirect
      ? '请先登录'
      : error.response?.data?.detail || '请求失败，请稍后重试';
    if (!originalRequest.suppressErrorMessage) {
      ElMessage.error(message);
    }
    return Promise.reject(error);
  },
);

export default request;
