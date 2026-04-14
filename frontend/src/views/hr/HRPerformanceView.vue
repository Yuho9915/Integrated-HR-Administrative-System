<template>
  <div class="page-grid ep pp"><section class="page-section panel"><div class="bar"><div class="fs"><el-select v-model="f.department" placeholder="部门筛选" clearable style="width:140px"><el-option v-for="i in ds" :key="i" :label="i" :value="i"/></el-select><el-select v-model="f.position" placeholder="岗位筛选" clearable style="width:140px"><el-option v-for="i in ps" :key="i" :label="i" :value="i"/></el-select><el-select v-model="f.cycleType" placeholder="绩效周期" clearable style="width:140px"><el-option v-for="i in cycles" :key="i" :label="i" :value="i"/></el-select><el-date-picker v-model="ym" type="month" placeholder="考核年月" clearable style="width:160px"/><el-input v-model="f.keyword" placeholder="搜索工号/姓名" clearable style="width:220px"/></div><div class="acts"><el-button type="primary" @click="openCreate">新增绩效</el-button><el-button @click="iv=true">绩效导入</el-button><el-button v-if="canAiDepartmentReport" @click="openAiDepartmentReport"><el-icon><MagicStick /></el-icon><span>AI生成部门报表</span></el-button><el-button @click="doExport">导出报表</el-button></div></div><div class="tb"><el-table :data="rows" :height="th" width="100%" v-loading="loading" class="full-table"><el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center"/><el-table-column prop="name" label="姓名" min-width="100" align="center" header-align="center"/><el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center"/><el-table-column prop="position" label="岗位" min-width="140" align="center" header-align="center"/><el-table-column prop="cycleType" label="绩效周期" min-width="100" align="center" header-align="center"/><el-table-column prop="assessmentYear" label="考核年份" min-width="100" align="center" header-align="center"/><el-table-column prop="assessmentMonth" label="考核月份" min-width="100" align="center" header-align="center"/><el-table-column prop="totalScore" label="综合总分" min-width="100" align="center" header-align="center"/><el-table-column prop="grade" label="绩效等级" min-width="100" align="center" header-align="center"/><el-table-column prop="coefficient" label="绩效系数" min-width="100" align="center" header-align="center"/><el-table-column prop="status" label="考核状态" min-width="100" align="center" header-align="center"/><el-table-column label="操作" min-width="320" fixed="right" align="center" header-align="center"><template #default="s"><el-space wrap><el-button size="small" @click="openDetail(s.row)">查看明细</el-button><el-button v-if="canAiDiagnose" size="small" @click="openAiDiagnosis(s.row)"><el-icon><MagicStick /></el-icon><span>AI诊断</span></el-button><el-button size="small" type="primary" plain @click="openEdit(s.row)">编辑</el-button><el-button size="small" type="danger" plain @click="delRow(s.row)">删除</el-button></el-space></template></el-table-column></el-table></div><div class="pg"><el-pagination v-model:current-page="p.page" :page-size="p.pageSize" :total="p.total" layout="slot, prev, pager, next"><span class="tt">共计 {{ p.total }} 条</span></el-pagination></div></section><el-dialog v-model="fv" :title="edit?'编辑绩效':'新增绩效'" width="920px" destroy-on-close align-center><el-form :model="form" label-position="top"><div class="g g4"><el-form-item label="工号*"><el-select v-model="form.employeeNo" :disabled="edit" filterable @change="pickEmp"><el-option v-for="i in emps" :key="i.employeeNo" :label="`${i.employeeNo} / ${i.name}`" :value="i.employeeNo"/></el-select></el-form-item><el-form-item label="姓名*"><el-input v-model="form.name" disabled/></el-form-item><el-form-item label="部门*"><el-input v-model="form.department" disabled/></el-form-item><el-form-item label="岗位*"><el-input v-model="form.position" disabled/></el-form-item><el-form-item label="绩效周期*"><el-select v-model="form.cycleType"><el-option v-for="i in cycles" :key="i" :label="i" :value="i"/></el-select></el-form-item><el-form-item label="考核年份*"><el-input-number v-model="form.assessmentYear" :min="2020" :max="2100" style="width:100%"/></el-form-item><el-form-item v-if="form.cycleType==='月度'" label="考核月份*"><el-select v-model="form.assessmentMonth"><el-option v-for="i in ms" :key="i" :label="`${i}月`" :value="i"/></el-select></el-form-item><el-form-item label="考核状态*"><el-select v-model="form.status"><el-option v-for="i in sts" :key="i" :label="i" :value="i"/></el-select></el-form-item></div><div class="g ai-score-row"><el-form-item label="业绩指标得分"><el-input-number v-model="form.performanceScore" :min="0" :max="100" style="width:100%" @change="calc"/></el-form-item><el-form-item label="工作态度得分"><el-input-number v-model="form.attitudeScore" :min="0" :max="100" style="width:100%" @change="calc"/></el-form-item><el-form-item label="能力表现得分"><el-input-number v-model="form.abilityScore" :min="0" :max="100" style="width:100%" @change="calc"/></el-form-item><el-form-item label="综合总分*"><div class="ai-inline"><el-input-number v-model="form.totalScore" :min="0" :max="100" style="width:100%" @change="calcGC"/><el-button v-if="canAiAutoScore" class="ai-btn" @click="runAiAutoScore"><el-icon><MagicStick /></el-icon><span>AI智能评分</span></el-button></div></el-form-item><el-form-item label="绩效等级*"><el-select v-model="form.grade" @change="syncCoef"><el-option v-for="i in gs" :key="i" :label="i" :value="i"/></el-select></el-form-item><el-form-item label="绩效系数*"><el-input-number v-model="form.coefficient" :min="0" :max="3" :step="0.1" style="width:100%"/></el-form-item></div><div class="sec"><div class="sec-hd"><span>考核指标明细</span><div class="sec-actions"><el-button v-if="canAiGenerateIndicators" class="ai-btn" @click="runAiGenerateIndicators"><el-icon><MagicStick /></el-icon><span>AI生成指标</span></el-button><el-button type="primary" plain @click="addIndicator">新增行</el-button></div></div><el-table :data="form.indicators" width="100%"><el-table-column label="指标名称" min-width="150"><template #default="s"><el-input v-model="s.row.name"/></template></el-table-column><el-table-column label="权重" min-width="100"><template #default="s"><el-input-number v-model="s.row.weight" :min="0" :max="100" style="width:100%"/></template></el-table-column><el-table-column label="目标值" min-width="120"><template #default="s"><el-input v-model="s.row.targetValue"/></template></el-table-column><el-table-column label="实际完成值" min-width="120"><template #default="s"><el-input v-model="s.row.actualValue"/></template></el-table-column><el-table-column label="完成率" min-width="100"><template #default="s"><el-input-number v-model="s.row.completionRate" :min="0" :max="999" style="width:100%"/></template></el-table-column><el-table-column label="得分" min-width="100"><template #default="s"><el-input-number v-model="s.row.score" :min="0" :max="100" style="width:100%"/></template></el-table-column><el-table-column label="操作" min-width="80" align="center"><template #default="s"><el-button link type="danger" @click="removeIndicator(s.$index)">删除</el-button></template></el-table-column></el-table></div><div class="g g3"><el-form-item label="员工自评"><div class="ai-comment-field"><el-input v-model="form.selfReview" type="textarea" :rows="4"/><el-button v-if="canAiGenerateSelfComment" class="ai-btn" @click="runAiComment('self')"><el-icon><MagicStick /></el-icon><span>AI生成自评</span></el-button></div></el-form-item><el-form-item label="上级评价"><div class="ai-comment-field"><el-input v-model="form.managerReview" type="textarea" :rows="4"/><el-button v-if="canAiGenerateManagerComment" class="ai-btn" @click="runAiComment('manager')"><el-icon><MagicStick /></el-icon><span>AI生成上级评</span></el-button></div></el-form-item><el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="4"/></el-form-item></div></el-form><template #footer><el-button @click="fv=false">取消</el-button><el-button type="primary" :loading="saving" @click="save">确定</el-button></template></el-dialog><el-dialog v-model="dv" class="performance-detail-dialog" width="min(900px, calc(100vw - 32px))" destroy-on-close align-center>
  <template #header>
    <div class="detail-header">
      <h3>{{ dt }}</h3>
    </div>
  </template>

  <div v-if="detail" class="detail-layout">
    <section class="detail-card detail-card--meta">
      <div class="detail-meta-grid">
        <div class="detail-meta-item"><span class="detail-meta-label">工号:</span><span class="detail-meta-value">{{ detail.employeeNo || '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">姓名:</span><span class="detail-meta-value">{{ detail.name || '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">部门:</span><span class="detail-meta-value">{{ detail.department || '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">岗位:</span><span class="detail-meta-value">{{ detail.position || '—' }}</span></div>

        <div class="detail-meta-item"><span class="detail-meta-label">绩效周期:</span><span class="detail-meta-value">{{ detail.cycleType || '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">考核年月:</span><span class="detail-meta-value">{{ detail.assessmentYear || '—' }}{{ detail.assessmentMonth ? ` / ${detail.assessmentMonth}月` : '' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">综合总分:</span><span class="detail-meta-value detail-meta-value--accent">{{ detail.totalScore ?? '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">绩效等级:</span><span class="detail-meta-value detail-meta-value--accent">{{ detail.grade || '—' }}</span></div>

        <div class="detail-meta-item"><span class="detail-meta-label">绩效系数:</span><span class="detail-meta-value">{{ detail.coefficient ?? '—' }}</span></div>
        <div class="detail-meta-item"><span class="detail-meta-label">考核状态:</span><span class="detail-meta-value">{{ detail.status || '—' }}</span></div>
        <div class="detail-meta-item detail-meta-item--span-2"><span class="detail-meta-label">审批人:</span><span class="detail-meta-value">{{ detail.reviewer || '-' }}</span></div>
      </div>
    </section>

    <section class="detail-card">
      <div class="detail-section-title">考核指标明细</div>
      <el-table :data="detail?.indicators || []" empty-text="暂无考核指标" width="100%">
        <el-table-column prop="name" label="指标名称" min-width="150" align="center" header-align="center" />
        <el-table-column prop="weight" label="权重" min-width="100" align="center" header-align="center" />
        <el-table-column prop="targetValue" label="目标值" min-width="120" align="center" header-align="center" />
        <el-table-column prop="actualValue" label="实际完成值" min-width="120" align="center" header-align="center" />
        <el-table-column prop="completionRate" label="完成率" min-width="100" align="center" header-align="center" />
        <el-table-column prop="score" label="得分" min-width="100" align="center" header-align="center" />
      </el-table>
    </section>

    <section class="detail-remark-grid">
      <div class="detail-note-card">
        <div class="detail-note-title">员工自评</div>
        <div class="detail-note-content">{{ detail.selfReview || '—' }}</div>
      </div>
      <div class="detail-note-card">
        <div class="detail-note-title">上级评价</div>
        <div class="detail-note-content">{{ detail.managerReview || '—' }}</div>
      </div>
      <div class="detail-note-card">
        <div class="detail-note-title">备注</div>
        <div class="detail-note-content">{{ detail.remark || '—' }}</div>
      </div>
    </section>
  </div>

  <template #footer>
    <div class="detail-footer">
      <el-button v-if="canAiAppealReview" class="detail-close-btn" @click="runAiAppealReview"><el-icon><MagicStick /></el-icon><span>AI申诉审核</span></el-button>
      <el-button v-if="canAiDiagnose" class="detail-close-btn" @click="openAiDiagnosis(detail)"><el-icon><MagicStick /></el-icon><span>AI诊断报告</span></el-button>
      <el-button class="detail-close-btn" @click="dv=false">关闭</el-button>
    </div>
  </template>
</el-dialog><el-dialog v-model="aiDialogVisible" class="performance-ai-dialog" width="min(980px, calc(100vw - 32px))" destroy-on-close align-center>
  <template #header>
    <div class="ai-report-header">
      <div>
        <div class="ai-report-eyebrow">PERFORMANCE INTELLIGENCE</div>
        <h3>{{ aiResult.title }}</h3>
      </div>
      <div class="ai-report-chip">AI生成</div>
    </div>
  </template>
  <div class="ai-report-shell" v-loading="aiLoading">
    <div class="ai-report-scroll">
      <section class="ai-hero-card">
        <div class="ai-hero-title">执行摘要</div>
        <div class="ai-hero-summary">{{ aiResult.summary || 'AI 已生成分析结果。' }}</div>
      </section>
      <section class="ai-result-grid">
        <div v-for="section in aiResult.sections" :key="section.title" class="ai-report-card">
          <div class="ai-report-card__title">{{ section.title }}</div>
          <div class="ai-list">
            <div v-for="(item,index) in section.items" :key="`${section.title}-${index}`" class="ai-list-item">{{ item }}</div>
            <div v-if="!section.items?.length" class="ai-list-item">暂无内容</div>
          </div>
        </div>
      </section>
    </div>
  </div>
  <template #footer>
    <div class="detail-footer ai-report-footer">
      <el-button class="detail-close-btn" @click="aiDialogVisible=false">关闭</el-button>
    </div>
  </template>
</el-dialog><el-dialog v-model="iv" class="performance-import-dialog" destroy-on-close align-center>
  <template #header>
    <div class="import-header">
      <h3>绩效导入</h3>
    </div>
  </template>

  <div class="import-layout">
    <section class="import-card">
      <div class="import-filter-row">
        <el-select v-model="imp.cycleType" class="import-control" placeholder="绩效周期">
          <el-option v-for="i in cycles" :key="i" :label="i" :value="i" />
        </el-select>
        <el-date-picker v-model="iym" class="import-control" type="month" placeholder="考核年月" clearable />
      </div>

      <div class="import-upload-row">
        <div class="import-upload-main">
          <el-upload :auto-upload="false" :show-file-list="false" :limit="1" accept=".xlsx" :on-change="pickFile">
            <el-button type="primary" round class="import-btn import-btn--primary">上传文件</el-button>
          </el-upload>
          <div class="import-file-meta">
            <span class="import-file-icon">📄</span>
            <span class="import-file-name">{{ uploadedFileName }}</span>
          </div>
        </div>
        <el-button plain class="import-btn import-btn--outline" @click="tpl">下载模板</el-button>
      </div>

      <p class="import-tip">仅支持.xlsx，文件大小不超过20MB</p>

      <el-progress v-if="parsing || parsed.total_count" :percentage="parsePercentage" :status="parsing ? '' : parsed.error_count ? 'warning' : 'success'" :stroke-width="10" />
    </section>

    <section class="import-card import-card--result">
      <div class="import-result-head">
        <div class="import-result-stats">
          <span class="success">成功 {{ parsed.success_count || 0 }} 条</span>
          <span class="danger">异常 {{ parsed.error_count || 0 }} 条</span>
        </div>
        <el-button v-if="parsed.error_count" class="import-btn import-btn--outline" @click="downloadErrors">下载异常清单</el-button>
      </div>

      <el-table :data="parsed.errors || []" empty-text="暂无异常数据" width="100%">
        <el-table-column prop="row" label="行号" min-width="90" align="center" header-align="center" />
        <el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center" />
        <el-table-column prop="message" label="异常信息" min-width="260" align="center" header-align="center" show-overflow-tooltip />
      </el-table>
    </section>
  </div>

  <template #footer>
    <div class="import-footer">
      <el-button class="import-btn import-btn--ghost" @click="resetImportDialog">取消</el-button>
      <el-button type="primary" class="import-btn import-btn--primary" :disabled="!canConfirm" :loading="importing" @click="confirmIt">确定</el-button>
    </div>
  </template>
</el-dialog></div>
</template>

<script setup>
import { computed,onMounted,reactive,ref,watch } from 'vue';
import { ElMessage,ElMessageBox } from 'element-plus';
import { MagicStick } from '@element-plus/icons-vue';
import { storeToRefs } from 'pinia';
import { autoScorePerformance,confirmPerformanceImport,createPerformance,deletePerformance,diagnosePerformance,exportPerformance,generatePerformanceComment,generatePerformanceIndicators,generatePerformanceReport,getEmployeeMeta,getPerformanceDetail,getPerformanceList,getPerformanceOptions,parsePerformanceImport,reviewPerformanceAppeal,updatePerformance } from '@/api/modules';
import { useAppStore } from '@/stores/app';
import { exportWorkbook } from '@/utils/export';
const th='calc(100vh - 320px)',ms=Array.from({length:12},(_,i)=>i+1),gs=['S','A','B','C','D'];
const appStore = useAppStore();
const { user } = storeToRefs(appStore);
const currentRole = computed(() => user.value?.role || '');
const canAiGenerateIndicators = computed(() => ['manager', 'hr'].includes(currentRole.value));
const canAiAutoScore = computed(() => ['manager', 'hr'].includes(currentRole.value));
const canAiGenerateSelfComment = computed(() => currentRole.value === 'employee');
const canAiGenerateManagerComment = computed(() => currentRole.value === 'manager');
const canAiDiagnose = computed(() => ['manager', 'hr', 'boss'].includes(currentRole.value));
const canAiDepartmentReport = computed(() => ['manager', 'hr', 'boss'].includes(currentRole.value));
const canAiAppealReview = computed(() => ['manager', 'hr', 'boss'].includes(currentRole.value));
const loading=ref(false),saving=ref(false),importing=ref(false),parsing=ref(false),aiLoading=ref(false),fv=ref(false),dv=ref(false),iv=ref(false),aiDialogVisible=ref(false),edit=ref(false),rows=ref([]),detail=ref(null),emps=ref([]),cycles=ref([]),sts=ref([]),ds=ref([]),pm=ref({}),ym=ref(''),iym=ref(''),file=ref(null),parsed=reactive({records:[],errors:[],total_count:0,success_count:0,error_count:0});
const aiResult=reactive({title:'AI分析结果',summary:'',sections:[],raw:null});
const p=reactive({page:1,pageSize:10,total:0}); const f=reactive({keyword:'',department:'',position:'',cycleType:'',assessmentYear:null,assessmentMonth:null}); const imp=reactive({cycleType:'月度',assessmentYear:new Date().getFullYear(),assessmentMonth:new Date().getMonth()+1}); const form=reactive({});
const reset=()=>Object.assign(form,{id:'',employeeNo:'',name:'',department:'',position:'',cycleType:'月度',assessmentYear:new Date().getFullYear(),assessmentMonth:new Date().getMonth()+1,performanceScore:0,attitudeScore:0,abilityScore:0,totalScore:0,grade:'B',coefficient:1,status:'待自评',reviewer:'',selfReview:'',managerReview:'',remark:'',indicators:[]}); reset();
const ps=computed(()=>f.department?(pm.value[f.department]||[]):[...new Set(Object.values(pm.value).flat())]); const dt=computed(()=>detail.value?`绩效明细 - ${detail.value.name} ${detail.value.cycleType} ${detail.value.assessmentYear}`:'绩效明细');
const uploadedFileName = computed(() => file.value?.name || '未上传文件');
const canConfirm = computed(() => Boolean(file.value) && parsed.records.length > 0 && !parsing.value && !importing.value);
const parsePercentage = computed(() => {
  if (parsing.value) return 60;
  if (!parsed.total_count) return 0;
  return Math.min(100, Math.round((parsed.success_count / parsed.total_count) * 100));
});
watch(()=>f.department,()=>{ if(f.position&&!ps.value.includes(f.position))f.position=''; p.page=1; load(); }); watch(()=>[f.position,f.cycleType,f.keyword],()=>{ p.page=1; load(); }); watch(()=>p.page,load);
watch(ym,v=>{ if(!v){f.assessmentYear=null;f.assessmentMonth=null;} else { const d=new Date(v); f.assessmentYear=d.getFullYear(); f.assessmentMonth=d.getMonth()+1; } p.page=1; load(); });
watch(iym,v=>{ if(!v){imp.assessmentYear=new Date().getFullYear();imp.assessmentMonth=new Date().getMonth()+1;} else { const d=new Date(v); imp.assessmentYear=d.getFullYear(); imp.assessmentMonth=d.getMonth()+1; } });
watch(()=>form.cycleType,v=>{ if(v!=='月度') form.assessmentMonth=null; });
function opts() { return Promise.all([getPerformanceOptions(), getEmployeeMeta()]).then(([po, em]) => { cycles.value = po.data?.cycleOptions || []; sts.value = po.data?.statusOptions || []; emps.value = po.data?.employeeOptions || []; ds.value = em.data?.departments || []; pm.value = em.data?.positions || {}; }); }
async function load() { loading.value = true; try { const r = await getPerformanceList({ ...f, page: p.page, pageSize: p.pageSize }); rows.value = r.data?.records || []; p.total = r.data?.total || 0; } finally { loading.value = false; } }
const pickEmp=v=>{ const e=emps.value.find(i=>i.employeeNo===v); if(!e)return; form.name=e.name; form.department=e.department; form.position=e.position; };
const syncCoef=()=>{ form.coefficient=({S:1.5,A:1.2,B:1,C:0.8,D:0.5})[form.grade]||1; };
const calcGC=()=>{ const s=Number(form.totalScore||0); form.grade=s>=90?'S':s>=80?'A':s>=70?'B':s>=60?'C':'D'; syncCoef(); };
const calc=()=>{ form.totalScore=Number((Number(form.performanceScore||0)*0.6+Number(form.attitudeScore||0)*0.2+Number(form.abilityScore||0)*0.2).toFixed(2)); calcGC(); };
const addIndicator=()=>{ form.indicators.push({name:'',weight:0,targetValue:'',actualValue:'',completionRate:0,score:0}); };
const removeIndicator=(index)=>{ form.indicators.splice(index,1); };
const openCreate=()=>{ edit.value=false; reset(); addIndicator(); fv.value=true; };
const openEdit=r=>{ edit.value=true; Object.assign(form,JSON.parse(JSON.stringify(r))); form.indicators=Array.isArray(form.indicators)?form.indicators:[]; fv.value=true; };
const openDetail=async r=>{ detail.value=(await getPerformanceDetail(r.id)).data; dv.value=true; };
const payload=()=>({employeeNo:form.employeeNo,name:form.name,department:form.department,position:form.position,cycleType:form.cycleType,assessmentYear:form.assessmentYear,assessmentMonth:form.cycleType==='月度'?form.assessmentMonth:null,performanceScore:Number(form.performanceScore||0),attitudeScore:Number(form.attitudeScore||0),abilityScore:Number(form.abilityScore||0),totalScore:Number(form.totalScore||0),grade:form.grade,coefficient:Number(form.coefficient||0),status:form.status,reviewer:form.reviewer,selfReview:form.selfReview,managerReview:form.managerReview,remark:form.remark,indicators:form.indicators});
const save=async()=>{ saving.value=true; try{ edit.value?await updatePerformance(form.id,payload()):await createPerformance(payload()); ElMessage.success(edit.value?'绩效更新成功':'绩效创建成功'); fv.value=false; load(); } finally{ saving.value=false; } };
const delRow=async r=>{ await ElMessageBox.confirm(`确认删除 ${r.name} 的绩效记录吗？`,'删除确认',{type:'warning'}); await deletePerformance(r.id); ElMessage.success('绩效删除成功'); load(); };
const doExport=async()=>{ const r=await exportPerformance(f); exportWorkbook(r.data?.records||[],r.data?.fileName||'绩效报表','Performance'); };
const openAiDialog=(title, summary, sections, raw=null)=>{ aiResult.title=title; aiResult.summary=summary||''; aiResult.sections=sections||[]; aiResult.raw=raw; aiDialogVisible.value=true; };
const handleAiError=(error, fallback)=>{ const detail = error?.response?.data?.detail || fallback; ElMessage.error(detail); };
const runAiGenerateIndicators=async()=>{ if(!form.department||!form.position) return ElMessage.warning('请先选择员工并带出部门、岗位'); aiLoading.value=true; try{ const r=await generatePerformanceIndicators({department:form.department,position:form.position,employeeNo:form.employeeNo}); form.indicators=(r.data?.indicators||[]).map(item=>({name:item.name||'',weight:Number(item.weight||0),targetValue:item.targetValue||'',actualValue:'',completionRate:0,score:0})); ElMessage.success(r.message||'AI 指标生成完成'); } catch(error){ handleAiError(error,'AI 指标生成失败'); } finally{ aiLoading.value=false; } };
const runAiAutoScore=async()=>{ if(!form.indicators?.length) return ElMessage.warning('请先填写或生成考核指标'); aiLoading.value=true; try{ const r=await autoScorePerformance({employeeNo:form.employeeNo,department:form.department,position:form.position,indicators:form.indicators,selfReview:form.selfReview}); const data=r.data||{}; form.performanceScore=Number(data.performanceScore||0); form.attitudeScore=Number(data.attitudeScore||0); form.abilityScore=Number(data.abilityScore||0); form.totalScore=Number(data.totalScore||0); form.grade=data.grade||'B'; form.coefficient=Number(data.coefficient||1); ElMessage.success(r.message||'AI 智能评分完成'); } catch(error){ handleAiError(error,'AI 智能评分失败'); } finally{ aiLoading.value=false; } };
const runAiComment=async(commentType)=>{ if(!form.employeeNo) return ElMessage.warning('请先选择员工'); aiLoading.value=true; try{ const r=await generatePerformanceComment({commentType,style:'中性型',employeeNo:form.employeeNo,name:form.name,department:form.department,position:form.position,indicators:form.indicators,totalScore:form.totalScore,grade:form.grade,selfReview:form.selfReview,managerReview:form.managerReview}); if(commentType==='self') form.selfReview=r.data?.content||form.selfReview; else form.managerReview=r.data?.content||form.managerReview; ElMessage.success(r.message||'AI 评语生成完成'); } catch(error){ handleAiError(error,'AI 评语生成失败'); } finally{ aiLoading.value=false; } };
const openAiDiagnosis=async(row)=>{ aiLoading.value=true; try{ const r=await diagnosePerformance({recordId:row.id,employeeNo:row.employeeNo}); const data=r.data||{}; openAiDialog('AI诊断报告',data.summary,[{title:'问题诊断',items:data.issues||[]},{title:'原因分析',items:data.reasons||[]},{title:'优势亮点',items:data.highlights||[]},{title:'改进建议',items:data.suggestions||[]}],data); } catch(error){ handleAiError(error,'AI 诊断失败'); } finally{ aiLoading.value=false; } };
const openAiDepartmentReport=async()=>{ aiLoading.value=true; try{ const r=await generatePerformanceReport({...f}); const data=r.data||{}; openAiDialog(data.title||'AI部门报表',data.overview,[{title:'部门对比',items:data.departmentComparison||[]},{title:'优秀案例',items:data.excellentCases||[]},{title:'待改进名单',items:data.improvementCases||[]},{title:'问题分析',items:data.analysis||[]},{title:'优化建议',items:data.suggestions||[]}],data); } catch(error){ handleAiError(error,'AI 报表生成失败'); } finally{ aiLoading.value=false; } };
const runAiAppealReview=async()=>{ if(!detail.value?.id) return ElMessage.warning('请先打开绩效明细'); const { value } = await ElMessageBox.prompt('请输入申诉内容','AI申诉审核',{confirmButtonText:'提交审核',cancelButtonText:'取消',inputType:'textarea'}); aiLoading.value=true; try{ const r=await reviewPerformanceAppeal({recordId:detail.value.id,employeeNo:detail.value.employeeNo,appealContent:value}); const data=r.data||{}; openAiDialog('AI申诉审核',data.reason,[{title:'审核结论',items:[data.decision||'—']},{title:'审核依据',items:data.evidence||[]}],data); } catch(error){ handleAiError(error,'AI 申诉审核失败'); } finally{ aiLoading.value=false; } };
const pickFile=async f=>{ const raw = f.raw; if (!raw) return; if (!raw.name.toLowerCase().endsWith('.xlsx')) return ElMessage.warning('仅支持上传 .xlsx 文件'); if (raw.size > 20 * 1024 * 1024) return ElMessage.warning('文件大小不能超过20MB'); file.value=raw; await parseIt(); };
const parseIt=async()=>{ if(!file.value) return ElMessage.warning('请先选择导入文件'); const fd=new FormData(); fd.append('file',file.value); parsing.value = true; try { const r=await parsePerformanceImport(fd,{cycleType:imp.cycleType,assessmentYear:imp.assessmentYear,assessmentMonth:imp.cycleType==='月度'?imp.assessmentMonth:null}); Object.assign(parsed, r.data?.parsed || {records:[],errors:[],total_count:0,success_count:0,error_count:0}); ElMessage.success(r.message); } catch (error) { Object.assign(parsed, {records:[],errors:[],total_count:0,success_count:0,error_count:0}); ElMessage.error(error?.response?.data?.detail || '绩效文件解析失败'); } finally { parsing.value = false; } };
const resetImportDialog=()=>{ iv.value=false; file.value=null; Object.assign(parsed, {records:[],errors:[],total_count:0,success_count:0,error_count:0}); };
const downloadErrors=()=>{ exportWorkbook((parsed.errors || []).map(item => ({ 行号: item.row || '', 工号: item.employeeNo || '', 异常信息: item.message || '' })), '绩效导入异常清单', 'PerformanceImportErrors'); };
const confirmIt=async()=>{ if(!parsed.records?.length) return ElMessage.warning('请先完成解析'); importing.value=true; try{ await confirmPerformanceImport({cycleType:imp.cycleType,assessmentYear:imp.assessmentYear,assessmentMonth:imp.cycleType==='月度'?imp.assessmentMonth:null,records:parsed.records,errors:parsed.errors}); ElMessage.success('绩效导入成功'); resetImportDialog(); load(); } finally{ importing.value=false; } };
const tpl=()=>exportWorkbook([{工号:'',姓名:'',部门:'',岗位:'',绩效周期:'月度',考核年份:new Date().getFullYear(),考核月份:new Date().getMonth()+1,业绩指标得分:0,工作态度得分:0,能力表现得分:0,综合总分:0,绩效等级:'B',绩效系数:1,员工自评:'',上级评价:'',考核状态:'待自评',备注:''}],'绩效导入模板','PerformanceTemplate');
onMounted(async()=>{ await opts(); await load(); });
</script>

<style scoped>
.pp{display:grid;gap:16px;height:calc(100vh - 148px)}.panel{display:grid;grid-template-rows:auto 1fr auto;gap:16px;padding:16px;min-height:0;height:100%;box-sizing:border-box}.bar{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}.fs,.acts,.ig{display:flex;align-items:center;gap:16px;flex-wrap:wrap}.tb{min-height:0;overflow:hidden}.tb :deep(.el-table th.el-table__cell){height:48px;padding:10px 0}.tb :deep(.el-table .el-table__cell){padding:10px 0}.tb :deep(.el-table .cell){line-height:24px}.pg{display:flex;justify-content:flex-end;position:sticky;bottom:0;z-index:2;padding-top:16px;background:transparent}.pg :deep(.el-pagination){padding:0;border-radius:0;background:transparent;box-shadow:none;border:none}.pg :deep(.el-pagination.is-background){background:transparent;border:none;box-shadow:none}.pg :deep(.btn-prev),.pg :deep(.btn-next),.pg :deep(.el-pager li){border-radius:8px}.pg :deep(.el-pager li.is-active){background:#409EFF;color:#fff}.tt{display:inline-flex;align-items:center;padding:0 12px;color:var(--hr-info);font-size:13px}.g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.g4{grid-template-columns:repeat(4,minmax(0,1fr))}.g3{margin-top:16px}.sec,.ir{display:grid;gap:16px}.sec-hd{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.sec-actions,.ai-inline,.ai-comment-field{display:flex;align-items:center;gap:12px}.ai-comment-field{flex-direction:column;align-items:stretch}.ai-score-row .el-form-item{margin-bottom:0}.ai-btn{height:36px;border-radius:8px;border:1px solid #409EFF;color:#409EFF;background:#fff}.ai-btn:hover{background:#409EFF;color:#fff;border-color:#409EFF}.ai-result-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.ai-list{display:grid;gap:12px}.ai-list-item{padding:14px 16px;border-radius:14px;background:linear-gradient(180deg,#f8fbff 0%,#f2f7ff 100%);border:1px solid #dbe8ff;color:#445066;line-height:1.8;text-align:left;box-shadow:inset 0 1px 0 rgba(255,255,255,.7)}.ai-summary{min-height:auto}.ai-report-header{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.ai-report-header h3{margin:4px 0 0;font-size:28px;font-weight:800;letter-spacing:.02em;color:#1f2d3d}.ai-report-eyebrow{font-size:12px;font-weight:700;letter-spacing:.16em;color:#7f8ea3}.ai-report-chip{display:inline-flex;align-items:center;justify-content:center;height:30px;padding:0 12px;border-radius:999px;background:linear-gradient(135deg,#409EFF 0%,#76b6ff 100%);color:#fff;font-size:12px;font-weight:700;box-shadow:0 10px 24px rgba(64,158,255,.24)}.ai-report-shell{height:786.82px;max-height:calc(100vh - 120px);overflow:hidden;border-radius:20px;background:linear-gradient(180deg,#f8fbff 0%,#eef4ff 100%);border:1px solid #d9e7ff}.ai-report-scroll{height:100%;overflow-y:auto;padding:20px}.ai-report-scroll::-webkit-scrollbar{width:10px}.ai-report-scroll::-webkit-scrollbar-thumb{background:#c5d9ff;border-radius:999px}.ai-hero-card{padding:24px 24px 20px;border-radius:20px;background:radial-gradient(circle at top left,rgba(64,158,255,.18),transparent 36%),linear-gradient(145deg,#ffffff 0%,#f4f8ff 100%);border:1px solid #d8e6ff;box-shadow:0 18px 36px rgba(70,110,180,.12);margin-bottom:16px}.ai-hero-title{font-size:13px;font-weight:800;letter-spacing:.16em;color:#7d8da5;margin-bottom:12px}.ai-hero-summary{font-size:18px;line-height:1.9;color:#24364b;font-weight:600}.ai-report-card{padding:18px;border-radius:18px;background:linear-gradient(180deg,#ffffff 0%,#f7faff 100%);border:1px solid #dce7f7;box-shadow:0 14px 28px rgba(31,45,61,.08)}.ai-report-card__title{font-size:20px;font-weight:800;color:#21324a;margin-bottom:14px;text-align:left}.tx{grid-column:1/-1;line-height:1.8}.detail-header h3,.import-header h3{margin:0 0 16px;font-size:18px;font-weight:700;color:var(--hr-title)}.detail-layout,.import-layout{display:grid;gap:16px}.detail-card,.import-card{background:#fff;border:1px solid var(--hr-border);border-radius:8px;box-shadow:0 4px 16px rgba(31,35,41,.06);padding:16px}.detail-card{display:grid;gap:16px}.detail-meta-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.detail-meta-item{min-height:52px;border-radius:8px;background:#f8fbff;display:flex;align-items:center;justify-content:center;gap:6px;padding:0 12px;text-align:center}.detail-meta-item--span-2{grid-column:span 2}.detail-meta-label{font-weight:700;color:#303133}.detail-meta-value{font-weight:400;color:#606266;word-break:break-word}.detail-meta-value--accent{color:#409EFF;font-weight:700}.detail-section-title{font-size:16px;font-weight:700;color:var(--hr-title);text-align:center}.detail-card :deep(.el-table th),.detail-card :deep(.el-table td),.import-card--result :deep(.el-table th),.import-card--result :deep(.el-table td){text-align:center}.detail-card :deep(.el-table),.import-card--result :deep(.el-table){--el-table-header-bg-color:#fff;--el-table-tr-bg-color:#fff}.detail-card :deep(.el-table__row:hover > td){background:#f5faff}.detail-remark-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.detail-note-card{background:#fff;border:1px solid var(--hr-border);border-radius:8px;box-shadow:0 4px 16px rgba(31,35,41,.06);padding:12px;display:grid;gap:12px}.detail-note-title{font-size:15px;font-weight:700;color:var(--hr-title);text-align:center}.detail-note-content{min-height:112px;border:1px solid #dcdfe6;border-radius:8px;background:#f8fafc;padding:12px;line-height:1.8;color:#606266;white-space:pre-wrap;word-break:break-word;text-align:center}.detail-footer,.import-footer{display:flex;justify-content:flex-end;gap:16px;flex-wrap:wrap}.ai-report-footer{padding-top:6px}.detail-close-btn,.import-btn{height:40px;border-radius:8px;padding:0 18px}.detail-close-btn{border-color:#409EFF;color:#409EFF;background:#fff}.detail-close-btn:hover{background:#409EFF;color:#fff;border-color:#409EFF}.import-card{display:grid;gap:16px}.import-filter-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.import-control :deep(.el-input__wrapper),.import-control :deep(.el-select__wrapper){border-radius:8px;box-shadow:0 0 0 1px var(--hr-border) inset}.import-control :deep(.el-input__wrapper:hover),.import-control :deep(.el-select__wrapper:hover){box-shadow:0 0 0 1px #409EFF inset}.import-upload-row{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.import-upload-main{display:flex;align-items:center;gap:16px;flex-wrap:wrap}.import-file-meta{display:flex;align-items:center;gap:8px;color:var(--hr-info);font-size:14px}.import-file-icon{font-size:16px}.import-file-name{max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.import-tip{margin:0;color:#909399;font-size:12px}.import-result-head{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}.import-result-stats{display:flex;align-items:center;gap:16px;font-size:16px;font-weight:700}.import-result-stats .success{color:#67C23A}.import-result-stats .danger{color:#F56C6C}.import-btn--primary{background:#409EFF;border-color:#409EFF;color:#fff}.import-btn--outline{border-color:#409EFF;color:#409EFF;background:#fff}.import-btn--outline:hover{background:#409EFF;color:#fff}.import-btn--ghost{border-color:#dcdfe6;color:#606266;background:#fff}.import-btn--ghost:hover{border-color:#c0c4cc;color:#606266;background:#f5f7fa}@media (max-width:1200px){.g,.g4,.detail-meta-grid,.ai-result-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.detail-remark-grid{grid-template-columns:1fr}}@media (max-width:900px){.bar{flex-direction:column;align-items:stretch}.g,.g4,.detail-meta-grid,.import-filter-row,.ai-result-grid{grid-template-columns:1fr}.detail-meta-item--span-2{grid-column:span 1}.import-upload-row,.import-upload-main,.ai-inline{align-items:stretch;flex-direction:column}.import-file-name{max-width:100%}.ai-report-header{flex-direction:column}.ai-report-shell{height:min(786.82px,calc(100vh - 120px))}.ai-hero-summary{font-size:16px}.pp,.panel{height:auto}}
</style>
