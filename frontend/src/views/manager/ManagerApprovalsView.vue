<template>
  <div class="page-grid">
    <PageCard title="本部门审批" description="审批请假、加班、绩效异议等部门事项。">
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="applicant" label="申请人" min-width="120" />
        <el-table-column prop="type" label="申请类型" min-width="120" />
        <el-table-column prop="duration" label="时长" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="120" />
        <el-table-column label="操作" min-width="180">
          <template #default="scope">
            <el-space>
              <el-button type="primary" size="small" @click="handleDecision(scope.row, '已通过')">通过</el-button>
              <el-button size="small" @click="handleDecision(scope.row, '已驳回')">驳回</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { decideApproval, getApprovalOverview } from '@/api/modules';

const rows = ref([]);
const loading = ref(false);

const loadRows = async () => {
  loading.value = true;
  try {
    const result = await getApprovalOverview();
    rows.value = (result.data.records || []).filter((item) => item.level === 'manager' || item.category === '人事审批');
  } finally {
    loading.value = false;
  }
};

const handleDecision = async (row, decision) => {
  await decideApproval(row.id, { decision, comment: decision });
  ElMessage.success(`已${decision}`);
  loadRows();
};

onMounted(loadRows);
</script>
