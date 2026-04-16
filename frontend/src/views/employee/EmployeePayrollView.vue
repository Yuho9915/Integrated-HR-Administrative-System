<template>
  <div class="page-grid payroll-page">
    <PageCard title="工资查询" hide-header>
      <template #actions>
        <el-button type="primary" :disabled="!verified" @click="handleExport">导出工资表</el-button>
      </template>

      <div v-if="!verified" class="payroll-page__guard">
        <div class="payroll-page__guard-card">
          <h3>请输入二次密码</h3>
          <p>为保护工资信息安全，进入工资查询页前需要再次验证登录密码。</p>
          <el-input
            :key="passwordInputKey"
            v-model="secondaryPassword"
            type="password"
            show-password
            clearable
            autocomplete="new-password"
            name="payroll-secondary-password"
            placeholder="请输入二次密码"
            class="payroll-page__password"
            @keyup.enter="verifyAccess"
          />
          <el-button type="primary" :loading="verifying" @click="verifyAccess">确认进入</el-button>
        </div>
      </div>

      <template v-else>
        <div class="payroll-page__table-shell">
          <div class="payroll-page__table-wrap">
            <el-table :data="pagedRows" width="100%" :height="TABLE_HEIGHT" v-loading="loading">
              <template #empty>
                <el-empty description="暂无工资记录" />
              </template>
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
          <div class="payroll-page__pagination">
            <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="rows.length" layout="slot, prev, pager, next" background>
              <span class="payroll-page__total">共计 {{ rows.length }} 条</span>
            </el-pagination>
          </div>
        </div>
      </template>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { getPayrollSummary, verifyPasswordApi } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const PAGE_SIZE = 10;
const TABLE_HEIGHT = 520;
const rows = ref([]);
const loading = ref(false);
const verifying = ref(false);
const verified = ref(false);
const secondaryPassword = ref('');
const passwordInputKey = ref(0);
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

const verifyAccess = async () => {
  if (!secondaryPassword.value) {
    ElMessage.warning('请输入二次密码');
    return;
  }
  verifying.value = true;
  try {
    await verifyPasswordApi({ password: secondaryPassword.value });
    verified.value = true;
    secondaryPassword.value = '';
    await loadData();
    ElMessage.success('验证通过');
  } catch {
    verified.value = false;
  } finally {
    verifying.value = false;
  }
};

const handleExport = () => {
  if (!verified.value) return;
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

onMounted(() => {
  verified.value = false;
  secondaryPassword.value = '';
  passwordInputKey.value += 1;
});
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

.payroll-page :deep(.page-card__body) {
  display: grid;
  min-height: 620px;
}

.payroll-page__guard {
  display: grid;
  place-items: center;
  min-height: 520px;
}

.payroll-page__guard-card {
  width: min(420px, 100%);
  display: grid;
  gap: 14px;
  padding: 24px;
  border-radius: 18px;
  border: 1px solid rgba(64, 158, 255, 0.12);
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
}

.payroll-page__guard-card h3 {
  margin: 0;
  color: var(--hr-title);
}

.payroll-page__guard-card p {
  margin: 0;
  color: var(--hr-info);
  line-height: 1.7;
  font-size: 13px;
}

.payroll-page__password {
  width: 100%;
}

.payroll-page__table-shell {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 16px;
  min-height: 0;
}

.payroll-page__table-wrap {
  min-height: 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.payroll-page__pagination {
  display: flex;
  justify-content: flex-end;
  position: sticky;
  bottom: 0;
  z-index: 2;
  background: #fff;
  padding-top: 8px;
}

.payroll-page__total {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--hr-info);
  font-size: 13px;
}
</style>
