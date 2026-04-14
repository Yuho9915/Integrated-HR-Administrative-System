<template>
  <div class="page-grid">
    <div class="metric-grid">
      <MetricCard title="A档人数" :value="`${distribution.A || 0}`" tip="动态统计" icon="A" />
      <MetricCard title="B档人数" :value="`${distribution.B || 0}`" tip="动态统计" icon="B" />
      <MetricCard title="校验结果" :value="passedLabel" tip="基于规则引擎 + AI" icon="验" />
      <MetricCard title="复核建议" :value="ruleHint" tip="关注 A 档比例与异常波动" icon="议" />
    </div>
    <PageCard title="AI 绩效校验" description="提交后调用后端接口校验等级分布、连续异常与超标情况。">
      <el-alert :title="message" :type="passed ? 'success' : 'warning'" :closable="false" show-icon />
      <div style="margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap;">
        <el-button type="primary" :loading="loading" @click="submitCheck">提交 AI 校验</el-button>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';
import { checkPerformance, getPerformanceSummary } from '@/api/modules';

const loading = ref(false);
const message = ref('当前分布符合绩效规则，可执行批量保存。');
const distribution = ref({ A: 0, B: 0, C: 0, D: 0 });
const passed = ref(true);

const passedLabel = computed(() => (passed.value ? '通过' : '待复核'));
const ruleHint = computed(() => (passed.value ? '分布合理' : 'A档占比或异常波动过高'));

const submitCheck = async () => {
  loading.value = true;
  try {
    const summary = await getPerformanceSummary();
    const records = (summary.data.records || []).map((item) => ({
      ...item,
      score: item.totalScore || item.score || 0,
    }));
    const result = await checkPerformance({ cycle: '2026-04', records });
    message.value = result.data.comment;
    distribution.value = result.data.distribution || distribution.value;
    passed.value = Boolean(result.data.passed);
  } finally {
    loading.value = false;
  }
};
</script>
