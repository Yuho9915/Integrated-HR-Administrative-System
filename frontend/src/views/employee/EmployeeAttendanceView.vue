<template>
  <div class="page-grid">
    <PageCard title="考勤查询" description="查询本月考勤明细与异常情况。">
      <template #actions>
        <el-space wrap>
          <el-date-picker v-model="month" type="month" placeholder="选择月份" />
          <el-button @click="loadData">刷新</el-button>
        </el-space>
      </template>
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="date" label="日期" min-width="140" />
        <el-table-column prop="type" label="类型" min-width="120" />
        <el-table-column prop="checkIn" label="上班打卡" min-width="120" />
        <el-table-column prop="checkOut" label="下班打卡" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === '正常' ? 'success' : 'warning'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { getAttendanceOverview } from '@/api/modules';

const month = ref('2026-04');
const loading = ref(false);
const rows = ref([]);

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getAttendanceOverview();
    rows.value = result.data.records || [];
  } finally {
    loading.value = false;
  }
};

onMounted(loadData);
</script>
