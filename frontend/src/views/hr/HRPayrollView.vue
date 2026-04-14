<template>
  <div class="page-grid ep">
    <div class="metric-grid">
      <MetricCard title="本月应发" :value="`¥${totalPreTax}`" tip="全员税前工资实时汇总" icon="¥" />
      <MetricCard title="扣减合计" :value="`¥${totalDeduction}`" tip="请假/社保个人/公积金个人/个税/考勤扣减" icon="扣" />
      <MetricCard title="异常工资" :value="`${abnormalCount}条`" tip="低于 0 或低于 5000 预警" icon="!" />
      <MetricCard title="工资条完成" :value="completionRate" tip="当前已生成工资记录" icon="单" />
    </div>

    <PageCard title="薪酬核算" description="AI 根据考勤、绩效、补贴、个税自动汇总工资表。" class="page-section panel payroll-card payroll-card--plain-header payroll-card--headerless">
      <div class="payroll-toolbar bar">
        <div class="payroll-filters fs">
          <el-input v-model="keyword" placeholder="搜索工号/员工姓名" clearable class="payroll-filter__search" />
          <el-date-picker v-model="selectedMonth" type="month" value-format="YYYY-MM" placeholder="选择月份" class="payroll-filter__month" />
          <el-select v-model="selectedDepartment" placeholder="选择部门" clearable class="payroll-filter__department">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </div>

        <el-space wrap class="payroll-toolbar__actions bar-actions">
          <el-button type="primary" :loading="calculating" @click="runCalculate">一键核算</el-button>
          <el-button @click="handleExport">导出工资表</el-button>
        </el-space>
      </div>

      <div class="tb">
        <el-table :data="pagedRows" width="100%" :height="TABLE_HEIGHT" v-loading="loading">
        <el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center" />
        <el-table-column prop="name" label="员工姓名" min-width="120" align="center" header-align="center" />
        <el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center" />
        <el-table-column prop="month" label="月份" min-width="120" align="center" header-align="center" />
        <el-table-column prop="basic" label="基本工资" min-width="120" align="center" header-align="center" />
        <el-table-column prop="subsidy" label="补贴" min-width="110" align="center" header-align="center" />
        <el-table-column prop="performance_coefficient" label="绩效系数" min-width="110" align="center" header-align="center" />
        <el-table-column prop="performance" label="绩效工资" min-width="120" align="center" header-align="center" />
        <el-table-column prop="overtime_pay" label="加班工资" min-width="120" align="center" header-align="center" />
        <el-table-column prop="attendance_deduction" label="考勤扣款" min-width="120" align="center" header-align="center" />
        <el-table-column prop="leave_deduction" label="请假扣款" min-width="120" align="center" header-align="center" />
        <el-table-column prop="pre_tax_salary" label="应发工资" min-width="120" align="center" header-align="center" />
        <el-table-column prop="social_security_personal" label="社保个人" min-width="120" align="center" header-align="center" />
        <el-table-column prop="housing_fund_personal" label="公积金个人" min-width="130" align="center" header-align="center" />
        <el-table-column prop="social_security_employer" label="社保单位" min-width="120" align="center" header-align="center" />
        <el-table-column prop="housing_fund_employer" label="公积金单位" min-width="130" align="center" header-align="center" />
        <el-table-column prop="tax" label="个税" min-width="110" align="center" header-align="center" />
        <el-table-column prop="actual" label="实发工资" min-width="140" align="center" header-align="center" />
      </el-table>
      </div>

      <div class="payroll-page__pagination pg">
        <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="filteredRows.length" layout="slot, prev, pager, next" background>
          <span class="payroll-page__total ttl">共计 {{ filteredRows.length }} 条</span>
        </el-pagination>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';
import { calculatePayroll, getEmployeeMeta, getPayrollSummary } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const PAGE_SIZE = 10;
const TABLE_HEIGHT = 'calc(100vh - 360px)';
const rows = ref([]);
const loading = ref(false);
const calculating = ref(false);
const currentPage = ref(1);
const keyword = ref('');
const selectedMonth = ref(new Date().toISOString().slice(0, 7));
const selectedDepartment = ref('');
const departmentOptions = ref([]);

const normalizeRow = (item) => ({
  ...item,
  employeeNo: item.employeeNo || item.employee_no || '',
  name: item.name || '',
  month: item.month || selectedMonth.value,
  department: item.department || item.dept || '',
});

const filteredRows = computed(() => rows.value.filter((item) => {
  const matchesKeyword = !keyword.value || item.employeeNo.includes(keyword.value) || item.name.includes(keyword.value);
  const matchesMonth = !selectedMonth.value || item.month === selectedMonth.value;
  const matchesDepartment = !selectedDepartment.value || item.department === selectedDepartment.value;
  return matchesKeyword && matchesMonth && matchesDepartment;
}));

const pagedRows = computed(() => filteredRows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));
const totalPreTax = computed(() => filteredRows.value.reduce((sum, item) => sum + Number(item.pre_tax_salary || 0), 0).toFixed(2));
const totalDeduction = computed(() => filteredRows.value.reduce((sum, item) => sum + Number(item.tax || 0) + Number(item.leave_deduction || 0) + Number(item.attendance_deduction || 0) + Number(item.social_security_personal || 0) + Number(item.housing_fund_personal || 0), 0).toFixed(2));
const abnormalCount = computed(() => filteredRows.value.filter((item) => Number(item.actual || 0) < 0 || Number(item.actual || 0) < 5000).length);
const completionRate = computed(() => `${filteredRows.value.length ? Math.min(100, Math.round((filteredRows.value.length / 48) * 100)) : 0}%`);

watch([keyword, selectedMonth, selectedDepartment], () => {
  currentPage.value = 1;
});

const loadMeta = async () => {
  const result = await getEmployeeMeta();
  departmentOptions.value = result.data?.departments || [];
};

const loadRows = async () => {
  loading.value = true;
  try {
    const result = await getPayrollSummary();
    rows.value = (result.data.records || []).map(normalizeRow);
    currentPage.value = 1;
  } finally {
    loading.value = false;
  }
};

const runCalculate = async () => {
  calculating.value = true;
  try {
    const result = await calculatePayroll({ month: selectedMonth.value || new Date().toISOString().slice(0, 7) });
    ElMessage.success(result.message);
    rows.value = (result.data.records || []).map(normalizeRow);
    currentPage.value = 1;
  } finally {
    calculating.value = false;
  }
};

const handleExport = () => {
  exportWorkbook(filteredRows.value.map((item) => ({
    工号: item.employeeNo,
    员工姓名: item.name,
    部门: item.department,
    月份: item.month,
    基本工资: item.basic,
    补贴: item.subsidy,
    绩效系数: item.performance_coefficient,
    绩效工资: item.performance,
    加班工资: item.overtime_pay,
    考勤扣款: item.attendance_deduction,
    请假扣款: item.leave_deduction,
    应发工资: item.pre_tax_salary,
    社保个人部分: item.social_security_personal,
    公积金个人部分: item.housing_fund_personal,
    社保单位部分: item.social_security_employer,
    公积金单位部分: item.housing_fund_employer,
    个税: item.tax,
    实发工资: item.actual,
    绩效等级: item.grade,
  })), '薪酬核算总表', 'PayrollSummary');
};

onMounted(async () => {
  await Promise.all([loadMeta(), loadRows()]);
});
</script>

<style scoped>
.ep {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px;
  height: calc(100vh - 148px);
}

.panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 16px;
  padding: 16px;
  min-height: 0;
  height: 100%;
  box-sizing: border-box;
  align-content: stretch;
}

.bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.fs,
.bar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tb {
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.pg {
  display: flex;
  justify-content: flex-end;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding-top: 16px;
  background: transparent;
}

.pg :deep(.el-pagination) {
  padding: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  border: none;
}

.pg :deep(.el-pagination.is-background) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.pg :deep(.btn-prev),
.pg :deep(.btn-next),
.pg :deep(.el-pager li) {
  border-radius: 8px;
}

.pg :deep(.el-pager li.is-active) {
  background: #409EFF;
  color: #fff;
}

.ttl {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--hr-info);
  font-size: 13px;
}

.page-grid {
  display: grid;
  gap: 16px;
}

:deep(.page-card__body) {
  display: grid;
  gap: 16px;
}

.payroll-card--plain-header :deep(.page-card__header > div:first-child) {
  display: none;
}

.payroll-card--headerless :deep(.page-card__header) {
  display: none;
}

.payroll-card--headerless :deep(.page-card__body) {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 16px;
  min-height: 0;
  height: 100%;
  padding-top: 16px;
}

.payroll-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.payroll-filters {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.payroll-toolbar__actions {
  margin-left: auto;
}

.payroll-filter__search {
  width: 240px;
}

.payroll-filter__month,
.payroll-filter__department {
  width: 180px;
}

.payroll-page__pagination {
  display: flex;
  justify-content: flex-end;
}

.payroll-page__total {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--hr-info);
  font-size: 13px;
}

:deep(.el-table th.el-table__cell) {
  height: 48px;
  padding: 10px 0;
}

:deep(.el-table .el-table__cell) {
  padding: 10px 0;
}

:deep(.el-table .cell) {
  line-height: 24px;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focused),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #409EFF inset;
}

@media (max-width: 900px) {
  .ep,
  .payroll-card,
  .panel,
  .payroll-card--headerless :deep(.page-card__body),
  .tb {
    height: auto;
  }

  .payroll-toolbar,
  .payroll-filters {
    align-items: stretch;
  }

  .payroll-toolbar__actions {
    margin-left: 0;
  }

  .payroll-filter__search,
  .payroll-filter__month,
  .payroll-filter__department {
    width: 100%;
  }
}
</style>
