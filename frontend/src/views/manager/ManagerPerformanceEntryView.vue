<template>
  <div class="page-grid mp">
    <div class="manager-summary-grid">
      <div class="summary-card">
        <div class="summary-card__label">A档人数</div>
        <div class="summary-card__value">{{ validationPanels.aCount }}</div>
        <div class="summary-card__meta">当前筛选范围内 A 档绩效人数</div>
      </div>
      <div class="summary-card">
        <div class="summary-card__label">B档人数</div>
        <div class="summary-card__value">{{ validationPanels.bCount }}</div>
        <div class="summary-card__meta">当前筛选范围内 B 档绩效人数</div>
      </div>
      <div class="summary-card">
        <div class="summary-card__label">校验结果</div>
        <div class="summary-card__value summary-card__value--text">{{ validationPanels.result }}</div>
        <div class="summary-card__meta">基于当前绩效等级分布自动判断</div>
      </div>
      <div class="summary-card">
        <div class="summary-card__label">复核建议</div>
        <div class="summary-card__value summary-card__value--text">{{ validationPanels.suggestion }}</div>
        <div class="summary-card__meta">帮助经理快速决定是否需要再复核</div>
      </div>
    </div>

    <PageCard>
      <template #actions>
        <el-space wrap>
          <el-date-picker v-model="monthValue" type="month" value-format="YYYY-MM" placeholder="考核周期" />
          <el-select v-model="statusFilter" clearable placeholder="状态筛选" style="width: 160px">
            <el-option label="待经理审核" value="待经理审核" />
            <el-option label="待HR审核" value="待HR审核" />
            <el-option label="经理退回修改" value="经理退回修改" />
            <el-option label="HR退回修改" value="HR退回修改" />
            <el-option label="已确认发布" value="已确认发布" />
          </el-select>
          <el-button plain :loading="loading" @click="loadRows">刷新</el-button>
        </el-space>
      </template>

      <el-table :data="filteredRows" width="100%" v-loading="loading">
        <el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center" />
        <el-table-column prop="name" label="姓名" min-width="120" align="center" header-align="center" />
        <el-table-column prop="department" label="部门" min-width="120" align="center" header-align="center" />
        <el-table-column prop="period" label="周期" min-width="120" align="center" header-align="center" />
        <el-table-column prop="monthlyWorkContent" label="月度工作内容" min-width="220" show-overflow-tooltip align="center" header-align="center" />
        <el-table-column prop="achievementHighlights" label="突出业绩" min-width="220" show-overflow-tooltip align="center" header-align="center" />
        <el-table-column prop="status" label="状态" min-width="120" align="center" header-align="center" />
        <el-table-column label="操作" min-width="200" fixed="right" align="center" header-align="center">
          <template #default="s">
            <el-space wrap>
              <el-button size="small" @click="openView(s.row)">查看内容</el-button>
              <el-button v-if="canReview(s.row)" size="small" type="primary" plain @click="openEdit(s.row)">审核评分</el-button>
              <span v-else class="muted-action">无需处理</span>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>

    <el-dialog v-model="dialogVisible" class="manager-review-dialog" width="min(980px, calc(100vw - 32px))" destroy-on-close>
      <template #header>
        <div class="dialog-headline">
          <div>
            <div class="dialog-eyebrow">MANAGER REVIEW</div>
            <h3>经理审核与评分</h3>
            <p>基于员工提交内容完成评分判断，并输出上级评价后提交给 HR。</p>
          </div>
        </div>
      </template>

      <el-form :model="form" label-position="top" class="dialog-body-grid">
        <section class="block block--soft">
          <div class="block-title">员工提交内容</div>
          <div class="identity-strip">
            <div class="identity-chip">
              <span class="identity-chip__label">工号</span>
              <strong>{{ form.employeeNo || '—' }}</strong>
            </div>
            <div class="identity-chip">
              <span class="identity-chip__label">姓名</span>
              <strong>{{ form.name || '—' }}</strong>
            </div>
            <div class="identity-chip">
              <span class="identity-chip__label">部门</span>
              <strong>{{ form.department || '—' }}</strong>
            </div>
            <div class="identity-chip">
              <span class="identity-chip__label">周期</span>
              <strong>{{ form.period || '—' }}</strong>
            </div>
          </div>
          <div class="submission-grid">
            <div class="submission-card">
              <div class="submission-card__title">月度工作内容</div>
              <div class="submission-card__content">{{ form.monthlyWorkContent || '暂无内容' }}</div>
            </div>
            <div class="submission-card">
              <div class="submission-card__title">突出业绩</div>
              <div class="submission-card__content">{{ form.achievementHighlights || '暂无内容' }}</div>
            </div>
            <div class="submission-card submission-card--full">
              <div class="submission-card__title">员工自评</div>
              <div class="submission-card__content">{{ form.selfReview || '暂无内容' }}</div>
            </div>
          </div>
        </section>

        <section class="block block--accent">
          <div class="block-head block-head--inline">
            <div>
              <div class="block-title">经理审核评分</div>
              <div class="block-subtitle">可手动调整评分，AI 仅作为辅助参考。</div>
            </div>
            <el-button v-if="canUseAi" class="ai-btn ai-btn--solid" :loading="aiLoading.score" @click="runAiAutoScore">AI辅助评分</el-button>
          </div>

          <div class="score-grid">
            <div class="score-card">
              <span class="score-card__label">业绩指标得分</span>
              <el-input-number v-model="form.performanceScore" :min="0" :max="100" :disabled="viewOnly" style="width:100%" @change="calc" />
            </div>
            <div class="score-card">
              <span class="score-card__label">工作态度得分</span>
              <el-input-number v-model="form.attitudeScore" :min="0" :max="100" :disabled="viewOnly" style="width:100%" @change="calc" />
            </div>
            <div class="score-card">
              <span class="score-card__label">能力表现得分</span>
              <el-input-number v-model="form.abilityScore" :min="0" :max="100" :disabled="viewOnly" style="width:100%" @change="calc" />
            </div>
            <div class="score-card score-card--strong">
              <span class="score-card__label">综合总分</span>
              <el-input-number v-model="form.totalScore" :min="0" :max="100" :disabled="viewOnly" style="width:100%" @change="calcGC" />
            </div>
            <div class="score-card">
              <span class="score-card__label">绩效等级</span>
              <el-select v-model="form.grade" :disabled="viewOnly" @change="syncCoef"><el-option v-for="i in grades" :key="i" :label="i" :value="i" /></el-select>
            </div>
            <div class="score-card">
              <span class="score-card__label">绩效系数</span>
              <el-input-number v-model="form.coefficient" :min="0" :max="3" :step="0.1" :disabled="viewOnly" style="width:100%" />
            </div>
          </div>

          <el-form-item class="manager-comment-item">
            <template #label>
              <div class="field-head">
                <span>上级评价</span>
                <el-button v-if="canUseAi" class="ai-btn ai-btn--solid" :loading="aiLoading.comment" @click="runAiManagerComment">AI生成上级评价</el-button>
              </div>
            </template>
            <div class="comment-field">
              <el-input v-model="form.managerReview" type="textarea" :rows="6" :disabled="viewOnly" />
            </div>
          </el-form-item>
        </section>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible=false">关闭</el-button>
          <template v-if="!viewOnly">
            <el-button :loading="saving" @click="submitBack">退回员工修改</el-button>
            <el-button type="primary" :loading="saving" @click="submitHr">提交 HR</el-button>
          </template>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import PageCard from '@/components/PageCard.vue';
import { autoScorePerformance, generatePerformanceComment, getPerformanceList, updatePerformance } from '@/api/modules';

const rows = ref([]), loading = ref(false), saving = ref(false), dialogVisible = ref(false), viewOnly = ref(false), monthValue = ref('2026-04'), statusFilter = ref('');
const aiLoading = reactive({ score: false, comment: false });
const grades = ['S', 'A', 'B', 'C', 'D'];
const emptyForm = () => ({ id: '', employeeNo: '', name: '', department: '', position: '', period: '', monthlyWorkContent: '', achievementHighlights: '', selfReview: '', performanceScore: 0, attitudeScore: 0, abilityScore: 0, totalScore: 0, grade: 'B', coefficient: 1, managerReview: '' });
const form = reactive(emptyForm());
const coefMap = { S: 1.5, A: 1.2, B: 1, C: 0.8, D: 0.5 };
const filteredRows = computed(() => rows.value.filter((item) => !statusFilter.value || item.status === statusFilter.value));
const validationPanels = computed(() => {
  const list = filteredRows.value;
  const aCount = list.filter((item) => item.grade === 'A').length;
  const bCount = list.filter((item) => item.grade === 'B').length;
  const scoredCount = list.filter((item) => ['S', 'A', 'B', 'C', 'D'].includes(item.grade)).length;
  const aRatio = scoredCount ? aCount / scoredCount : 0;
  return {
    aCount,
    bCount,
    result: scoredCount ? (aRatio > 0.3 ? '需复核' : '校验通过') : '暂无数据',
    suggestion: !scoredCount ? '当前暂无已评分记录，可先完成评分后再查看校验结果。' : aRatio > 0.3 ? 'A档占比偏高，建议复核评分依据并横向比较同部门员工表现。' : '当前 A/B 档分布较稳定，可继续推进绩效流程。',
  };
});
const canReview = (row) => ['待经理审核', '经理退回修改', 'HR退回修改'].includes(row.status);
const canUseAi = computed(() => !viewOnly.value && ['待经理审核', '经理退回修改', 'HR退回修改'].includes(form.status));
const reset = () => Object.assign(form, emptyForm());
const normalize = (item) => ({ ...item, period: item.period || '—', monthlyWorkContent: item.monthlyWorkContent || '', achievementHighlights: item.achievementHighlights || '', selfReview: item.selfReview || '', managerReview: item.managerReview || '', status: item.status || '待经理审核' });
const syncCoef = () => { form.coefficient = coefMap[form.grade] || 1; };
const calcGC = () => { const s = Number(form.totalScore || 0); form.grade = s >= 90 ? 'S' : s >= 80 ? 'A' : s >= 70 ? 'B' : s >= 60 ? 'C' : 'D'; syncCoef(); };
const calc = () => { form.totalScore = Number((Number(form.performanceScore || 0) * 0.6 + Number(form.attitudeScore || 0) * 0.2 + Number(form.abilityScore || 0) * 0.2).toFixed(2)); calcGC(); };

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
function openView(row) { viewOnly.value = true; reset(); Object.assign(form, normalize(JSON.parse(JSON.stringify(row)))); dialogVisible.value = true; }
function openEdit(row) { viewOnly.value = false; reset(); Object.assign(form, normalize(JSON.parse(JSON.stringify(row)))); dialogVisible.value = true; }
async function runAiAutoScore() {
  aiLoading.score = true;
  try {
    const result = await autoScorePerformance({ employeeNo: form.employeeNo, department: form.department, position: form.position, selfReview: `${form.monthlyWorkContent}\n${form.achievementHighlights}\n${form.selfReview}` });
    const data = result.data || {};
    form.performanceScore = Number(data.performanceScore || 0);
    form.attitudeScore = Number(data.attitudeScore || 0);
    form.abilityScore = Number(data.abilityScore || 0);
    form.totalScore = Number(data.totalScore || 0);
    form.grade = data.grade || 'B';
    form.coefficient = Number(data.coefficient || 1);
    ElMessage.success('AI 辅助评分完成');
  } finally { aiLoading.score = false; }
}
async function runAiManagerComment() {
  aiLoading.comment = true;
  try {
    const result = await generatePerformanceComment({ commentType: 'manager', style: '中性型', employeeNo: form.employeeNo, name: form.name, department: form.department, totalScore: form.totalScore, grade: form.grade, selfReview: form.selfReview, managerReview: form.managerReview, achievementHighlights: form.achievementHighlights });
    form.managerReview = result.data?.content || form.managerReview;
    ElMessage.success('AI 上级评价生成完成');
  } finally { aiLoading.comment = false; }
}
async function submitBack() {
  saving.value = true;
  try {
    await updatePerformance(form.id, { status: '经理退回修改', performanceScore: form.performanceScore, attitudeScore: form.attitudeScore, abilityScore: form.abilityScore, totalScore: form.totalScore, grade: form.grade, coefficient: form.coefficient, managerReview: form.managerReview });
    ElMessage.success('已退回员工修改');
    dialogVisible.value = false;
    await loadRows();
  } finally { saving.value = false; }
}
async function submitHr() {
  if ([form.performanceScore, form.attitudeScore, form.abilityScore].some((item) => item === null || item === undefined || item === '')) {
    return ElMessage.warning('提交 HR 前必须填写全部评分');
  }
  saving.value = true;
  try {
    await updatePerformance(form.id, { status: '待HR审核', performanceScore: form.performanceScore, attitudeScore: form.attitudeScore, abilityScore: form.abilityScore, totalScore: form.totalScore, grade: form.grade, coefficient: form.coefficient, managerReview: form.managerReview });
    ElMessage.success('已提交 HR 复核');
    dialogVisible.value = false;
    await loadRows();
  } finally { saving.value = false; }
}

onMounted(loadRows);
</script>

<style scoped>
.mp{display:grid;gap:16px}
.manager-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}
.summary-card{padding:18px;border-radius:18px;border:1px solid rgba(114,132,168,.16);background:linear-gradient(180deg,#f8fbff 0%,#ffffff 100%);box-shadow:0 10px 24px rgba(31,42,68,.05);display:grid;gap:8px}
.summary-card__label{font-size:14px;font-weight:800;color:#5f6f86}
.summary-card__value{font-size:30px;font-weight:900;color:#20324a;line-height:1.2}
.summary-card__value--text{font-size:20px}
.summary-card__meta{font-size:12px;color:#7a879a;line-height:1.6}
.block{display:grid;gap:18px;padding:20px;border-radius:22px;border:1px solid rgba(114,132,168,.18);background:linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);box-shadow:0 18px 40px rgba(31,42,68,.08)}
.block--soft{background:linear-gradient(180deg,#ffffff 0%,#f7faff 100%)}
.block--accent{background:linear-gradient(180deg,#fdfefe 0%,#f4f9ff 100%)}
.block-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}
.block-head--inline{align-items:center}
.block-title{font-size:18px;font-weight:800;color:#20324a;letter-spacing:.01em}
.block-subtitle{margin-top:6px;color:#6d7c92;font-size:13px}
.dialog-headline{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}
.dialog-headline h3{margin:4px 0 6px;font-size:28px;font-weight:900;color:#18263a}
.dialog-headline p{margin:0;color:#6d7c92;line-height:1.7}
.dialog-eyebrow{font-size:12px;font-weight:800;letter-spacing:.18em;color:#7b8ba3}
.dialog-body-grid{display:grid;gap:18px}
.identity-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.identity-chip{padding:14px 16px;border-radius:18px;background:linear-gradient(180deg,#eef5ff 0%,#f7fbff 100%);border:1px solid #d8e5ff;display:grid;gap:6px}
.identity-chip__label{font-size:12px;color:#6e7f98;font-weight:700;letter-spacing:.08em}
.submission-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.submission-card{padding:16px;border-radius:18px;background:#fff;border:1px solid rgba(114,132,168,.14);min-height:152px;display:grid;gap:10px}
.submission-card--full{grid-column:1 / -1;min-height:136px}
.submission-card__title{font-size:14px;font-weight:800;color:#30445f}
.submission-card__content{color:#5b6b82;line-height:1.85;white-space:pre-wrap;word-break:break-word}
.score-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.score-card{padding:16px;border-radius:18px;background:#fff;border:1px solid rgba(114,132,168,.14);display:grid;gap:10px}
.score-card--strong{background:linear-gradient(180deg,#eef6ff 0%,#f7fbff 100%);border-color:#cfe0ff}
.score-card__label{font-size:13px;font-weight:800;color:#52647e}
.manager-comment-item{margin-bottom:0}
.manager-comment-item:deep(.el-form-item__label){width:100%}
.manager-comment-item:deep(.el-form-item__content){display:block}
.field-head{display:flex;justify-content:space-between;align-items:center;gap:12px;width:100%}
.comment-field{display:grid;gap:12px}
.ai-btn{border-color:#409EFF;color:#409EFF;background:#fff;border-radius:12px;padding:0 18px}
.ai-btn:hover{background:#409EFF;color:#fff}
.ai-btn--solid{background:linear-gradient(135deg,#409EFF 0%,#73b7ff 100%);border-color:transparent;color:#fff;box-shadow:0 16px 32px rgba(64,158,255,.24)}
.ai-btn--solid:hover{background:linear-gradient(135deg,#358ef2 0%,#63aaf8 100%);color:#fff}
.dialog-footer{display:flex;justify-content:flex-end;gap:12px;flex-wrap:wrap}
.muted-action{color:#909399;font-size:13px}
:deep(.manager-review-dialog){max-height:calc(100vh - 64px);display:flex;flex-direction:column;overflow:hidden}
:deep(.manager-review-dialog .el-dialog__header){padding:24px 24px 8px}
:deep(.manager-review-dialog .el-dialog__body){padding:8px 24px 20px;height:600px;max-height:600px;overflow-y:auto;box-sizing:border-box}
:deep(.manager-review-dialog .el-dialog__footer){padding:16px 24px 24px;border-top:1px solid rgba(114,132,168,.12);background:rgba(248,251,255,.9)}
:deep(.manager-review-dialog .el-dialog){margin:24px auto !important;border-radius:28px;overflow:hidden;box-shadow:0 30px 80px rgba(15,23,42,.22);background:linear-gradient(180deg,#ffffff 0%,#f9fbff 100%)}
.manager-review-dialog:deep(.el-input__wrapper),
.manager-review-dialog:deep(.el-textarea__inner),
.manager-review-dialog:deep(.el-input-number),
.manager-review-dialog:deep(.el-select__wrapper){border-radius:14px}
@media (max-width:900px){.manager-summary-grid,.identity-strip,.submission-grid,.score-grid{grid-template-columns:1fr}.submission-card--full{grid-column:auto}.dialog-headline{flex-direction:column;align-items:stretch}.field-head{flex-direction:column;align-items:stretch}.field-head .el-button{width:100%}}
</style>
