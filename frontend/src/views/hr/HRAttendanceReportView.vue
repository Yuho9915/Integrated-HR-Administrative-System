<template>
  <div class="page-grid ep attendance-report-page">
    <section class="report-panel page-section panel">
      <div class="report-toolbar bar">
        <div class="report-toolbar__left fs">
          <el-select v-model="departmentFilter" clearable placeholder="部门筛选" class="filter-control">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item" />
          </el-select>
          <el-date-picker v-model="monthFilter" type="month" value-format="YYYY-MM" placeholder="选择月份" class="filter-control month-control" />
          <el-input v-model="searchKeyword" placeholder="搜索部门/工号" clearable class="search-control" />
        </div>
        <div class="report-toolbar__right bar-actions">
          <el-button type="primary" @click="dialogVisible = true">考勤导入</el-button>
          <el-button v-if="isHrRole" type="primary" plain class="ai-summary-btn" :loading="aiLoading" @click="openAiSummaryReport">
            <el-icon><MagicStick /></el-icon>
            <span>AI 生成汇总报表</span>
          </el-button>
        </div>
      </div>

      <div class="report-table-wrap">
        <el-table :data="pagedRows" :height="tableHeight" width="100%" v-loading="loading" class="full-table">
          <el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center" />
          <el-table-column prop="attendanceRate" label="出勤率" min-width="120" align="center" header-align="center" />
          <el-table-column prop="lateTimes" label="迟到次数" min-width="120" align="center" header-align="center" />
          <el-table-column prop="earlyTimes" label="早退次数" min-width="120" align="center" header-align="center" />
          <el-table-column prop="leaveHours" label="请假时长" min-width="120" align="center" header-align="center" />
          <el-table-column prop="absenteeismDays" label="旷工天数" min-width="120" align="center" header-align="center" />
          <el-table-column prop="abnormalCount" label="异常人数" min-width="120" align="center" header-align="center" />
          <el-table-column label="操作" min-width="220" fixed="right" align="center" header-align="center">
            <template #default="scope">
              <div class="action-cell">
                <el-button link type="primary" @click="openDetailDialog(scope.row.department)">查看明细</el-button>
                <el-button link type="primary" @click="exportDepartmentRows(scope.row.department)">导出报表</el-button>
              </div>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无考勤数据" />
          </template>
        </el-table>
        </div>
      <div class="report-pagination pg">
        <el-pagination v-model:current-page="currentPage" :page-size="PAGE_SIZE" :total="filteredRows.length" layout="slot, prev, pager, next" background>
          <span class="report-pagination__total ttl">共计 {{ filteredRows.length }} 条</span>
        </el-pagination>
      </div>
    </section>

    <el-dialog v-model="detailDialogVisible" title="考勤明细" width="1200px" top="6vh" destroy-on-close align-center>
      <div class="detail-toolbar">
        <el-input v-model="detailSearchKeyword" placeholder="搜索姓名/工号" clearable class="detail-search" />
        <el-date-picker v-model="detailDateRange" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" range-separator="至" class="detail-date" />
        <el-select v-model="detailStatusFilter" clearable placeholder="考勤状态" class="detail-status">
          <el-option v-for="item in attendanceStatusOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </div>
      <el-table :data="detailRows" width="100%" height="520">
        <el-table-column prop="employeeNo" label="工号" min-width="120" align="center" header-align="center" />
        <el-table-column prop="name" label="姓名" min-width="110" align="center" header-align="center" />
        <el-table-column prop="department" label="部门" min-width="140" align="center" header-align="center" />
        <el-table-column prop="date" label="考勤日期" min-width="120" align="center" header-align="center" />
        <el-table-column prop="shouldAttendance" label="应出勤" min-width="90" align="center" header-align="center" />
        <el-table-column prop="actualAttendance" label="实出勤" min-width="90" align="center" header-align="center" />
        <el-table-column label="上班打卡时间" min-width="120" align="center" header-align="center">
          <template #default="scope">{{ normalizeClockValue(scope.row.checkIn) || '—' }}</template>
        </el-table-column>
        <el-table-column label="下班打卡时间" min-width="120" align="center" header-align="center">
          <template #default="scope">{{ normalizeClockValue(scope.row.checkOut) || '—' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="考勤状态" min-width="110" align="center" header-align="center" />
        <el-table-column prop="lateMinutes" label="迟到分钟" min-width="100" align="center" header-align="center" />
        <el-table-column prop="earlyMinutes" label="早退分钟" min-width="100" align="center" header-align="center" />
        <el-table-column prop="absenteeismDays" label="旷工天数" min-width="100" align="center" header-align="center" />
        <el-table-column prop="missingCardCount" label="缺卡次数" min-width="100" align="center" header-align="center" />
        <el-table-column prop="leaveType" label="请假类型" min-width="100" align="center" header-align="center" />
        <el-table-column prop="overtimeHours" label="加班小时" min-width="100" align="center" header-align="center" />
        <el-table-column prop="remark" label="备注" min-width="180" align="center" header-align="center" show-overflow-tooltip />
        <template #empty>
          <el-empty description="暂无符合条件的考勤明细" />
        </template>
      </el-table>
    </el-dialog>

    <el-dialog v-model="dialogVisible" title="考勤数据导入" width="760px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="import-grid">
          <el-form-item label="导入月份" prop="month">
            <el-date-picker v-model="form.month" type="month" value-format="YYYY-MM" placeholder="选择导入月份" style="width: 100%" />
          </el-form-item>
          <el-form-item label="上传考勤文件" prop="file">
            <div class="upload-card">
              <div class="upload-header">
                <span>上传考勤文件</span>
                <button class="template-link" type="button" @click="downloadTemplate">下载模板</button>
              </div>
              <el-upload action="#" :auto-upload="false" :show-file-list="true" :limit="1" accept=".xlsx" :on-change="handleFileChange" :on-remove="handleFileRemove">
                <el-button type="primary">选择文件</el-button>
                <template #tip>
                  <div class="upload-tip">仅支持 .xlsx，文件大小不超过 20MB，选择后自动解析</div>
                </template>
              </el-upload>
            </div>
          </el-form-item>
        </div>
      </el-form>

      <div class="parse-panel page-section">
        <div class="parse-panel__header">
          <h4>解析结果</h4>
          <span>{{ parseStateText }}</span>
        </div>
        <el-progress v-if="parsing || parseResult.total_count" :percentage="parsePercentage" :status="parsing ? '' : parseResult.error_count ? 'warning' : 'success'" />
        <div class="parse-metrics">
          <div class="parse-metric"><span>总条数</span><strong>{{ parseResult.total_count }}</strong></div>
          <div class="parse-metric"><span>成功条数</span><strong>{{ parseResult.success_count }}</strong></div>
          <div class="parse-metric"><span>异常条数</span><strong>{{ parseResult.error_count }}</strong></div>
        </div>
        <el-button v-if="parseResult.error_count" class="download-error" @click="downloadErrorList">下载异常清单</el-button>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!fileRef || parsing" :loading="submitting" @click="confirmImport">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="aiDialogVisible" class="attendance-ai-dialog" width="min(960px, calc(100vw - 32px))" destroy-on-close align-center>
      <template #header>
        <div class="attendance-ai-header">
          <div>
            <div class="attendance-ai-eyebrow">ATTENDANCE SUMMARY</div>
            <h3>{{ aiReport.title }}</h3>
          </div>
          <el-button type="primary" plain class="attendance-ai-copy" @click="copyAiReport">
            <el-icon><DocumentCopy /></el-icon>
            <span>复制原文</span>
          </el-button>
        </div>
      </template>
      <div class="attendance-ai-body" v-loading="aiLoading">
        <div class="attendance-ai-report-shell">
          <section class="attendance-ai-hero">
            <div class="attendance-ai-hero__label">执行摘要</div>
            <div class="attendance-ai-hero__text">{{ aiReportView.summary }}</div>
          </section>

          <section v-if="aiReportView.sections.length" class="attendance-ai-grid">
            <article v-for="section in aiReportView.sections" :key="section.title" class="attendance-ai-card">
              <div class="attendance-ai-card__title">{{ section.title }}</div>
              <div class="attendance-ai-points">
                <div v-for="(item,index) in section.items" :key="`${section.title}-${index}`" class="attendance-ai-point">{{ item }}</div>
              </div>
            </article>
          </section>

          <section class="attendance-ai-original">
            <div class="attendance-ai-original__head">
              <div>
                <div class="attendance-ai-original__eyebrow">ORIGINAL TEXT</div>
                <h4>可复制原文</h4>
              </div>
              <el-button type="primary" plain class="attendance-ai-copy attendance-ai-copy--inline" @click="copyAiReport">
                <el-icon><DocumentCopy /></el-icon>
                <span>复制原文</span>
              </el-button>
            </div>
            <div class="attendance-ai-content">{{ aiReportView.original }}</div>
          </section>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, DocumentCopy } from '@element-plus/icons-vue';
import { storeToRefs } from 'pinia';

import { generateAttendanceSummaryReport, getAttendanceOverview, getEmployeeMeta, getLeaves, importAttendanceFile, parseAttendanceFile } from '@/api/modules';
import { useAppStore } from '@/stores/app';
import { exportWorkbook } from '@/utils/export';

const PAGE_SIZE = 10;
const tableHeight = 'calc(100vh - 320px)';
const appStore = useAppStore();
const { user } = storeToRefs(appStore);
const isHrRole = computed(() => user.value?.role === 'hr');
const attendanceStatusOptions = ['正常', '迟到', '早退', '旷工', '请假', '外勤', '出差'];
const currentPage = ref(1);
const rawRows = ref([]);
const leaves = ref([]);
const loading = ref(false);
const parsing = ref(false);
const submitting = ref(false);
const aiLoading = ref(false);
const dialogVisible = ref(false);
const detailDialogVisible = ref(false);
const aiDialogVisible = ref(false);
const activeDepartment = ref('');
const detailSearchKeyword = ref('');
const detailDateRange = ref([]);
const detailStatusFilter = ref('');
const fileRef = ref(null);
const formRef = ref();
const departmentFilter = ref('');
const monthFilter = ref('2026-04');
const searchKeyword = ref('');
const departmentMeta = ref([]);
const aiReport = reactive({ title: 'AI考勤汇总报表', content: '' });
const aiReportView = computed(() => {
  const lines = String(aiReport.content || '').split('\n').map((line) => line.trim()).filter(Boolean);
  const sections = [];
  let summary = '';
  let currentSection = null;
  lines.forEach((line, index) => {
    const isHeading = /[：:]$/.test(line) && !line.startsWith('-');
    if (index === 0 && !isHeading) {
      summary = line;
      return;
    }
    if (isHeading) {
      currentSection = { title: line.replace(/[：:]$/, ''), items: [] };
      sections.push(currentSection);
      return;
    }
    if (!currentSection) {
      summary = summary ? `${summary} ${line}` : line;
      return;
    }
    currentSection.items.push(line.replace(/^[-•]\s*/, ''));
  });
  return {
    summary: summary || 'AI 已生成考勤汇总分析。',
    sections,
    original: aiReport.content || '',
  };
});
const form = reactive({ month: '2026-04', file: null });
const parseResult = reactive({ total_count: 0, success_count: 0, error_count: 0, errors: [] });

const rules = {
  month: [{ required: true, message: '请选择导入月份', trigger: 'change' }],
  file: [{ required: true, message: '请上传考勤文件', trigger: 'change' }],
};

const parsePercentage = computed(() => {
  if (parsing.value) return 65;
  if (!parseResult.total_count) return 0;
  return 100;
});

const parseStateText = computed(() => {
  if (parsing.value) return '解析中...';
  if (!fileRef.value) return '待上传';
  return parseResult.error_count ? '解析完成，存在异常' : '解析完成';
});

const inferDepartment = (employeeNo = '', department = '') => {
  if (department) return department;
  if (String(employeeNo).startsWith('HR')) return '综合管理部';
  if (String(employeeNo).startsWith('OPS')) return '运营中心';
  if (String(employeeNo).startsWith('DEV')) return '产品技术部';
  if (String(employeeNo).startsWith('MKT')) return '市场部';
  if (String(employeeNo).startsWith('SAL')) return '销售部';
  if (String(employeeNo).startsWith('FIN')) return '财务部';
  return '未分组';
};

const normalizeMonth = (item = {}) => String(item.month || item.date || '').slice(0, 7);
const normalizeClockValue = (value) => {
  const text = String(value || '').trim();
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(text) ? text : '';
};
const departmentOptions = computed(() => departmentMeta.value);

const filteredAttendanceRowsSource = computed(() => rawRows.value.filter((item) => {
  const monthMatch = !monthFilter.value || normalizeMonth(item) === monthFilter.value;
  const departmentMatch = !departmentFilter.value || inferDepartment(item.employeeNo, item.department) === departmentFilter.value;
  const keyword = searchKeyword.value.trim().toLowerCase();
  const keywordMatch = !keyword || String(item.department || '').toLowerCase().includes(keyword) || String(item.employeeNo || '').toLowerCase().includes(keyword);
  return monthMatch && departmentMatch && keywordMatch;
}));

const filteredAttendanceRows = computed(() => filteredAttendanceRowsSource.value.map((item) => ({
  ...item,
  shouldAttendance: Number(item.shouldAttendance ?? 1),
  actualAttendance: Number(item.actualAttendance ?? (String(item.status || '').includes('旷工') || String(item.status || '').includes('请假') ? 0 : 1)),
  absenteeismDays: Number(item.absenteeismDays ?? (String(item.status || '').includes('旷工') ? 1 : 0)),
  missingCardCount: Number(item.missingCardCount ?? (String(item.status || '').includes('缺卡') ? 1 : 0)),
})));

const filteredLeaves = computed(() => leaves.value.filter((item) => {
  const itemMonth = String(item.start_at || '').slice(0, 7) || String(item.period || '').slice(0, 7);
  const monthMatch = !monthFilter.value || itemMonth === monthFilter.value;
  const departmentMatch = !departmentFilter.value || inferDepartment(item.employee_no || item.employeeNo, item.department) === departmentFilter.value;
  return monthMatch && departmentMatch;
}));

const filteredRows = computed(() => {
  const departmentMap = new Map();
  filteredAttendanceRows.value.forEach((item) => {
    const department = inferDepartment(item.employeeNo, item.department);
    const current = departmentMap.get(department) || { department, total: 0, lateTimes: 0, earlyTimes: 0, absenteeismDays: 0, abnormalEmployees: new Set() };
    current.total += Number(item.shouldAttendance || 1);
    if (item.status !== '正常') current.abnormalEmployees.add(item.employeeNo || item.name || `${department}-${current.total}`);
    if (String(item.status).includes('迟到')) current.lateTimes += 1;
    if (String(item.status).includes('早退')) current.earlyTimes += 1;
    current.absenteeismDays += Number(item.absenteeismDays || (String(item.status).includes('旷工') ? 1 : 0));
    departmentMap.set(department, current);
  });

  const leaveHoursMap = filteredLeaves.value.reduce((acc, item) => {
    const department = inferDepartment(item.employee_no || item.employeeNo, item.department);
    acc[department] = (acc[department] || 0) + Number(item.days || 0) * 8;
    return acc;
  }, {});

  return Array.from(departmentMap.values()).map((item) => ({
    department: item.department,
    attendanceRate: `${item.total ? (((item.total - item.absenteeismDays) / item.total) * 100).toFixed(1) : '0.0'}%`,
    lateTimes: item.lateTimes,
    earlyTimes: item.earlyTimes,
    leaveHours: leaveHoursMap[item.department] || 0,
    absenteeismDays: Number(item.absenteeismDays.toFixed(2)),
    abnormalCount: item.abnormalEmployees.size,
  }));
});

const pagedRows = computed(() => filteredRows.value.slice((currentPage.value - 1) * PAGE_SIZE, currentPage.value * PAGE_SIZE));
const departmentDetailRows = computed(() => filteredAttendanceRows.value.filter((item) => inferDepartment(item.employeeNo, item.department) === activeDepartment.value));
const detailRows = computed(() => {
  const keyword = detailSearchKeyword.value.trim().toLowerCase();
  const [startDate, endDate] = detailDateRange.value || [];
  return departmentDetailRows.value.filter((item) => {
    const keywordMatch = !keyword || String(item.name || '').toLowerCase().includes(keyword) || String(item.employeeNo || '').toLowerCase().includes(keyword);
    const statusMatch = !detailStatusFilter.value || item.status === detailStatusFilter.value;
    const dateValue = String(item.date || '');
    const dateMatch = (!startDate || dateValue >= startDate) && (!endDate || dateValue <= endDate);
    return keywordMatch && statusMatch && dateMatch;
  });
});

watch([departmentFilter, monthFilter, searchKeyword], () => {
  currentPage.value = 1;
});

const loadData = async () => {
  loading.value = true;
  try {
    const [attendanceResult, leaveResult, metaResult] = await Promise.all([getAttendanceOverview(), getLeaves(), getEmployeeMeta()]);
    rawRows.value = attendanceResult.data.records || [];
    leaves.value = leaveResult.data || [];
    departmentMeta.value = metaResult.data?.departments || [];
    if (!monthFilter.value && rawRows.value.length) monthFilter.value = normalizeMonth(rawRows.value[0]);
  } finally {
    loading.value = false;
  }
};

const resetParseResult = () => {
  parseResult.total_count = 0;
  parseResult.success_count = 0;
  parseResult.error_count = 0;
  parseResult.errors = [];
};

const handleFileRemove = () => {
  fileRef.value = null;
  form.file = null;
  resetParseResult();
};

const handleFileChange = async (file) => {
  const raw = file.raw;
  if (!raw) return;
  if (!String(raw.name || '').toLowerCase().endsWith('.xlsx')) {
    ElMessage.error('仅支持 .xlsx 文件');
    return;
  }
  if ((raw.size || 0) > 20 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 20MB');
    return;
  }
  fileRef.value = raw;
  form.file = raw;
  await parseFile();
};

const parseFile = async () => {
  if (!fileRef.value || !form.month) return;
  parsing.value = true;
  resetParseResult();
  try {
    const formData = new FormData();
    formData.append('file', fileRef.value);
    formData.append('month', form.month);
    const result = await parseAttendanceFile(formData);
    const parsed = result.data.parsed || {};
    parseResult.total_count = parsed.total_count || 0;
    parseResult.success_count = parsed.success_count || 0;
    parseResult.error_count = parsed.error_count || 0;
    parseResult.errors = parsed.errors || [];
    ElMessage.success('考勤文件解析完成');
  } catch {
    ElMessage.error('考勤文件解析失败，请检查文件格式或内容');
  } finally {
    parsing.value = false;
  }
};

const confirmImport = async () => {
  await formRef.value.validate();
  if (!fileRef.value) return;
  submitting.value = true;
  try {
    const formData = new FormData();
    formData.append('file', fileRef.value);
    formData.append('month', form.month);
    await importAttendanceFile(formData);
    dialogVisible.value = false;
    fileRef.value = null;
    form.file = null;
    resetParseResult();
    monthFilter.value = form.month;
    ElMessage.success('导入成功，考勤报表已刷新');
    await loadData();
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '考勤导入失败');
  } finally {
    submitting.value = false;
  }
};

const formatToday = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
};

const buildExportRows = (rows) => rows.map((item) => ({
  工号: item.employeeNo || '',
  姓名: item.name || '',
  部门: inferDepartment(item.employeeNo, item.department),
  考勤日期: item.date || '',
  应出勤: Number(item.shouldAttendance || 0),
  实出勤: Number(item.actualAttendance || 0),
  上班打卡时间: normalizeClockValue(item.checkIn) || '',
  下班打卡时间: normalizeClockValue(item.checkOut) || '',
  考勤状态: item.status || '',
  迟到分钟: Number(item.lateMinutes || 0),
  早退分钟: Number(item.earlyMinutes || 0),
  旷工天数: Number(item.absenteeismDays || 0),
  缺卡次数: Number(item.missingCardCount || 0),
  请假类型: item.leaveType || '',
  加班小时: Number(item.overtimeHours || 0),
  备注: item.remark || '',
}));

const exportDepartmentRows = (department) => {
  const rows = filteredAttendanceRows.value.filter((item) => inferDepartment(item.employeeNo, item.department) === department);
  exportWorkbook(buildExportRows(rows), `考勤报表_${formatToday()}`, 'AttendanceReport');
};

const openDetailDialog = (department) => {
  activeDepartment.value = department;
  detailSearchKeyword.value = '';
  detailDateRange.value = [];
  detailStatusFilter.value = '';
  detailDialogVisible.value = true;
};

const downloadTemplate = () => {
  exportWorkbook([
    {
      工号: 'EMP-1001',
      姓名: '张三',
      部门: '综合管理部',
      考勤日期: `${form.month}-01`,
      应出勤: 1,
      实出勤: 1,
      上班打卡时间: '09:00',
      下班打卡时间: '18:00',
      考勤状态: '正常',
      迟到分钟: 0,
      早退分钟: 0,
      旷工天数: 0,
      缺卡次数: 0,
      请假类型: '',
      加班小时: 0,
      备注: '',
    },
  ], '考勤导入模板', 'Template');
};

const openAiSummaryReport = async () => {
  aiLoading.value = true;
  try {
    const [year, month] = String(monthFilter.value || '').split('-');
    const result = await generateAttendanceSummaryReport({
      department: departmentFilter.value || '',
      year: year || '',
      month: month || '',
      monthValue: monthFilter.value || '',
    });
    aiReport.title = 'AI考勤汇总报表';
    aiReport.content = result.data?.content || '暂无AI汇总结果';
    aiDialogVisible.value = true;
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'AI 考勤汇总报表生成失败');
  } finally {
    aiLoading.value = false;
  }
};

const copyAiReport = async () => {
  try {
    await navigator.clipboard.writeText(aiReport.content || '');
    ElMessage.success('已复制考勤汇总报表');
  } catch {
    ElMessage.error('复制失败，请手动复制');
  }
};

onMounted(loadData);
</script>

<style scoped>
.attendance-report-page {
  display: grid;
  gap: 16px;
  height: calc(100vh - 148px);
}

.report-panel {
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 16px;
  padding: 16px;
  min-height: 0;
  height: 100%;
  box-sizing: border-box;
}

.report-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.report-toolbar__left,
.report-toolbar__right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-control {
  width: 180px;
}

.month-control {
  width: 190px;
}

.search-control {
  width: 220px;
}

.action-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.report-table-wrap {
  min-height: 0;
  overflow: hidden;
}

.report-table-wrap :deep(.el-table th.el-table__cell) {
  height: 48px;
  padding: 10px 0;
}

.report-table-wrap :deep(.el-table .el-table__cell) {
  padding: 10px 0;
}

.report-table-wrap :deep(.el-table .cell) {
  line-height: 24px;
}

.report-pagination {
  display: flex;
  justify-content: flex-end;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding-top: 16px;
  background: transparent;
}

.report-pagination :deep(.el-pagination) {
  padding: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  border: none;
}

.report-pagination :deep(.el-pagination.is-background) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.report-pagination :deep(.btn-prev),
.report-pagination :deep(.btn-next),
.report-pagination :deep(.el-pager li) {
  border-radius: 8px;
}

.report-pagination :deep(.el-pager li.is-active) {
  background: #409EFF;
  color: #fff;
}

.report-pagination__total {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  color: var(--hr-info);
  font-size: 13px;
}

.detail-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.detail-search {
  width: 240px;
}

.detail-date {
  width: 320px;
}

.detail-status {
  width: 180px;
}

.import-grid {
  display: grid;
  gap: 16px;
}

.upload-card {
  background: #fff;
  border: 1px solid var(--hr-border);
  border-radius: 8px;
  padding: 16px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: var(--hr-title);
  font-size: 14px;
}

.template-link {
  color: #409EFF;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
}

.template-link:hover {
  text-decoration: underline;
}

.upload-tip {
  margin-top: 8px;
  color: var(--hr-info);
  font-size: 12px;
  line-height: 1.6;
}

.parse-panel {
  margin-top: 16px;
  padding: 18px;
}

.parse-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.parse-panel__header h4 {
  margin: 0;
  color: var(--hr-title);
}

.parse-panel__header span {
  color: var(--hr-info);
  font-size: 12px;
}

.parse-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.parse-metric {
  padding: 14px;
  border-radius: 8px;
  background: #f8fbff;
  border: 1px solid rgba(64, 158, 255, 0.12);
}

.parse-metric span {
  display: block;
  color: var(--hr-info);
  font-size: 12px;
  margin-bottom: 8px;
}

.parse-metric strong {
  color: var(--hr-title);
  font-size: 20px;
}

.download-error {
  margin-top: 16px;
  border-radius: 8px;
}

.ai-summary-btn {
  border-color: #409EFF;
  color: #409EFF;
}

.attendance-ai-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.attendance-ai-eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .16em;
  color: #7f8ea3;
  margin-bottom: 6px;
}

.attendance-ai-header h3 {
  margin: 0;
  color: var(--hr-title);
  font-size: 24px;
  font-weight: 800;
}

.attendance-ai-copy {
  border-radius: 10px;
}

.attendance-ai-body {
  max-height: min(720px, calc(100vh - 160px));
  overflow-y: auto;
  padding: 20px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
  border: 1px solid #dce9ff;
}

.attendance-ai-report-shell {
  display: grid;
  gap: 16px;
}

.attendance-ai-hero {
  padding: 24px;
  border-radius: 18px;
  background: radial-gradient(circle at top left, rgba(64, 158, 255, 0.18), transparent 35%), linear-gradient(145deg, #ffffff 0%, #f4f8ff 100%);
  border: 1px solid #d8e6ff;
  box-shadow: 0 16px 32px rgba(70, 110, 180, 0.12);
}

.attendance-ai-hero__label {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .16em;
  color: #7d8da5;
  margin-bottom: 12px;
}

.attendance-ai-hero__text {
  font-size: 17px;
  line-height: 1.9;
  color: #24364b;
  font-weight: 600;
}

.attendance-ai-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.attendance-ai-card {
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
  border: 1px solid #dce7f7;
  box-shadow: 0 14px 28px rgba(31, 45, 61, 0.08);
}

.attendance-ai-card__title {
  font-size: 18px;
  font-weight: 800;
  color: #21324a;
  margin-bottom: 14px;
}

.attendance-ai-points {
  display: grid;
  gap: 12px;
}

.attendance-ai-point {
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%);
  border: 1px solid #dbe8ff;
  color: #445066;
  line-height: 1.8;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.7);
}

.attendance-ai-original {
  padding: 18px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid #dce7f7;
  box-shadow: 0 12px 24px rgba(31, 45, 61, 0.06);
}

.attendance-ai-original__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.attendance-ai-original__eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .16em;
  color: #7f8ea3;
  margin-bottom: 6px;
}

.attendance-ai-original h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #21324a;
}

.attendance-ai-copy--inline {
  flex-shrink: 0;
}

.attendance-ai-content {
  white-space: pre-wrap;
  line-height: 1.95;
  color: #2f3b52;
  font-size: 15px;
  padding: 16px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fbff 0%, #f3f7ff 100%);
  border: 1px solid #dbe8ff;
}

@media (max-width: 767px) {
  .attendance-report-page,
  .report-panel {
    min-height: auto;
    height: auto;
  }

  .report-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .report-toolbar__left,
  .report-toolbar__right,
  .detail-toolbar {
    width: 100%;
  }

  .filter-control,
  .month-control,
  .search-control,
  .detail-search,
  .detail-date,
  .detail-status {
    width: 100%;
  }

  .report-toolbar__right {
    justify-content: flex-end;
  }

  .attendance-ai-header,
  .attendance-ai-original__head {
    flex-direction: column;
    align-items: stretch;
  }

  .attendance-ai-grid {
    grid-template-columns: 1fr;
  }

  .attendance-ai-body {
    padding: 14px;
  }

  .attendance-ai-hero,
  .attendance-ai-card,
  .attendance-ai-original {
    padding: 14px;
  }

  .parse-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
