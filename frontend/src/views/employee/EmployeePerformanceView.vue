<template>
  <div class="page-grid ep">
    <PageCard title="我的绩效提交" description="月底填写本月工作内容、突出业绩并提交自评给部门经理。">
      <template #actions>
        <el-space wrap>
          <el-select v-model="statusFilter" clearable placeholder="状态筛选" style="width: 160px">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
          <el-button type="primary" @click="openCreate">新增月度绩效</el-button>
          <el-button plain :loading="loading" @click="loadRows">刷新</el-button>
        </el-space>
      </template>

      <el-table :data="filteredRows" width="100%" v-loading="loading">
        <el-table-column prop="period" label="考核周期" min-width="120" />
        <el-table-column prop="monthlyWorkContent" label="月度工作内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="achievementHighlights" label="突出业绩" min-width="220" show-overflow-tooltip />
        <el-table-column prop="selfReview" label="员工自评" min-width="220" show-overflow-tooltip />
        <el-table-column prop="managerReview" label="上级评价" min-width="220" show-overflow-tooltip />
        <el-table-column prop="totalScore" label="总分" min-width="90" />
        <el-table-column prop="grade" label="等级" min-width="80" />
        <el-table-column prop="status" label="状态" min-width="120" />
        <el-table-column label="操作" min-width="140" fixed="right">
          <template #default="s">
            <el-button v-if="canEdit(s.row)" size="small" type="primary" plain @click="openEdit(s.row)">编辑</el-button>
            <span v-else class="muted-action">当前不可修改</span>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑绩效提交' : '新增绩效提交'" width="840px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <div class="g g3">
          <el-form-item label="绩效周期*">
            <el-select v-model="form.cycleType"><el-option label="月度" value="月度" /></el-select>
          </el-form-item>
          <el-form-item label="考核年份*"><el-input-number v-model="form.assessmentYear" :min="2020" :max="2100" style="width:100%" /></el-form-item>
          <el-form-item label="考核月份*"><el-select v-model="form.assessmentMonth"><el-option v-for="i in months" :key="i" :label="`${i}月`" :value="i" /></el-select></el-form-item>
        </div>
        <el-form-item label="月度工作内容*"><el-input v-model="form.monthlyWorkContent" type="textarea" :rows="5" placeholder="填写本月主要工作内容、推进事项与完成情况" /></el-form-item>
        <el-form-item label="突出业绩*"><el-input v-model="form.achievementHighlights" type="textarea" :rows="5" placeholder="突出说明本月关键成果、亮点业绩与价值贡献" /></el-form-item>
        <el-form-item label="提交自评*"><el-input v-model="form.selfReview" type="textarea" :rows="5" placeholder="从目标达成、协作表现、成长反思等角度填写自评" /></el-form-item>
        <el-form-item label="补充说明"><el-input v-model="form.remark" type="textarea" :rows="3" placeholder="可补充说明风险、困难或需要经理关注的事项" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">提交给经理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import PageCard from '@/components/PageCard.vue';
import { createPerformance, getPerformanceSummary, updatePerformance } from '@/api/modules';

const rows = ref([]), loading = ref(false), saving = ref(false), dialogVisible = ref(false), editing = ref(false), statusFilter = ref('');
const months = Array.from({ length: 12 }, (_, i) => i + 1);
const statusOptions = ['待员工提交', '待经理审核', '经理退回修改', '待HR审核', 'HR退回修改', '已确认发布'];
const emptyForm = () => ({ id: '', cycleType: '月度', assessmentYear: new Date().getFullYear(), assessmentMonth: new Date().getMonth() + 1, monthlyWorkContent: '', achievementHighlights: '', selfReview: '', remark: '' });
const form = reactive(emptyForm());
const filteredRows = computed(() => rows.value.filter((item) => !statusFilter.value || item.status === statusFilter.value));
const reset = () => Object.assign(form, emptyForm());
const normalize = (item) => ({ ...item, monthlyWorkContent: item.monthlyWorkContent || '', achievementHighlights: item.achievementHighlights || '', selfReview: item.selfReview || '', managerReview: item.managerReview || '', grade: item.grade || (['待经理审核', '经理退回修改', '待HR审核', 'HR退回修改'].includes(item.status) ? '待评审中' : '') });
const canEdit = (row) => ['待员工提交', '经理退回修改', 'HR退回修改'].includes(row.status);

async function loadRows() {
  loading.value = true;
  try {
    const result = await getPerformanceSummary();
    rows.value = (result.data?.records || []).map(normalize);
  } finally { loading.value = false; }
}
function openCreate() { editing.value = false; reset(); dialogVisible.value = true; }
function openEdit(row) {
  if (!['待员工提交', '经理退回修改', 'HR退回修改'].includes(row.status)) return ElMessage.warning('当前状态不可由员工修改');
  editing.value = true;
  reset();
  Object.assign(form, normalize(JSON.parse(JSON.stringify(row))));
  dialogVisible.value = true;
}
function buildPayload() {
  return { cycleType: '月度', assessmentYear: form.assessmentYear, assessmentMonth: form.assessmentMonth, monthlyWorkContent: form.monthlyWorkContent, achievementHighlights: form.achievementHighlights, selfReview: form.selfReview, remark: form.remark, status: '待经理审核' };
}
async function save() {
  if (!form.monthlyWorkContent || !form.achievementHighlights || !form.selfReview) return ElMessage.warning('请填写完整后再提交');
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;
  if (form.assessmentYear !== currentYear || form.assessmentMonth !== currentMonth) {
    return ElMessage.warning('月度绩效仅允许提交当前自然月，不能提前或滞后提交');
  }
  const duplicate = rows.value.some((item) => !editing.value || item.id !== form.id ? item.assessmentYear === form.assessmentYear && item.assessmentMonth === form.assessmentMonth : false);
  if (duplicate) {
    return ElMessage.warning('当前月份绩效已提交，不能重复提交');
  }
  saving.value = true;
  try {
    if (editing.value) await updatePerformance(form.id, buildPayload());
    else await createPerformance(buildPayload());
    ElMessage.success('已提交给部门经理审核');
    dialogVisible.value = false;
    await loadRows();
  } finally { saving.value = false; }
}

onMounted(loadRows);
</script>

<style scoped>
.ep{display:grid;gap:16px}.g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.g3{grid-template-columns:repeat(3,minmax(0,1fr))}.muted-action{color:#909399;font-size:13px}@media (max-width:768px){.g,.g3{grid-template-columns:1fr}}
</style>
