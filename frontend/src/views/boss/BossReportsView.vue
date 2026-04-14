<template>
  <div class="page-grid">
    <PageCard title="图表报表" description="支持导出 Excel，查看部门人力、考勤、绩效与行政统计。">
      <template #actions>
        <el-button type="primary" @click="handleExport">导出图表报表</el-button>
      </template>
      <div class="three-column reports-grid">
        <div class="page-section chart-card" v-for="card in chartCards" :key="card.name">
          <p class="chart-card__label">{{ card.name }}</p>
          <strong>{{ card.value }}</strong>
          <span>{{ card.tip }}</span>
        </div>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { getReportsSummary } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const chartCards = ref([]);

const loadRows = async () => {
  const result = await getReportsSummary();
  chartCards.value = result.data.charts || [];
};

const handleExport = () => {
  exportWorkbook(chartCards.value, '老板图表报表', 'BossReports');
};

onMounted(loadRows);
</script>

<style scoped>
.page-grid {
  display: grid;
}

.reports-grid {
  align-items: stretch;
}

.chart-card {
  padding: 18px;
  display: grid;
  gap: 6px;
}

.chart-card__label {
  margin: 0;
}

.chart-card strong {
  display: block;
  margin: 12px 0 8px;
  color: var(--hr-title);
  font-size: 22px;
}

.chart-card span {
  font-size: 12px;
  color: var(--hr-info);
}
</style>
