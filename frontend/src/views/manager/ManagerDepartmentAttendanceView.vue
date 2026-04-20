<template>
  <div class="page-grid ep attendance-report-page">
    <section class="report-panel page-section panel">
      <div class="report-toolbar bar">
        <div class="report-toolbar__left fs">
          <el-date-picker v-model="monthFilter" type="month" value-format="YYYY-MM" placeholder="选择月份" class="filter-control month-control" />
          <el-input v-model="searchKeyword" placeholder="搜索姓名/工号" clearable class="search-control" />
        </div>
      </div>

      <div v-if="usingMockData" class="mock-tip">当前暂无真实考勤数据，以下为本部门模拟展示数据。</div>

      <div class="metrics-grid">
        <div class="metric-card">
          <span>正常出勤率</span>
          <strong>{{ displaySummaryRow?.attendanceRate || '暂无数据' }}</strong>
        </div>
        <div class="metric-card">
          <span>迟到次数</span>
          <strong>{{ displaySummaryRow?.lateTimes || 0 }}</strong>
        </div>
        <div class="metric-card">
          <span>早退次数</span>
          <strong>{{ displaySummaryRow?.earlyTimes || 0 }}</strong>
        </div>
        <div class="metric-card">
          <span>异常人数</span>
          <strong>{{ displaySummaryRow?.abnormalCount || 0 }}</strong>
        </div>
      </div>

      <div class="report-table-wrap">
        <el-table :data="pagedRows" :height="tableHeight" width="100%" v-loading="loading" class="full-table">
          <el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center" />
          <el-table-column prop="name" label="姓名" min-width="110" align="center" header-align="center" />
          <el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center" />
          <el-table-column prop="date" label="考勤日期" min-width="120" align="center" header-align="center" />
          <el-table-column prop="checkIn" label="上班时间" min-width="110" align="center" header-align="center" />
          <el-table-column prop="checkOut" label="下班时间" min-width="110" align="center" header-align="center" />
          <el-table-column prop="status" label="考勤状态" min-width="110" align="center" header-align="center" />
          <el-table-column prop="lateMinutes" label="迟到分钟" min-width="100" align="center" header-align="center" />
          <el-table-column prop="earlyMinutes" label="早退分钟" min-width="100" align="center" header-align="center" />
          <el-table-column prop="leaveType" label="请假类型" min-width="100" align="center" header-align="center" />
          <el-table-column prop="remark" label="备注" min-width="180" align="center" header-align="center" show-overflow-tooltip />
          <template #empty>
            <el-empty description="暂无本部门考勤数据" />
          </template>
        </el-table>
      </div>
      <div class="report-pagination pg">
        <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="displayRows.length" layout="slot, prev, pager, next" background>
          <span class="report-pagination__total ttl">共计 {{ displayRows.length }} 条</span>
        </el-pagination>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { getAttendanceOverview } from '@/api/modules';
import { useAppStore } from '@/stores/app';

const PAGE_SIZE = 10;
const tableHeight = 'calc(100vh - 420px)';
const appStore = useAppStore();
const { user } = storeToRefs(appStore);
const loading = ref(false);
const rawRows = ref([]);
const overviewRows = ref([]);
const currentPage = ref(1);
const monthFilter = ref('2026-04');
const searchKeyword = ref('');
const departmentName = computed(() => user.value?.department || '未分配部门');
const normalizeMonth = (item = {}) => String(item.month || item.date || '').slice(0, 7);
const inferDepartment = (item = {}) => {
  if (item.department) return item.department;
  const employeeNo = String(item.employeeNo || item.employee_no || '');
  if (employeeNo.startsWith('HR')) return '综合管理部';
  if (employeeNo.startsWith('OPS')) return '运营中心';
  if (employeeNo.startsWith('DEV')) return '产品技术部';
  if (employeeNo.startsWith('MKT')) return '市场部';
  if (employeeNo.startsWith('SAL')) return '销售部';
  if (employeeNo.startsWith('FIN')) return '财务部';
  return '未分组';
};
const createMockRows = (department) => ([
  { employeeNo: 'DEV-1001', name: '陈晓雨', department, date: '2026-04-18', checkIn: '08:57', checkOut: '18:06', status: '正常', lateMinutes: 0, earlyMinutes: 0, leaveType: '', remark: '按时出勤' },
  { employeeNo: 'DEV-1002', name: '李文博', department, date: '2026-04-18', checkIn: '09:12', checkOut: '18:11', status: '迟到', lateMinutes: 12, earlyMinutes: 0, leaveType: '', remark: '早高峰延误' },
  { employeeNo: 'DEV-1003', name: '王一诺', department, date: '2026-04-18', checkIn: '08:49', checkOut: '17:42', status: '早退', lateMinutes: 0, earlyMinutes: 18, leaveType: '', remark: '外出就医提前离岗' },
  { employeeNo: 'DEV-1004', name: '赵嘉宁', department, date: '2026-04-18', checkIn: '—', checkOut: '—', status: '请假', lateMinutes: 0, earlyMinutes: 0, leaveType: '病假', remark: '请假 1 天' },
  { employeeNo: 'DEV-1005', name: '孙可欣', department, date: '2026-04-18', checkIn: '08:55', checkOut: '18:20', status: '正常', lateMinutes: 0, earlyMinutes: 0, leaveType: '', remark: '项目冲刺正常出勤' },
  { employeeNo: 'DEV-1006', name: '周泽宇', department, date: '2026-04-18', checkIn: '09:05', checkOut: '18:03', status: '迟到', lateMinutes: 5, earlyMinutes: 0, leaveType: '', remark: '打卡延迟' },
]);
const buildMockSummary = (rows) => ({
  department: departmentName.value,
  attendanceRate: rows.length ? `${Math.round((rows.filter((item) => item.status !== '请假').length / rows.length) * 100)}%` : '暂无数据',
  lateTimes: rows.filter((item) => item.status === '迟到').length,
  earlyTimes: rows.filter((item) => item.status === '早退').length,
  abnormalCount: rows.filter((item) => item.status !== '正常').length,
});

const normalizedRows = computed(() => rawRows.value.map((item) => ({
  ...item,
  department: inferDepartment(item),
  employeeNo: item.employeeNo || item.employee_no || '',
  leaveType: item.leaveType || item.leave_type || item.type || '',
})).filter((item) => item.department === departmentName.value));

const filteredRows = computed(() => normalizedRows.value.filter((item) => {
  const monthMatch = !monthFilter.value || normalizeMonth(item) === monthFilter.value;
  const keyword = searchKeyword.value.trim().toLowerCase();
  const keywordMatch = !keyword || String(item.name || '').toLowerCase().includes(keyword) || String(item.employeeNo || '').toLowerCase().includes(keyword);
  return monthMatch && keywordMatch;
}));
const mockRows = computed(() => createMockRows(departmentName.value).filter((item) => {
  const monthMatch = !monthFilter.value || normalizeMonth(item) === monthFilter.value;
  const keyword = searchKeyword.value.trim().toLowerCase();
  const keywordMatch = !keyword || String(item.name || '').toLowerCase().includes(keyword) || String(item.employeeNo || '').toLowerCase().includes(keyword);
  return monthMatch && keywordMatch;
}));
const usingMockData = computed(() => !loading.value && filteredRows.value.length === 0);
const displayRows = computed(() => usingMockData.value ? mockRows.value : filteredRows.value);
const pagedRows = computed(() => displayRows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));
const summaryRow = computed(() => overviewRows.value.find((item) => item.department === departmentName.value) || null);
const displaySummaryRow = computed(() => usingMockData.value ? buildMockSummary(mockRows.value) : summaryRow.value);
watch([monthFilter, searchKeyword], () => { currentPage.value = 1; });

onMounted(async () => {
  loading.value = true;
  try {
    const result = await getAttendanceOverview({ suppressErrorMessage: true });
    rawRows.value = result.data?.records || [];
    overviewRows.value = result.data?.overview || result.data?.departments || [];
  } catch {
    rawRows.value = [];
    overviewRows.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.ep{display:grid;gap:16px;height:calc(100vh - 148px)}.panel{display:grid;grid-template-rows:auto auto auto 1fr auto;gap:16px;padding:16px;min-height:0;height:100%;box-sizing:border-box}.bar{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.fs{display:flex;align-items:center;gap:12px;flex-wrap:nowrap}.month-control{width:180px;flex:0 0 180px}.search-control{width:260px;flex:0 0 260px}.mock-tip{padding:12px 14px;border-radius:12px;background:linear-gradient(180deg,#fff9f1 0%,#fff2df 100%);border:1px solid #f6d8a8;color:#9a6a16;font-size:13px}.metrics-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric-card{display:grid;gap:8px;padding:16px;border-radius:16px;background:linear-gradient(180deg,#fff 0%,#f6f9ff 100%);border:1px solid rgba(120,146,190,.16)}.metric-card span{font-size:12px;color:#7f8da3}.metric-card strong{font-size:24px;color:#20324a}.report-table-wrap{min-height:0;overflow:hidden}.report-table-wrap :deep(.el-table th.el-table__cell){height:48px;padding:10px 0}.report-table-wrap :deep(.el-table .el-table__cell){padding:10px 0}.report-table-wrap :deep(.el-table .cell){line-height:24px}.pg{display:flex;justify-content:flex-end;position:sticky;bottom:0;z-index:2;padding-top:16px;background:transparent}.pg :deep(.el-pagination){padding:0;border-radius:0;background:transparent;box-shadow:none;border:none}.pg :deep(.el-pagination.is-background){background:transparent;border:none;box-shadow:none}.pg :deep(.btn-prev),.pg :deep(.btn-next),.pg :deep(.el-pager li){border-radius:8px}.pg :deep(.el-pager li.is-active){background:#409EFF;color:#fff}.ttl{display:inline-flex;align-items:center;padding:0 12px;color:var(--hr-info);font-size:13px}@media (max-width:767px){.ep,.panel{height:auto;min-height:auto}.fs{flex-wrap:wrap}.month-control,.search-control{width:100%;flex:1 1 100%}.metrics-grid{grid-template-columns:1fr}.pg{position:static;justify-content:center}}
</style>
