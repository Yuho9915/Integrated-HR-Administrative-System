<template>
  <div class="shell-layout">
    <aside class="sidebar page-section" :class="{ 'is-mobile-open': mobileOpen }">
      <div class="brand-box">
        <div class="brand-box__badge">HR</div>
        <div>
          <strong>人事行政一体化HR系统</strong>
          <p>CloudBase · Zeabur · Doubao</p>
        </div>
      </div>

      <el-menu :default-active="route.path" router class="sidebar-menu">
        <el-menu-item v-for="item in store.menus" :key="item.path" :index="item.path">
          <el-icon><component :is="iconRegistry[item.icon]" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <section class="main-panel">
      <header class="topbar page-section">
        <div class="topbar__left">
          <el-button class="mobile-menu" circle @click="mobileOpen = !mobileOpen">☰</el-button>
          <div>
            <AppBreadcrumb :items="breadcrumbItems" />
            <h2>{{ route.meta.title }}</h2>
            <p>{{ route.meta.description }}</p>
          </div>
        </div>
        <div class="topbar__info">
          <el-tag v-if="showDevMockBadge" type="warning" effect="dark">DEV MOCK</el-tag>
          <el-tag type="info">{{ currentUser.department }}</el-tag>
          <el-tag type="success">{{ roleLabel }}</el-tag>
          <el-dropdown>
            <div class="user-chip">
              <el-avatar>{{ currentUser.name.slice(0, 1) }}</el-avatar>
              <div>
                <strong>{{ currentUser.name }}</strong>
                <p>{{ currentUser.position }}</p>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goHome">返回首页</el-dropdown-item>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content-area">
        <router-view />
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue';
import { iconRegistry } from '@/constants/menus';
import { ROLE_MAP } from '@/constants/roles';
import { useAppStore } from '@/stores/app';

const route = useRoute();
const router = useRouter();
const store = useAppStore();
const mobileOpen = ref(false);

const breadcrumbItems = computed(() => {
  const title = String(route.meta.title || '').trim();
  return title ? ['首页', title] : ['首页'];
});

const roleLabel = computed(() => ROLE_MAP[store.user?.role] || '访客');
const currentUser = computed(() => ({
  name: store.user?.name || '访客',
  department: store.user?.department || '未分配部门',
  position: store.user?.position || '未分配岗位',
}));
const showDevMockBadge = import.meta.env.DEV && import.meta.env.VITE_FORCE_REMOTE_API !== 'true';

const logout = async () => {
  try {
    await store.logout();
  } catch {
    // ignore and proceed to local logout redirect
  }
  router.push('/login');
};

const goHome = () => {
  router.push(store.homePath);
};
</script>

<style scoped>
.shell-layout {
  display: grid;
  grid-template-columns: 272px 1fr;
  gap: 16px;
  padding: 16px;
  height: 100vh;
  box-sizing: border-box;
  align-items: stretch;
}

.sidebar {
  padding: 16px;
  height: calc(100vh - 32px);
  position: sticky;
  top: 16px;
}

.brand-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 8px 20px;
}

.brand-box__badge {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #409eff, #83beff);
  color: #fff;
  font-weight: 700;
}

.brand-box strong,
.topbar h2,
.user-chip strong {
  color: var(--hr-title);
}

.brand-box p,
.topbar p,
.user-chip p {
  margin: 4px 0 0;
  color: var(--hr-info);
  font-size: 12px;
}

.sidebar-menu {
  border-right: none;
}

.main-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px;
  min-width: 0;
  min-height: 0;
  height: calc(100vh - 32px);
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100px;
  box-sizing: border-box;
  padding: 10px 20px;
}

.topbar__left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.topbar h2 {
  margin: 6px 0 0;
  font-size: 18px;
}

.topbar__info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.topbar__info :deep(.el-tag:first-child) {
  letter-spacing: 0.08em;
  font-weight: 700;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.content-area {
  display: grid;
  gap: 16px;
  min-height: 0;
  overflow: auto;
  align-content: start;
  align-items: start;
}

.mobile-menu {
  display: none;
}

@media (max-width: 1024px) {
  .shell-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
    height: auto;
    position: relative;
    top: 0;
  }

  .sidebar.is-mobile-open {
    display: block;
  }

  .mobile-menu {
    display: inline-flex;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
