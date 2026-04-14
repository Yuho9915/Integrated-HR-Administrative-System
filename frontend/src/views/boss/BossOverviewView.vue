<template>
  <div class="page-grid">
    <div class="metric-grid">
      <MetricCard v-for="item in cards" :key="item.label" :title="item.label" :value="item.value" :tip="item.tip" icon="览" />
    </div>

    <div class="two-column dashboard-panels">
      <PageCard title="经营快照" description="老板查看本月关键经营、人力、考勤指标。">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总人数">{{ headcount }} 人</el-descriptions-item>
          <el-descriptions-item label="待终审事项">{{ pendingApprovals }} 项</el-descriptions-item>
          <el-descriptions-item label="考勤异常">{{ abnormalCount }} 条</el-descriptions-item>
          <el-descriptions-item label="月度实发">¥{{ payrollTotal }}</el-descriptions-item>
        </el-descriptions>
      </PageCard>

      <PageCard title="趋势概览" description="按月观察人力成本趋势。">
        <div class="trend-list">
          <div v-for="item in trend" :key="item.month" class="trend-item">
            <span>{{ item.month }}</span>
            <div class="trend-bar">
              <div class="trend-bar__fill" :style="{ width: `${item.width}%` }"></div>
            </div>
            <strong>¥{{ item.amount }}</strong>
          </div>
        </div>
      </PageCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';
import { getApprovalOverview, getDashboardSummary, getPayrollSummary } from '@/api/modules';

const cards = ref([]);
const pendingApprovals = ref(0);
const payrollRows = ref([]);

const headcount = computed(() => Number(cards.value.find((item) => item.label === '总人数')?.value || 0));
const abnormalCount = computed(() => Number(cards.value.find((item) => item.label === '考勤异常')?.value || 0));
const payrollTotal = computed(() => payrollRows.value.reduce((sum, item) => sum + Number(item.actual || 0), 0).toFixed(2));
const trend = computed(() => {
  const base = Number(payrollTotal.value || 0);
  const values = [0.92, 0.96, 1, 1.03].map((factor, index) => ({
    month: `${index + 1}月`,
    amount: (base * factor).toFixed(2),
  }));
  const max = Math.max(...values.map((item) => Number(item.amount)), 1);
  return values.map((item) => ({ ...item, width: Math.round((Number(item.amount) / max) * 100) }));
});

onMounted(async () => {
  const [dashboard, approvals, payroll] = await Promise.all([getDashboardSummary(), getApprovalOverview(), getPayrollSummary()]);
  cards.value = dashboard.data.cards || [];
  pendingApprovals.value = (approvals.data.records || []).filter((item) => item.status === '待审批').length;
  payrollRows.value = payroll.data.records || [];
});
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

.dashboard-panels {
  align-items: stretch;
}

.trend-list {
  display: grid;
  gap: 14px;
}

.trend-item {
  display: grid;
  grid-template-columns: 48px 1fr 96px;
  gap: 12px;
  align-items: center;
}

.trend-bar {
  height: 10px;
  border-radius: 999px;
  background: #eef4ff;
  overflow: hidden;
}

.trend-bar__fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #409eff, #8ac0ff);
}

@media (max-width: 767px) {
  .trend-item {
    grid-template-columns: 44px 1fr 82px;
  }
}
</style>
