<template>
  <div class="page-grid ep approvals-page">
    <PageCard title="审批中心" description="分类处理人事、行政、资产、综合审批。" class="page-section panel approvals-card approvals-card--plain-header">
      <div class="approvals-toolbar bar">
        <div class="approvals-toolbar__filters fs">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
          <el-select v-model="typeFilter" placeholder="审批类型筛选" clearable style="width: 180px">
            <el-option v-for="item in typeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </div>
        <div class="approvals-toolbar__actions bar-actions">
          <el-button :disabled="!selectedRows.length" type="primary" plain @click="openBatchDialog('已通过')">批量通过</el-button>
          <el-button :disabled="!selectedRows.length" type="danger" plain @click="openBatchDialog('已驳回')">批量驳回</el-button>
        </div>
      </div>
      <div class="tb">
      <el-table ref="tableRef" :data="pagedRows" :height="TABLE_HEIGHT" width="100%" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="48" :selectable="canSelectRow" align="center" header-align="center" />
        <el-table-column prop="category" label="分类" min-width="120" align="center" header-align="center" />
        <el-table-column prop="applicant" label="申请人" min-width="120" align="center" header-align="center" />
        <el-table-column prop="apply_time" label="申请时间" min-width="180" align="center" header-align="center"><template #default="scope">{{ formatDateTime(scope.row.apply_time) }}</template></el-table-column>
        <el-table-column prop="type" label="类型" min-width="120" align="center" header-align="center" />
        <el-table-column prop="duration" label="时长/数量" min-width="120" align="center" header-align="center" />
        <el-table-column prop="level_label" label="审批层级" min-width="140" align="center" header-align="center" />
        <el-table-column prop="status" label="状态" min-width="120" align="center" header-align="center"><template #default="scope"><el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status }}</el-tag></template></el-table-column>
        <el-table-column label="操作" min-width="260" fixed="right" align="center" header-align="center"><template #default="scope"><el-space wrap><el-button size="small" @click="openDetail(scope.row)">详情</el-button><el-button size="small" type="primary" :disabled="!isPending(scope.row)" @click="openDecisionDialog(scope.row,'已通过')">通过</el-button><el-button size="small" type="danger" plain :disabled="!isPending(scope.row)" @click="openDecisionDialog(scope.row,'已驳回')">驳回</el-button></el-space></template></el-table-column>
      </el-table>
      </div>
      <div class="approvals-page__pagination pg"><el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="rows.length" layout="slot, prev, pager, next" background><span class="approvals-page__total ttl">共计 {{ rows.length }} 条</span></el-pagination></div>
    </PageCard>
    <el-dialog v-model="detailVisible" title="审批详情" width="920px" destroy-on-close align-center class="approval-detail-dialog">
      <div v-if="detailRecord" v-loading="detailLoading" class="approval-detail">
        <section class="approval-detail__section approval-detail__summary"><div><div class="approval-detail__eyebrow">{{ detailRecord.category }}</div><h3>{{ detailRecord.type }}</h3><p>{{ detailRecord.reason||'暂无事由说明' }}</p></div><el-tag :type="statusTagType(detailRecord.status)" effect="light">{{ detailRecord.status }}</el-tag></section>
        <section class="approval-detail__section"><div class="approval-detail__grid approval-detail__grid--two"><div class="approval-detail__field"><span>申请人</span><strong>{{ detailRecord.applicant }}</strong></div><div class="approval-detail__field"><span>申请工号</span><strong>{{ detailRecord.applicant_employee_no||'—' }}</strong></div><div class="approval-detail__field"><span>申请时间</span><strong>{{ formatDateTime(detailRecord.apply_time) }}</strong></div><div class="approval-detail__field"><span>审批层级</span><strong>{{ detailRecord.level_label||'—' }}</strong></div><div class="approval-detail__field"><span>申请类型</span><strong>{{ detailRecord.type||'—' }}</strong></div><div class="approval-detail__field"><span>时长/数量</span><strong>{{ detailRecord.duration||'—' }}</strong></div></div></section>
        <section v-if="detailRecord.asset_info?.length" class="approval-detail__section"><div class="approval-detail__section-title">标准资产信息</div><div class="approval-detail__grid approval-detail__grid--three"><div v-for="(item,index) in detailRecord.asset_info" :key="`${item.label}-${index}`" class="approval-detail__field approval-detail__field--asset"><span>{{ item.label }}</span><strong>{{ item.value||'—' }}</strong></div></div></section><section class="approval-detail__section"><div class="approval-detail__section-title">关联信息</div><div class="approval-detail__grid approval-detail__grid--two"><div v-for="(item,index) in detailRecord.related_info||[]" :key="`${item.label}-${index}`" class="approval-detail__field"><span>{{ item.label }}</span><strong>{{ item.value||'—' }}</strong></div><div v-if="!(detailRecord.related_info||[]).length" class="approval-detail__empty">暂无关联信息</div></div></section>
        <section class="approval-detail__section"><div class="approval-detail__section-title">明细内容</div><div class="approval-detail__content">{{ detailRecord.detail_content||'暂无明细内容' }}</div></section>
        <section class="approval-detail__section"><div class="approval-detail__section-title">审批历史流转</div><div class="approval-history"><div v-for="(item,index) in detailRecord.history||[]" :key="`${item.node}-${index}`" class="approval-history__item"><div class="approval-history__dot"></div><div class="approval-history__body"><div class="approval-history__head"><strong>{{ item.node }}</strong><span>{{ formatDateTime(item.time) }}</span></div><div class="approval-history__meta">{{ item.approver }} · {{ item.result }}</div><div class="approval-history__comment">{{ item.comment||'无审批意见' }}</div></div></div></div></section>
      </div>
    </el-dialog>
    <el-dialog v-model="decisionVisible" :title="decisionForm.decision==='已通过'?'确认通过审批':'确认驳回审批'" width="520px" destroy-on-close align-center>
      <div class="approval-action"><p class="approval-action__tip">{{ decisionForm.decision==='已通过'?'确认通过该审批？通过后将按审批链自动流转或完成归档。':'确认驳回该审批？驳回后将终止当前审批流程，请填写明确原因。' }}</p><el-input v-model="decisionForm.comment" type="textarea" :rows="5" :placeholder="decisionForm.decision==='已通过'?'请输入审批意见（可选）':'请输入驳回原因（必填）'" maxlength="200" show-word-limit /></div>
      <template #footer><el-button @click="decisionVisible=false">取消</el-button><el-button :type="decisionForm.decision==='已通过'?'primary':'danger'" @click="submitDecision">确认</el-button></template>
    </el-dialog>
    <el-dialog v-model="batchVisible" :title="batchForm.decision==='已通过'?'批量通过审批':'批量驳回审批'" width="520px" destroy-on-close align-center>
      <div class="approval-action"><p class="approval-action__tip">已选择 {{ selectedRows.length }} 条待审批记录，{{ batchForm.decision==='已通过'?'确认批量通过？':'确认批量驳回？' }}</p><el-input v-model="batchForm.comment" type="textarea" :rows="5" :placeholder="batchForm.decision==='已通过'?'请输入统一审批意见（可选）':'请输入统一驳回原因（必填）'" maxlength="200" show-word-limit /></div>
      <template #footer><el-button @click="batchVisible=false">取消</el-button><el-button :type="batchForm.decision==='已通过'?'primary':'danger'" @click="submitBatchDecision">确认</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed,onMounted,ref,watch } from 'vue';
import { ElMessage } from 'element-plus';
import { persistApprovedAssetRequest } from '@/utils/assetApprovalSync';
import PageCard from '@/components/PageCard.vue';
import { batchDecideApproval,decideApproval,getApprovalDetail,getApprovalOverview } from '@/api/modules';
const PAGE_SIZE=10,TABLE_HEIGHT='calc(100vh - 320px)',statusOptions=['待审批','已通过','已驳回','已撤销'],typeOptions=['请假','加班','补卡','转正','调岗','离职','薪酬异动','办公用品领用','资产领用','办公设备领用','公章使用','会议室申请','会议室预约','用车申请'];
const STATUS_SORT_ORDER = { '待审批': 0, '已通过': 1, '已驳回': 2, '已撤销': 3 };
const loading=ref(false),rows=ref([]),currentPage=ref(1),statusFilter=ref(''),typeFilter=ref(''),selectedRows=ref([]),tableRef=ref(),detailVisible=ref(false),detailLoading=ref(false),detailRecord=ref(null),decisionVisible=ref(false),batchVisible=ref(false);
const decisionForm=ref({row:null,decision:'已通过',comment:''}),batchForm=ref({decision:'已通过',comment:''});
const pagedRows=computed(()=>rows.value.slice((currentPage.value-1)*PAGE_SIZE,currentPage.value*PAGE_SIZE));
const sortApprovalRows = (items) => [...items].sort((a, b) => {
  const orderDiff = (STATUS_SORT_ORDER[a.status] ?? 99) - (STATUS_SORT_ORDER[b.status] ?? 99);
  if (orderDiff !== 0) return orderDiff;
  return String(b.apply_time || '').localeCompare(String(a.apply_time || ''));
});
const loadRows=async()=>{loading.value=true;try{const result=await getApprovalOverview({status:statusFilter.value||undefined,type:typeFilter.value||undefined});rows.value=sortApprovalRows((result.data.records||[]).map(normalizeApprovalRecord));currentPage.value=1;selectedRows.value=[];tableRef.value?.clearSelection?.();}finally{loading.value=false;}};
watch([statusFilter,typeFilter],()=>{loadRows();});
const isPending=row=>row.status==='待审批',canSelectRow=row=>isPending(row),handleSelectionChange=value=>{selectedRows.value=value.filter(item=>isPending(item));};
const statusTagType=status=>status==='已通过'?'success':status==='已驳回'?'danger':status==='已撤销'?'info':'warning';
const formatDateTime=value=>!value?'—':String(value).replace('T',' ').slice(0,19)||'—';
const isAssetApproval=type=>['办公用品领用','资产领用','办公设备领用','公章使用','会议室申请','会议室预约','用车申请'].some(item=>String(type||'').includes(item));
const pickInfo=(record,labels)=>{const items=record?.related_info||[];const hit=items.find(item=>labels.some(label=>String(item.label||'').includes(label)));return hit?.value||'';};
const inferAssetName=record=>pickInfo(record,['资产名称','用品名称','物品名称','资源名称','公章名称','会议室','车辆'])||String(record?.duration||'').replace(/\s*\d+.*$/,'').trim()||String(record?.type||'审批资产');
const inferAssetType=record=>{const type=String(record?.type||'');if(type.includes('公章'))return'印章';if(type.includes('会议室'))return'会议资源';if(type.includes('用车'))return'车辆';if(type.includes('办公用品'))return'办公耗材';if(type.includes('设备'))return'办公设备';return'行政物料';};
const buildAssetInfo=record=>!isAssetApproval(record?.type)?[]:[
  {label:'资产名称',value:pickInfo(record,['资产名称','用品名称','物品名称','资源名称','公章名称','会议室','车辆'])||inferAssetName(record)},
  {label:'资产类型',value:pickInfo(record,['资产类型','品类类型'])||inferAssetType(record)},
  {label:'申请数量',value:pickInfo(record,['申请数量','领用数量','数量'])||String(record?.duration||'1')},
  {label:'使用部门',value:pickInfo(record,['申请部门','使用部门','所属部门'])||record?.department||'综合管理部'},
  {label:'存放位置',value:pickInfo(record,['存放位置','使用地点'])||'系统自动匹配'},
  {label:'同步说明',value:`审批通过后同步进入行政资产台账`},
];
const normalizeApprovalRecord=record=>{if(!record)return null;const assetInfo=buildAssetInfo(record);return{...record,asset_info:assetInfo,related_info:isAssetApproval(record.type)?[...assetInfo,...(record.related_info||[])]:record.related_info||[]};};
const normalizeDetailRecord=record=>normalizeApprovalRecord(record);
const openDetail=async(row)=>{detailVisible.value=true;detailLoading.value=true;try{const result=await getApprovalDetail(row.id);detailRecord.value=normalizeDetailRecord(result.data?{...row,...result.data}:row);}finally{detailLoading.value=false;}};
const openDecisionDialog=(row,decision)=>{if(!isPending(row)) return;decisionForm.value={row,decision,comment:''};decisionVisible.value=true;};
const submitDecision=async()=>{const {row,decision,comment}=decisionForm.value;if(!row) return;if(decision==='已驳回'&&!String(comment||'').trim()){ElMessage.warning('驳回时请填写审批意见');return;}await decideApproval(row.id,{decision,comment:String(comment||'').trim()});if(decision==='已通过'){persistApprovedAssetRequest(detailRecord.value?.id===row.id?detailRecord.value:{...row,status:decision});}ElMessage.success(decision==='已通过'?'审批通过':'已驳回');decisionVisible.value=false;if(detailVisible.value&&detailRecord.value?.id===row.id){const detail=await getApprovalDetail(row.id);detailRecord.value=normalizeDetailRecord(detail.data||null);}await loadRows();};
const openBatchDialog=decision=>{if(!selectedRows.value.length) return;batchForm.value={decision,comment:''};batchVisible.value=true;};
const submitBatchDecision=async()=>{if(batchForm.value.decision==='已驳回'&&!String(batchForm.value.comment||'').trim()){ElMessage.warning('批量驳回时请填写统一审批意见');return;}const approvedRows=batchForm.value.decision==='已通过'?selectedRows.value.map(normalizeApprovalRecord):[];await batchDecideApproval({ids:selectedRows.value.map(item=>item.id),decision:batchForm.value.decision,comment:String(batchForm.value.comment||'').trim()});approvedRows.forEach(item=>persistApprovedAssetRequest({...item,status:'已通过'}));ElMessage.success(batchForm.value.decision==='已通过'?'批量审批通过':'批量驳回成功');batchVisible.value=false;await loadRows();};
onMounted(loadRows);
</script>

<style scoped>
.page-grid,.approvals-page :deep(.page-card__body),.approval-detail,.approval-history,.approval-action{display:grid;gap:16px}.approval-detail__summary,.approval-history__head{display:flex;gap:12px}.page-grid{grid-template-rows:minmax(0,1fr);gap:16px;height:calc(100vh - 148px)}.approvals-card{height:100%;min-height:0}.approvals-card :deep(.page-card__body){min-height:0;height:100%}.panel{display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:16px;padding:16px;min-height:0;height:100%;box-sizing:border-box}.tb{min-height:0;overflow:hidden}.approvals-card--plain-header :deep(.page-card__header > div:first-child){display:none}.approvals-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.approvals-toolbar__filters,.approvals-toolbar__actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.approvals-page :deep(.el-table th.el-table__cell){height:48px;padding:10px 0}.approvals-page :deep(.el-table .el-table__cell){padding:10px 0}.approvals-page :deep(.el-table .cell){line-height:24px}.approvals-page__pagination{display:flex;justify-content:flex-end;position:sticky;bottom:0;z-index:2;padding-top:16px;background:transparent}.approvals-page__pagination :deep(.el-pagination){padding:0;border-radius:0;background:transparent;box-shadow:none;border:none}.approvals-page__pagination :deep(.el-pagination.is-background){background:transparent;border:none;box-shadow:none}.approvals-page__pagination :deep(.btn-prev),.approvals-page__pagination :deep(.btn-next),.approvals-page__pagination :deep(.el-pager li){border-radius:8px}.approvals-page__pagination :deep(.el-pager li.is-active){background:#409EFF;color:#fff}.approvals-page__total{display:inline-flex;align-items:center;padding:0 12px;color:var(--hr-info);font-size:13px}.approval-detail__section{border:1px solid var(--hr-border);border-radius:12px;padding:16px;background:#fff}.approval-detail__summary{justify-content:space-between;align-items:flex-start}.approval-detail__eyebrow{margin-bottom:8px;color:var(--hr-primary);font-size:12px;letter-spacing:.08em}.approval-detail__summary h3{margin:0 0 8px;color:var(--hr-title);font-size:22px}.approval-detail__summary p,.approval-action__tip{margin:0;color:var(--hr-info);line-height:1.8}.approval-detail__section-title{margin-bottom:12px;font-size:14px;font-weight:600;color:var(--hr-title)}.approval-detail__grid{display:grid;gap:12px 16px}.approval-detail__grid--two{grid-template-columns:repeat(2,minmax(0,1fr))}.approval-detail__grid--three{grid-template-columns:repeat(3,minmax(0,1fr))}.approval-detail__field{display:grid;gap:6px;padding:12px 14px;border-radius:10px;background:#f8fbff;border:1px solid #e3edf9}.approval-detail__field--asset{background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border-color:#d8e9ff}.approval-detail__field span{color:var(--hr-info);font-size:12px}.approval-detail__field strong{color:var(--hr-title);font-size:14px;font-weight:600}.approval-detail__content,.approval-history__comment{line-height:1.9;color:var(--hr-title);white-space:pre-wrap}.approval-detail__empty,.approval-history__meta,.approval-history__head span{color:var(--hr-info);font-size:13px}.approval-history__item{display:grid;grid-template-columns:12px 1fr;gap:12px}.approval-history__dot{width:12px;height:12px;border-radius:50%;background:var(--hr-primary);margin-top:6px}.approval-history__body{padding-bottom:12px;border-bottom:1px dashed #d9e5f3}.approval-history__head{justify-content:space-between;margin-bottom:6px}.approval-history__head strong{color:var(--hr-title)}:deep(.approval-detail-dialog){max-height:calc(100vh - 64px);display:flex;flex-direction:column;overflow:hidden}:deep(.approval-detail-dialog .el-dialog__body){height:600px;max-height:600px;overflow-y:auto;box-sizing:border-box}@media (max-width:900px){.page-grid,.approvals-card,.panel{height:auto}.approval-detail__grid--two,.approval-detail__grid--three{grid-template-columns:1fr}.approvals-toolbar,.approvals-toolbar__filters,.approvals-toolbar__actions{align-items:stretch}}
</style>
