<template>
  <div class="page-grid hp">
    <PageCard title="HR绩效复核" description="使用 AI 诊断检查异常，复核流程和结果后确认发布或退回修正。">
      <template #actions>
        <el-space wrap>
          <el-date-picker v-model="monthValue" type="month" value-format="YYYY-MM" placeholder="考核周期" />
          <el-select v-model="statusFilter" clearable placeholder="状态筛选" style="width: 180px">
            <el-option label="待HR审核" value="待HR审核" />
            <el-option label="已确认发布" value="已确认发布" />
            <el-option label="HR退回修改" value="HR退回修改" />
          </el-select>
          <el-button plain :loading="loading" @click="loadRows">刷新</el-button>
        </el-space>
      </template>

      <el-table :data="filteredRows" width="100%" v-loading="loading">
        <el-table-column prop="employeeNo" label="工号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="department" label="部门" min-width="120" />
        <el-table-column prop="period" label="周期" min-width="120" />
        <el-table-column prop="totalScore" label="总分" min-width="90" />
        <el-table-column prop="grade" label="等级" min-width="80" />
        <el-table-column prop="status" label="状态" min-width="120" />
        <el-table-column label="操作" min-width="220" fixed="right">
          <template #default="s">
            <el-space wrap>
              <el-button v-if="canReview(s.row)" size="small" @click="openDetail(s.row)">查看复核</el-button>
              <el-button v-if="canReview(s.row)" size="small" :loading="aiLoading && aiRecordId===s.row.id" @click="openAiDiagnosis(s.row)">AI诊断</el-button>
              <span v-if="!canReview(s.row)" class="muted-action">已完成</span>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>

    <el-dialog v-model="dialogVisible" title="HR复核确认" width="960px" destroy-on-close>
      <div class="dialog-scroll" v-if="form.id">
        <div class="block">
          <div class="block-title">员工提交</div>
          <div class="info-grid">
            <div><strong>月度工作内容：</strong>{{ form.monthlyWorkContent || '—' }}</div>
            <div><strong>突出业绩：</strong>{{ form.achievementHighlights || '—' }}</div>
            <div><strong>员工自评：</strong>{{ form.selfReview || '—' }}</div>
          </div>
        </div>
        <div class="block">
          <div class="block-title">经理审核结果</div>
          <div class="info-grid">
            <div><strong>业绩指标得分：</strong>{{ form.performanceScore }}</div>
            <div><strong>工作态度得分：</strong>{{ form.attitudeScore }}</div>
            <div><strong>能力表现得分：</strong>{{ form.abilityScore }}</div>
            <div><strong>综合总分：</strong>{{ form.totalScore }}</div>
            <div><strong>绩效等级：</strong>{{ form.grade || '—' }}</div>
            <div><strong>绩效系数：</strong>{{ form.coefficient }}</div>
            <div class="span-2"><strong>上级评价：</strong>{{ form.managerReview || '—' }}</div>
          </div>
        </div>
        <div class="block">
          <div class="block-head"><span class="block-title">AI诊断结果</span><el-button :loading="aiLoading" @click="openAiDiagnosis(form)">重新AI诊断</el-button></div>
          <div class="diagnosis-box">{{ aiSummary || '尚未生成 AI 诊断，可点击按钮检查评分是否异常。' }}</div>
          <el-form label-position="top">
            <el-form-item label="HR复核备注"><el-input v-model="hrRemark" type="textarea" :rows="4" placeholder="填写复核意见、流程说明或退回原因" /></el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button :loading="saving" @click="sendBack">退回修正</el-button>
        <el-button type="primary" :loading="saving" @click="confirmPublish">确认发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="aiDialogVisible" title="AI诊断报告" width="820px" destroy-on-close>
      <div class="ai-shell">
        <div class="ai-summary">{{ aiSummary || '暂无诊断内容' }}</div>
        <div class="ai-grid">
          <div class="ai-card"><div class="ai-title">问题诊断</div><ul><li v-for="(i,index) in aiSections.issues" :key="`i-${index}`">{{ i }}</li></ul></div>
          <div class="ai-card"><div class="ai-title">原因分析</div><ul><li v-for="(i,index) in aiSections.reasons" :key="`r-${index}`">{{ i }}</li></ul></div>
          <div class="ai-card"><div class="ai-title">优势亮点</div><ul><li v-for="(i,index) in aiSections.highlights" :key="`h-${index}`">{{ i }}</li></ul></div>
          <div class="ai-card"><div class="ai-title">改进建议</div><ul><li v-for="(i,index) in aiSections.suggestions" :key="`s-${index}`">{{ i }}</li></ul></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import PageCard from '@/components/PageCard.vue';
import { diagnosePerformance, getPerformanceList, getPerformanceDetail, updatePerformance } from '@/api/modules';

const rows = ref([]), loading = ref(false), saving = ref(false), aiLoading = ref(false), dialogVisible = ref(false), aiDialogVisible = ref(false), aiRecordId = ref(''), monthValue = ref('2026-04'), statusFilter = ref('待HR审核');
const form = reactive({});
const hrRemark = ref('');
const aiSummary = ref('');
const aiSections = reactive({ issues: [], reasons: [], highlights: [], suggestions: [] });
const filteredRows = computed(() => rows.value.filter((item) => !statusFilter.value || item.status === statusFilter.value));
const canReview = (row) => row.status === '待HR审核';
const normalize = (item) => ({ ...item, monthlyWorkContent: item.monthlyWorkContent || '', achievementHighlights: item.achievementHighlights || '', selfReview: item.selfReview || '', managerReview: item.managerReview || '' });

async function loadRows() {
  loading.value = true;
  try {
    const params = { page: 1, pageSize: 200 };
    if (monthValue.value) {
      const [year, month] = monthValue.value.split('-').map(Number);
      params.assessmentYear = year;
      params.assessmentMonth = month;
      params.cycleType = '月度';
    }
    const result = await getPerformanceList(params);
    rows.value = (result.data?.records || []).map(normalize);
  } finally { loading.value = false; }
}
async function openDetail(row) {
  const result = await getPerformanceDetail(row.id);
  Object.assign(form, normalize(result.data || {}));
  hrRemark.value = form.remark || '';
  dialogVisible.value = true;
}
async function openAiDiagnosis(row) {
  aiLoading.value = true;
  aiRecordId.value = row.id || '';
  try {
    const result = await diagnosePerformance({ recordId: row.id, employeeNo: row.employeeNo });
    const data = result.data || {};
    aiSummary.value = data.summary || '';
    aiSections.issues = data.issues || [];
    aiSections.reasons = data.reasons || [];
    aiSections.highlights = data.highlights || [];
    aiSections.suggestions = data.suggestions || [];
    aiDialogVisible.value = true;
  } finally { aiLoading.value = false; aiRecordId.value = ''; }
}
async function sendBack() {
  saving.value = true;
  try {
    await updatePerformance(form.id, { status: 'HR退回修改', remark: hrRemark.value });
    ElMessage.success('已退回修正');
    dialogVisible.value = false;
    await loadRows();
  } finally { saving.value = false; }
}
async function confirmPublish() {
  saving.value = true;
  try {
    await updatePerformance(form.id, { status: '已确认发布', remark: hrRemark.value });
    ElMessage.success('已确认发布');
    dialogVisible.value = false;
    await loadRows();
  } finally { saving.value = false; }
}

onMounted(loadRows);
</script>

<style scoped>
.hp,.block{display:grid;gap:16px}.dialog-scroll{max-height:min(78vh,860px);overflow-y:auto;padding-right:6px}.block{padding:16px;border:1px solid #dcdfe6;border-radius:12px;background:#fff}.block-title,.ai-title{font-size:16px;font-weight:700}.block-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.info-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;line-height:1.8}.span-2{grid-column:span 2}.diagnosis-box{padding:14px 16px;border-radius:12px;background:#f7fbff;border:1px solid #dbe8ff;line-height:1.8}.ai-shell{display:grid;gap:16px}.ai-summary{padding:16px;border-radius:12px;background:#f7fbff;border:1px solid #dbe8ff;line-height:1.8}.ai-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.ai-card{padding:16px;border-radius:12px;background:#fff;border:1px solid #dcdfe6}.ai-card ul{margin:12px 0 0;padding-left:18px;display:grid;gap:8px}.muted-action{color:#909399;font-size:13px}@media (max-width:768px){.info-grid,.ai-grid{grid-template-columns:1fr}.span-2{grid-column:span 1}.block-head{flex-direction:column;align-items:stretch}}
</style>
