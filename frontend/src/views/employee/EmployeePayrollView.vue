<template>
  <div class="page-grid">
    <PageCard title="工资查询" description="查看历史工资条并导出 Excel。">
      <template #actions>
        <el-button type="primary" @click="handleExport">导出工资表</el-button>
      </template>
      <el-table :data="pagedRows" width="100%" v-loading="loading">
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
      <div class="payroll-page__pagination">
        <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="rows.length" layout="slot, prev, pager, next" background>
          <span class="payroll-page__total">共计 {{ rows.length }} 条</span>
        </el-pagination>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { getPayrollSummary } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const PAGE_SIZE = 15;
const rows = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pagedRows = computed(() => rows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getPayrollSummary();
    rows.value = result.data.records || [];
    currentPage.value = 1;
  } finally {
    loading.value = false;
  }
};

const handleExport = () => {
  exportWorkbook(rows.value.map((item) => ({
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
  })), '员工工资条', 'Payroll');
};

onMounted(loadData);
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

:deep(.page-card__body) {
  display: grid;
  gap: 16px;
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
</style>
