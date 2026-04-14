<template>
  <div class="page-grid">
    <PageCard title="部门绩效录入" description="按部门成员录入绩效分数、自评与评价，提交后写入当前绩效模块。">
      <template #actions>
        <el-space wrap>
          <el-date-picker v-model="monthValue" type="month" placeholder="考核周期" />
          <el-button type="primary" :loading="saving" @click="submit">批量保存</el-button>
        </el-space>
      </template>
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="employeeNo" label="工号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column label="业绩" min-width="120"><template #default="s"><el-input-number v-model="s.row.performanceScore" :min="0" :max="100" style="width:100%" @change="syncRow(s.row)" /></template></el-table-column>
        <el-table-column label="态度" min-width="120"><template #default="s"><el-input-number v-model="s.row.attitudeScore" :min="0" :max="100" style="width:100%" @change="syncRow(s.row)" /></template></el-table-column>
        <el-table-column label="能力" min-width="120"><template #default="s"><el-input-number v-model="s.row.abilityScore" :min="0" :max="100" style="width:100%" @change="syncRow(s.row)" /></template></el-table-column>
        <el-table-column prop="totalScore" label="总分" min-width="100" />
        <el-table-column label="等级" min-width="120"><template #default="s"><el-select v-model="s.row.grade" @change="syncCoef(s.row)"><el-option label="S" value="S" /><el-option label="A" value="A" /><el-option label="B" value="B" /><el-option label="C" value="C" /><el-option label="D" value="D" /></el-select></template></el-table-column>
        <el-table-column label="自评" min-width="220"><template #default="s"><el-input v-model="s.row.selfReview" /></template></el-table-column>
        <el-table-column label="上级评价" min-width="220"><template #default="s"><el-input v-model="s.row.managerReview" /></template></el-table-column>
      </el-table>
    </PageCard>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { checkPerformance, getPerformanceSummary } from '@/api/modules';

const rows = ref([]);
const loading = ref(false);
const saving = ref(false);
const monthValue = ref('2026-04');

const syncCoef = (row) => {
  row.coefficient = ({ S: 1.5, A: 1.2, B: 1, C: 0.8, D: 0.5 })[row.grade] || 1;
};

const syncRow = (row) => {
  row.totalScore = Number(((Number(row.performanceScore || 0) * 0.6) + (Number(row.attitudeScore || 0) * 0.2) + (Number(row.abilityScore || 0) * 0.2)).toFixed(2));
  row.grade = row.totalScore >= 90 ? 'S' : row.totalScore >= 80 ? 'A' : row.totalScore >= 70 ? 'B' : row.totalScore >= 60 ? 'C' : 'D';
  syncCoef(row);
};

const loadRows = async () => {
  loading.value = true;
  try {
    const result = await getPerformanceSummary();
    rows.value = (result.data.records || []).map((item) => ({
      ...item,
      performanceScore: Number(item.performanceScore || 0),
      attitudeScore: Number(item.attitudeScore || 0),
      abilityScore: Number(item.abilityScore || 0),
      totalScore: Number(item.totalScore || item.score || 0),
      selfReview: item.selfReview || '',
      managerReview: item.managerReview || '',
      status: '待审核',
    }));
  } finally {
    loading.value = false;
  }
};

watch(monthValue, loadRows);

const submit = async () => {
  saving.value = true;
  try {
    const result = await checkPerformance({ cycle: monthValue.value, records: rows.value });
    ElMessage.success(result.message);
  } finally {
    saving.value = false;
  }
};

onMounted(loadRows);
</script>
