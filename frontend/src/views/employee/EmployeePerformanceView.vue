<template>
  <div class="page-grid ep">
    <PageCard title="绩效查询" hide-header class="page-section panel panel--headerless">
      <div class="performance-toolbar bar">
        <div class="performance-filters fs">
          <el-select v-model="selectedPeriod" clearable placeholder="考核周期" class="performance-filter__period">
            <el-option v-for="item in periodOptions" :key="item" :label="item" :value="item" />
          </el-select>
          <el-select v-model="selectedStatus" clearable placeholder="状态筛选" class="performance-filter__status">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
      </div>

      <div class="performance-table-shell">
        <div class="performance-table-wrap">
          <el-table :data="pagedRows" width="100%" :height="TABLE_HEIGHT" v-loading="loading" class="performance-table">
            <template #empty>
              <el-empty description="暂无绩效记录" />
            </template>
            <el-table-column prop="period" label="考核周期" min-width="130" header-align="center" align="center" />
            <el-table-column prop="performanceScore" label="业绩得分" min-width="100" header-align="right" align="right">
              <template #default="scope">
                <span class="score-cell">{{ formatScore(scope.row.performanceScore) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="attitudeScore" label="态度得分" min-width="100" header-align="right" align="right">
              <template #default="scope">
                <span class="score-cell">{{ formatScore(scope.row.attitudeScore) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="abilityScore" label="能力得分" min-width="100" header-align="right" align="right">
              <template #default="scope">
                <span class="score-cell">{{ formatScore(scope.row.abilityScore) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="totalScore" label="总分" min-width="90" header-align="right" align="right">
              <template #default="scope">
                <span class="score-cell score-cell--strong">{{ formatScore(scope.row.totalScore) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" min-width="90" header-align="center" align="center">
              <template #default="scope">
                <el-tag :type="gradeTagType(scope.row.grade)" effect="light" round>{{ scope.row.grade || '—' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reviewer" label="考核人" min-width="110" header-align="center" align="center" />
            <el-table-column prop="status" label="状态" min-width="120" header-align="center" align="center">
              <template #default="scope">
                <el-tag :type="statusTagType(scope.row.status)" effect="light" round>{{ statusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="selfReview" label="员工自评" min-width="220" header-align="left">
              <template #default="scope">
                <button class="text-preview" type="button" @click="openDetail('员工自评', scope.row.selfReview)">
                  {{ previewText(scope.row.selfReview) }}
                </button>
              </template>
            </el-table-column>
            <el-table-column prop="managerReview" label="上级评价" min-width="220" header-align="left">
              <template #default="scope">
                <button class="text-preview" type="button" @click="openDetail('上级评价', scope.row.managerReview)">
                  {{ previewText(scope.row.managerReview) }}
                </button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="performance-pagination pg">
          <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="filteredRows.length" layout="slot, prev, pager, next" background>
            <span class="performance-total ttl">共计 {{ filteredRows.length }} 条</span>
          </el-pagination>
        </div>
      </div>
    </PageCard>

    <el-dialog v-model="detailVisible" :title="detailTitle" width="560px">
      <div class="detail-dialog__content">{{ detailContent || '暂无内容' }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { getPerformanceSummary } from '@/api/modules';

const PAGE_SIZE = 10;
const TABLE_HEIGHT = 'calc(100vh - 320px)';
const PREVIEW_LIMIT = 20;

const rows = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const selectedPeriod = ref('');
const selectedStatus = ref('');
const detailVisible = ref(false);
const detailTitle = ref('');
const detailContent = ref('');

const statusOptions = [
  { label: '待自评', value: '待自评' },
  { label: '待上级审核', value: '待审核' },
  { label: '已完成', value: '已完成' },
  { label: '已驳回', value: '驳回' },
];

const periodOptions = computed(() => [...new Set(rows.value.map((item) => item.period).filter(Boolean))]);

const filteredRows = computed(() => rows.value.filter((item) => {
  const matchesPeriod = !selectedPeriod.value || item.period === selectedPeriod.value;
  const matchesStatus = !selectedStatus.value || item.status === selectedStatus.value;
  return matchesPeriod && matchesStatus;
}));

const pagedRows = computed(() => filteredRows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));

watch([selectedPeriod, selectedStatus], () => {
  currentPage.value = 1;
});

const loadData = async () => {
  loading.value = true;
  try {
    const result = await getPerformanceSummary();
    rows.value = (result.data.records || []).map((item) => ({
      ...item,
      totalScore: item.totalScore ?? 0,
    }));
    currentPage.value = 1;
  } finally {
    loading.value = false;
  }
};

const formatScore = (value) => {
  const num = Number(value ?? 0);
  return Number.isInteger(num) ? String(num) : num.toFixed(2);
};

const previewText = (value) => {
  const text = String(value || '').trim();
  if (!text) return '暂无内容';
  return text.length > PREVIEW_LIMIT ? `${text.slice(0, PREVIEW_LIMIT)}...` : text;
};

const openDetail = (title, content) => {
  detailTitle.value = title;
  detailContent.value = String(content || '').trim();
  detailVisible.value = true;
};

const gradeTagType = (grade) => ({
  S: 'danger',
  A: 'success',
  B: 'primary',
  C: 'warning',
  D: 'info',
}[grade] || 'info');

const statusTagType = (status) => ({
  '待自评': 'primary',
  '待审核': 'warning',
  '已完成': 'success',
  '驳回': 'danger',
}[status] || 'info');

const statusText = (status) => ({
  '待自评': '待自评',
  '待审核': '待上级审核',
  '已完成': '已完成',
  '驳回': '已驳回',
}[status] || (status || '—'));

onMounted(loadData);
</script>

<style scoped>
.ep {
  display: grid;
  gap: 16px;
  height: calc(100vh - 148px);
}

.panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
  min-height: 0;
  height: 100%;
  box-sizing: border-box;
  border-radius: 24px;
  box-shadow: 0 16px 40px rgba(31, 42, 68, 0.06);
}

.panel--headerless :deep(.page-card__body) {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 16px;
  min-height: 0;
}

.bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.fs {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.performance-filter__period,
.performance-filter__status {
  width: 180px;
}

.performance-table-shell {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 16px;
  min-height: 0;
}

.performance-table-wrap {
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(64, 158, 255, 0.08);
  border-radius: 20px;
  padding: 10px 12px 0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.performance-table :deep(.el-table) {
  --el-table-border-color: transparent;
  --el-table-header-bg-color: #f4f6fb;
  --el-table-row-hover-bg-color: #edf5ff;
}

.performance-table :deep(th.el-table__cell) {
  background: #f4f6fb;
  color: var(--hr-title);
  font-weight: 700;
}

.performance-table :deep(.el-table__row td.el-table__cell) {
  height: 54px;
}

.performance-table :deep(.el-table__row:nth-child(even) td.el-table__cell) {
  background: #fbfcfe;
}

.performance-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background: #edf5ff !important;
}

.score-cell {
  display: inline-block;
  min-width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.score-cell--strong {
  font-weight: 700;
  color: var(--hr-title);
}

.text-preview {
  width: 100%;
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
  color: var(--hr-text, #334155);
  line-height: 1.6;
  cursor: pointer;
}

.text-preview:hover {
  color: #409eff;
}

.pg {
  display: flex;
  justify-content: flex-end;
  position: sticky;
  bottom: 0;
  z-index: 2;
  background: #fff;
  padding-top: 8px;
}

.ttl {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--hr-info);
  font-size: 13px;
}

.detail-dialog__content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--hr-text, #334155);
}

@media (max-width: 900px) {
  .performance-filter__period,
  .performance-filter__status {
    width: 100%;
  }

  .bar,
  .fs {
    align-items: stretch;
  }
}
</style>
