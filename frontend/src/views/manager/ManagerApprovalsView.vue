<template>
  <div class="page-grid approvals-page">
    <PageCard>
      <el-table :data="rows" width="100%" v-loading="loading">
        <el-table-column prop="applicant" label="申请人" min-width="120" align="center" header-align="center" />
        <el-table-column prop="type" label="申请类型" min-width="120" align="center" header-align="center" />
        <el-table-column prop="duration" label="时长" min-width="120" align="center" header-align="center" />
        <el-table-column prop="status" label="状态" min-width="120" align="center" header-align="center">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="260" align="center" header-align="center">
          <template #default="scope">
            <el-space wrap>
              <el-button size="small" @click="openDetail(scope.row)">详情</el-button>
              <template v-if="canOperate(scope.row)">
                <el-button type="primary" size="small" @click="handleDecision(scope.row, '已通过')">通过</el-button>
                <el-button size="small" @click="handleDecision(scope.row, '已驳回')">驳回</el-button>
              </template>
              <span v-else class="muted-action">已处理</span>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </PageCard>

    <el-dialog v-model="detailVisible" title="审批详情" width="920px" destroy-on-close align-center class="approval-detail-dialog">
      <div v-if="detailRecord" v-loading="detailLoading" class="approval-detail">
        <section class="approval-detail__section approval-detail__summary"><div><div class="approval-detail__eyebrow">{{ detailRecord.category }}</div><h3>{{ detailRecord.type }}</h3><p>{{ detailRecord.reason||'暂无事由说明' }}</p></div><el-tag :type="statusTagType(detailRecord.status)" effect="light">{{ detailRecord.status }}</el-tag></section>
        <section class="approval-detail__section"><div class="approval-detail__grid approval-detail__grid--two"><div class="approval-detail__field"><span>申请人</span><strong>{{ detailRecord.applicant }}</strong></div><div class="approval-detail__field"><span>申请工号</span><strong>{{ detailRecord.applicant_employee_no||'—' }}</strong></div><div class="approval-detail__field"><span>申请时间</span><strong>{{ formatDateTime(detailRecord.apply_time) }}</strong></div><div class="approval-detail__field"><span>审批层级</span><strong>{{ detailRecord.level_label||detailRecord.level||'—' }}</strong></div><div class="approval-detail__field"><span>申请类型</span><strong>{{ detailRecord.type||'—' }}</strong></div><div class="approval-detail__field"><span>时长/数量</span><strong>{{ detailRecord.duration||'—' }}</strong></div></div></section>
        <section v-if="detailRecord.asset_info?.length" class="approval-detail__section"><div class="approval-detail__section-title">标准资产信息</div><div class="approval-detail__grid approval-detail__grid--three"><div v-for="(item,index) in detailRecord.asset_info" :key="`${item.label}-${index}`" class="approval-detail__field approval-detail__field--asset"><span>{{ item.label }}</span><strong>{{ item.value||'—' }}</strong></div></div></section>
        <section class="approval-detail__section"><div class="approval-detail__section-title">关联信息</div><div class="approval-detail__grid approval-detail__grid--two"><div v-for="(item,index) in detailRecord.related_info||[]" :key="`${item.label}-${index}`" class="approval-detail__field"><span>{{ item.label }}</span><strong>{{ item.value||'—' }}</strong></div><div v-if="!(detailRecord.related_info||[]).length" class="approval-detail__empty">暂无关联信息</div></div></section>
        <section class="approval-detail__section"><div class="approval-detail__section-title">明细内容</div><div class="approval-detail__content">{{ detailRecord.detail_content||'暂无明细内容' }}</div></section>
        <section class="approval-detail__section"><div class="approval-detail__section-title">审批历史流转</div><div class="approval-history"><div v-for="(item,index) in detailRecord.history||[]" :key="`${item.node}-${index}`" class="approval-history__item"><div class="approval-history__dot"></div><div class="approval-history__body"><div class="approval-history__head"><strong>{{ item.node }}</strong><span>{{ formatDateTime(item.time) }}</span></div><div class="approval-history__meta">{{ item.approver }} · {{ item.result }}</div><div class="approval-history__comment">{{ item.comment||'无审批意见' }}</div></div></div></div></section>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { decideApproval, getApprovalDetail, getApprovalOverview } from '@/api/modules';

const rows = ref([]);
const loading = ref(false);
const detailVisible = ref(false);
const detailLoading = ref(false);
const detailRecord = ref(null);
const canOperate = (row) => row.status === '待审批' && row.level === 'manager';
const statusTagType = (status) => status === '已通过' ? 'success' : status === '已驳回' ? 'danger' : status === '已撤销' ? 'info' : 'warning';
const formatDateTime = (value) => !value ? '—' : String(value).replace('T', ' ').slice(0, 19) || '—';
const isAssetApproval = (type) => ['办公用品领用', '资产领用', '办公设备领用', '公章使用', '会议室申请', '会议室预约', '用车申请'].some((item) => String(type || '').includes(item));
const pickInfo = (record, labels) => {
  const items = record?.related_info || [];
  const hit = items.find((item) => labels.some((label) => String(item.label || '').includes(label)));
  return hit?.value || '';
};
const inferAssetName = (record) => pickInfo(record, ['资产名称', '用品名称', '物品名称', '资源名称', '公章名称', '会议室', '车辆']) || String(record?.duration || '').replace(/\s*\d+.*$/, '').trim() || String(record?.type || '审批资产');
const inferAssetType = (record) => {
  const type = String(record?.type || '');
  if (type.includes('公章')) return '印章';
  if (type.includes('会议室')) return '会议资源';
  if (type.includes('用车')) return '车辆';
  if (type.includes('办公用品')) return '办公耗材';
  if (type.includes('设备')) return '办公设备';
  return '行政物料';
};
const buildAssetInfo = (record) => !isAssetApproval(record?.type) ? [] : [
  { label: '资产名称', value: pickInfo(record, ['资产名称', '用品名称', '物品名称', '资源名称', '公章名称', '会议室', '车辆']) || inferAssetName(record) },
  { label: '资产类型', value: pickInfo(record, ['资产类型', '品类类型']) || inferAssetType(record) },
  { label: '申请数量', value: pickInfo(record, ['申请数量', '领用数量', '数量']) || String(record?.duration || '1') },
  { label: '使用部门', value: pickInfo(record, ['申请部门', '使用部门', '所属部门']) || record?.department || '综合管理部' },
  { label: '存放位置', value: pickInfo(record, ['存放位置', '使用地点']) || '系统自动匹配' },
  { label: '同步说明', value: '审批通过后同步进入行政资产台账' },
];
const normalizeDetailRecord = (record) => {
  if (!record) return null;
  const assetInfo = buildAssetInfo(record);
  return {
    ...record,
    asset_info: assetInfo,
    related_info: isAssetApproval(record.type) ? [...assetInfo, ...(record.related_info || [])] : (record.related_info || []),
  };
};

const loadRows = async () => {
  loading.value = true;
  try {
    const result = await getApprovalOverview();
    rows.value = (result.data.records || []).filter((item) => item.level === 'manager' || item.category === '人事审批');
  } finally {
    loading.value = false;
  }
};

const openDetail = async (row) => {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    const result = await getApprovalDetail(row.id);
    detailRecord.value = normalizeDetailRecord(result.data ? { ...row, ...result.data } : row);
  } finally {
    detailLoading.value = false;
  }
};

const handleDecision = async (row, decision) => {
  await decideApproval(row.id, { decision, comment: decision });
  ElMessage.success(`已${decision}`);
  if (detailVisible.value && detailRecord.value?.id === row.id) {
    const detail = await getApprovalDetail(row.id);
    detailRecord.value = normalizeDetailRecord(detail.data || null);
  }
  loadRows();
};

onMounted(loadRows);
</script>

<style scoped>
.page-grid,.approval-detail,.approval-history{display:grid;gap:16px}
.approval-detail__summary,.approval-history__head{display:flex;gap:12px}
.muted-action{color:#909399;font-size:13px}
:deep(.approval-detail-dialog){max-height:calc(100vh - 64px);display:flex;flex-direction:column;overflow:hidden}
:deep(.approval-detail-dialog .el-dialog__body){height:600px;max-height:600px;overflow-y:auto;box-sizing:border-box}
.approval-detail__section{border:1px solid var(--hr-border);border-radius:12px;padding:16px;background:#fff}
.approval-detail__summary{justify-content:space-between;align-items:flex-start}
.approval-detail__eyebrow{margin-bottom:8px;color:var(--hr-primary);font-size:12px;letter-spacing:.08em}
.approval-detail__summary h3{margin:0 0 8px;color:var(--hr-title);font-size:22px}
.approval-detail__summary p{margin:0;color:var(--hr-info);line-height:1.8}
.approval-detail__section-title{margin-bottom:12px;font-size:14px;font-weight:600;color:var(--hr-title)}
.approval-detail__grid{display:grid;gap:12px 16px}
.approval-detail__grid--two{grid-template-columns:repeat(2,minmax(0,1fr))}
.approval-detail__grid--three{grid-template-columns:repeat(3,minmax(0,1fr))}
.approval-detail__field{display:grid;gap:6px;padding:12px 14px;border-radius:10px;background:#f8fbff;border:1px solid #e3edf9}
.approval-detail__field--asset{background:linear-gradient(180deg,#f7fbff 0%,#eef6ff 100%);border-color:#d8e9ff}
.approval-detail__field span{color:var(--hr-info);font-size:12px}
.approval-detail__field strong{color:var(--hr-title);font-size:14px;font-weight:600}
.approval-detail__content,.approval-history__comment{line-height:1.9;color:var(--hr-title);white-space:pre-wrap}
.approval-detail__empty,.approval-history__meta,.approval-history__head span{color:var(--hr-info);font-size:13px}
.approval-history__item{display:grid;grid-template-columns:12px 1fr;gap:12px}
.approval-history__dot{width:12px;height:12px;border-radius:50%;background:var(--hr-primary);margin-top:6px}
.approval-history__body{padding-bottom:12px;border-bottom:1px dashed #d9e5f3}
.approval-history__head{justify-content:space-between;margin-bottom:6px}
.approval-history__head strong{color:var(--hr-title)}
@media (max-width:900px){.approval-detail__grid--two,.approval-detail__grid--three{grid-template-columns:1fr}}
</style>
