<template>
  <div class="page-grid">
    <PageCard title="申请中心" description="提交请假、加班、出差、领用等申请。">
      <div class="two-column">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="申请类型" prop="leave_type">
            <el-select v-model="form.leave_type" placeholder="请选择申请类型">
              <el-option label="病假" value="病假" />
              <el-option label="事假" value="事假" />
              <el-option label="婚假" value="婚假" />
              <el-option label="调休" value="调休" />
            </el-select>
          </el-form-item>
          <el-form-item label="起始时间" prop="start_at">
            <el-input v-model="form.start_at" placeholder="2026-04-16 09:00" />
          </el-form-item>
          <el-form-item label="结束时间" prop="end_at">
            <el-input v-model="form.end_at" placeholder="2026-04-17 18:00" />
          </el-form-item>
          <el-form-item label="请假天数" prop="days">
            <el-input-number v-model="form.days" :min="0" :step="0.5" style="width: 100%" />
          </el-form-item>
          <el-form-item label="申请说明" prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请原因" />
          </el-form-item>
          <el-button type="primary" @click="submit">提交申请</el-button>
        </el-form>

        <el-table :data="rows" width="100%" v-loading="loading">
          <el-table-column prop="leave_type" label="类型" min-width="120" />
          <el-table-column label="时间" min-width="180">
            <template #default="scope">{{ scope.row.start_at }} ~ {{ scope.row.end_at }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="120" />
          <el-table-column prop="approver" label="审批人" min-width="120" />
        </el-table>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { createLeave, getLeaves } from '@/api/modules';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
const formRef = ref();
const loading = ref(false);
const rows = ref([]);
const form = reactive({
  employee_no: store.user?.employeeNo || '',
  leave_type: '',
  start_at: '2026-04-16 09:00',
  end_at: '2026-04-17 18:00',
  days: 1,
  reason: '',
});

const rules = {
  leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
  start_at: [{ required: true, message: '请输入开始时间', trigger: 'blur' }],
  end_at: [{ required: true, message: '请输入结束时间', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }],
};

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getLeaves();
    rows.value = result.data || [];
  } finally {
    loading.value = false;
  }
};

const submit = async () => {
  await formRef.value.validate();
  form.employee_no = store.user?.employeeNo || '';
  await createLeave(form);
  ElMessage.success('申请已提交');
  loadData();
};

onMounted(loadData);
</script>
