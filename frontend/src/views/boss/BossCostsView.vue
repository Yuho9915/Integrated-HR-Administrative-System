<template>
  <div class="page-grid">
    <div class="metric-grid">
      <MetricCard title="月度人力成本" :value="`¥${totalActual}`" tip="按实发工资实时汇总" icon="¥" />
      <MetricCard title="人均成本" :value="`¥${avgActual}`" tip="基于当前工资表自动计算" icon="均" />
      <MetricCard title="绩效占比" :value="performanceRatio" tip="绩效工资 / 总实发" icon="绩" />
      <MetricCard title="税费与扣减" :value="`¥${totalDeduction}`" tip="含个税、请假、考勤扣款" icon="扣" />
    </div>
    <PageCard title="人力成本总览" description="支持查看成本结构并导出。">
      <template #actions>
        <el-button type="primary" @click="handleExport">导出成本报表</el-button>
      </template>
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="employeeNo" label="工号" min-width="120" />
        <el-table-column prop="month" label="月份" min-width="120" />
        <el-table-column prop="basic" label="基本工资" min-width="120" />
        <el-table-column prop="performance" label="绩效工资" min-width="120" />
        <el-table-column prop="tax" label="个税" min-width="120" />
        <el-table-column label="扣减/税费" min-width="140">
          <template #default="scope">{{ (Number(scope.row.tax || 0) + Number(scope.row.leave_deduction || 0) + Number(scope.row.attendance_deduction || 0)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual" label="实际成本" min-width="140" />
      </el-table>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';
import { getPayrollSummary } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const rows = ref([]);
const loading = ref(false);

const totalActual = computed(() => rows.value.reduce((sum, item) => sum + Number(item.actual || 0), 0).toFixed(2));
const avgActual = computed(() => rows.value.length ? (Number(totalActual.value) / rows.value.length).toFixed(2) : '0.00');
const totalDeduction = computed(() => rows.value.reduce((sum, item) => sum + Number(item.tax || 0) + Number(item.leave_deduction || 0) + Number(item.attendance_deduction || 0), 0).toFixed(2));
const performanceRatio = computed(() => {
  const totalPerformance = rows.value.reduce((sum, item) => sum + Number(item.performance || 0), 0);
  const total = Number(totalActual.value);
  return total ? `${((totalPerformance / total) * 100).toFixed(1)}%` : '0.0%';
});

const loadRows = async () => {
  loading.value = true;
  try {
    const result = await getPayrollSummary();
    rows.value = result.data.records || [];
  } finally {
    loading.value = false;
  }
};

const handleExport = () => {
  exportWorkbook(rows.value, '人力成本总览', 'HumanCost');
};

onMounted(loadRows);
</script>
