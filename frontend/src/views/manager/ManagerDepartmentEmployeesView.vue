<template>
  <div class="page-grid ep">
    <section class="page-section panel">
      <div class="bar">
        <div class="fs">
          <el-input v-model="keyword" placeholder="搜索姓名/工号/岗位" clearable style="width:260px" />
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width:160px">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </div>
      </div>
      <div class="tb">
        <el-table :data="pagedRows" :height="tableHeight" width="100%" v-loading="loading">
          <el-table-column prop="employee_no" label="工号" min-width="120" align="center" header-align="center" />
          <el-table-column prop="name" label="姓名" min-width="120" align="center" header-align="center" />
          <el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center" />
          <el-table-column prop="position" label="岗位" min-width="140" align="center" header-align="center" />
          <el-table-column prop="roleLabel" label="角色" min-width="120" align="center" header-align="center" />
          <el-table-column prop="status" label="状态" min-width="110" align="center" header-align="center" />
          <el-table-column prop="phone" label="手机号" min-width="140" align="center" header-align="center" />
          <el-table-column prop="hire_date" label="入职日期" min-width="130" align="center" header-align="center" />
        </el-table>
      </div>
      <div class="pg">
        <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="filteredRows.length" layout="slot, prev, pager, next" background>
          <span class="ttl">共计 {{ filteredRows.length }} 条</span>
        </el-pagination>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { getEmployees } from '@/api/modules';
import { useAppStore } from '@/stores/app';
import { ROLE_MAP } from '@/constants/roles';

const PAGE_SIZE = 15;
const tableHeight = 'calc(100vh - 320px)';
const appStore = useAppStore();
const { user } = storeToRefs(appStore);
const loading = ref(false);
const rows = ref([]);
const keyword = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const statusOptions = ['在职', '试用', '离职'];
const departmentName = computed(() => user.value?.department || '未分配部门');

const filteredRows = computed(() => rows.value.filter((item) => {
  const keywordText = keyword.value.trim().toLowerCase();
  const keywordMatch = !keywordText || String(item.name || '').toLowerCase().includes(keywordText) || String(item.employee_no || '').toLowerCase().includes(keywordText) || String(item.position || '').toLowerCase().includes(keywordText);
  const statusMatch = !statusFilter.value || item.status === statusFilter.value;
  return keywordMatch && statusMatch;
}));
const pagedRows = computed(() => filteredRows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));
watch([keyword, statusFilter], () => { currentPage.value = 1; });

onMounted(async () => {
  loading.value = true;
  try {
    const result = await getEmployees();
    rows.value = (result.data || [])
      .filter((item) => item.department === departmentName.value)
      .map((item) => ({ ...item, roleLabel: ROLE_MAP[item.role] || '员工' }));
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.ep{display:grid;gap:16px;height:calc(100vh - 148px)}.panel{display:grid;grid-template-rows:auto 1fr auto;gap:16px;padding:16px;min-height:0;height:100%;box-sizing:border-box}.bar{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.fs{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.tb{min-height:0;overflow:hidden}.tb :deep(.el-table th.el-table__cell){height:48px;padding:10px 0}.tb :deep(.el-table .el-table__cell){padding:10px 0}.tb :deep(.el-table .cell){line-height:24px}.pg{display:flex;justify-content:flex-end;position:sticky;bottom:0;z-index:2;padding-top:16px;background:transparent}.pg :deep(.el-pagination){padding:0;border-radius:0;background:transparent;box-shadow:none;border:none}.pg :deep(.el-pagination.is-background){background:transparent;border:none;box-shadow:none}.pg :deep(.btn-prev),.pg :deep(.btn-next),.pg :deep(.el-pager li){border-radius:8px}.pg :deep(.el-pager li.is-active){background:#409EFF;color:#fff}.ttl{display:inline-flex;align-items:center;padding:0 12px;color:var(--hr-info);font-size:13px}@media (max-width:767px){.ep,.panel{height:auto;min-height:auto}.pg{position:static;justify-content:center}}
</style>
