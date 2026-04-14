<template>
  <div class="page-grid">
    <PageCard title="绩效查询" description="查看当前与历史绩效结果及评价内容。">
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="period" label="考核周期" min-width="140" />
        <el-table-column prop="performanceScore" label="业绩" min-width="90" />
        <el-table-column prop="attitudeScore" label="态度" min-width="90" />
        <el-table-column prop="abilityScore" label="能力" min-width="90" />
        <el-table-column prop="totalScore" label="总分" min-width="100" />
        <el-table-column prop="grade" label="等级" min-width="100" />
        <el-table-column prop="reviewer" label="考核人" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="120" />
        <el-table-column prop="selfReview" label="员工自评" min-width="220" show-overflow-tooltip />
        <el-table-column prop="managerReview" label="上级评价" min-width="220" show-overflow-tooltip />
      </el-table>
    </PageCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { getPerformanceSummary } from '@/api/modules';

const rows = ref([]);
const loading = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getPerformanceSummary();
    rows.value = (result.data.records || []).map((item) => ({
      ...item,
      totalScore: item.totalScore || item.score || 0,
    }));
  } finally {
    loading.value = false;
  }
};

onMounted(loadData);
</script>
