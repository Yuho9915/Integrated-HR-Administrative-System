<template>
  <div class="login-page">
    <section class="login-stage">
      <div class="login-copy">
        <div class="login-copy__inner">
          <p class="login-copy__eyebrow">YUHO HR · 一体化协同平台</p>
          <h1>人事、行政、审批与 AI 助手统一入口</h1>
          <p>
            严格遵循 PRD 与 MRD，采用浅色专业办公视觉，支持员工、部门经理与人事行政多角色协同办公。
          </p>
        </div>
      </div>

      <div class="login-card page-section">
        <div class="login-card__header">
          <div class="logo-mark">
            <el-icon><Promotion /></el-icon>
          </div>
          <div>
            <h2>欢迎登录</h2>
            <p>请选择账号角色并进入工作台</p>
          </div>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="form.role" placeholder="请选择登录角色" style="width: 100%">
              <el-option v-for="item in roleOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <div class="login-form__meta">
            <el-checkbox v-model="rememberPassword" label="记住密码" />
            <el-checkbox v-model="rememberAccount" label="记住账号" />
          </div>
          <el-button type="primary" class="login-btn" :loading="loading" @click="submit">登录系统</el-button>
        </el-form>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Promotion } from '@element-plus/icons-vue';

import { ROLE_OPTIONS } from '@/constants/roles';
import { useAppStore } from '@/stores/app';

const router = useRouter();
const store = useAppStore();
const formRef = ref();
const loading = ref(false);
const roleOptions = ROLE_OPTIONS;
const rememberAccount = ref(true);
const rememberPassword = ref(true);

const defaults = {
  employee: { username: 'employee', password: '123456' },
  manager: { username: 'manager', password: '123456' },
  hr: { username: 'admin.hr', password: '123456' },
};

const storageKeys = {
  account: 'hr-system-login-account',
  password: 'hr-system-login-password',
  rememberAccount: 'hr-system-remember-account',
  rememberPassword: 'hr-system-remember-password',
};

const storedRememberAccount = localStorage.getItem(storageKeys.rememberAccount);
const storedRememberPassword = localStorage.getItem(storageKeys.rememberPassword);
const storedAccount = localStorage.getItem(storageKeys.account);
const storedPassword = localStorage.getItem(storageKeys.password);

if (storedRememberAccount !== null) {
  rememberAccount.value = storedRememberAccount === 'true';
}
if (storedRememberPassword !== null) {
  rememberPassword.value = storedRememberPassword === 'true';
}
if (rememberPassword.value) {
  rememberAccount.value = true;
}

const initialRole = 'hr';
const form = reactive({
  username: rememberAccount.value && storedAccount ? storedAccount : defaults[initialRole].username,
  password: rememberPassword.value && storedPassword ? storedPassword : defaults[initialRole].password,
  role: initialRole,
});

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
};

watch(
  () => form.role,
  (role) => {
    const matched = defaults[role];
    if (!matched) return;
    form.username = matched.username;
    form.password = matched.password;
  },
);

watch(rememberPassword, (value) => {
  if (value) {
    rememberAccount.value = true;
  }
});

watch(rememberAccount, (value) => {
  if (!value) {
    rememberPassword.value = false;
  }
});

const persistRememberState = () => {
  localStorage.setItem(storageKeys.rememberAccount, String(rememberAccount.value));
  localStorage.setItem(storageKeys.rememberPassword, String(rememberPassword.value));

  if (rememberAccount.value) {
    localStorage.setItem(storageKeys.account, form.username);
  } else {
    localStorage.removeItem(storageKeys.account);
  }

  if (rememberPassword.value) {
    localStorage.setItem(storageKeys.password, form.password);
  } else {
    localStorage.removeItem(storageKeys.password);
  }
};

const submit = async () => {
  await formRef.value.validate();
  loading.value = true;
  try {
    await store.login(form);
    persistRememberState();
    ElMessage.success('登录成功');
    router.push(store.homePath);
  } catch {
    // message handled globally by request interceptor
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(64, 158, 255, 0.18), transparent 24%),
    radial-gradient(circle at bottom right, rgba(102, 177, 255, 0.2), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #f8f9fa 100%);
}

.login-stage {
  width: min(1200px, 100%);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 24px;
  align-items: stretch;
}

.login-copy {
  display: flex;
  align-items: center;
  min-height: 100%;
}

.login-copy__inner {
  display: grid;
  gap: 14px;
}

.login-copy h1 {
  margin: 0;
  font-size: 40px;
  line-height: 1.3;
  color: var(--hr-title);
}

.login-copy p {
  margin: 0;
  line-height: 1.9;
  max-width: 640px;
}

.login-copy__eyebrow {
  color: var(--hr-primary);
  font-size: 12px;
  letter-spacing: 0.18em;
}

.login-card {
  padding: 28px;
}

.login-card__header {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
}

.logo-mark {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #1c4fa1, #6db7ff);
  color: #fff;
  box-shadow: 0 14px 30px rgba(28, 79, 161, 0.22);
}

.logo-mark :deep(svg) {
  font-size: 24px;
}

.login-card__header h2 {
  margin: 0;
  color: var(--hr-title);
}

.login-card__header p {
  margin: 6px 0 0;
  color: var(--hr-info);
  font-size: 12px;
}

.login-form__meta {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
  font-size: 12px;
  color: var(--hr-info);
}

.login-btn {
  width: 100%;
  height: 42px;
  border-radius: 8px;
}

@media (max-width: 900px) {
  .login-stage {
    grid-template-columns: 1fr;
  }

  .login-copy {
    min-height: auto;
  }

  .login-copy h1 {
    font-size: 28px;
  }

  .login-form__meta {
    flex-wrap: wrap;
    gap: 10px 18px;
  }
}
</style>
