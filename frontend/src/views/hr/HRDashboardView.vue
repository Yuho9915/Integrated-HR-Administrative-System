<template>
  <div class="page-grid hr-dashboard">
    <section class="hero-grid">
      <article v-for="item in summaryCards" :key="item.key" class="hero-card" @click="go(item.path)">
        <div class="hero-card__top">
          <div class="hero-card__head">
            <span>{{ item.label }}</span>
            <small>{{ item.tip }}</small>
          </div>
          <div class="hero-card__icon">
            <el-icon><component :is="iconRegistry[item.icon]" /></el-icon>
          </div>
        </div>
        <div class="hero-card__value">{{ item.value }}</div>
        <div class="hero-card__foot">{{ item.desc }}</div>
      </article>
    </section>

    <section v-if="visibleTodoItems.length || visibleRiskItems.length" class="focus-grid" :class="{ 'focus-grid--single': !(visibleTodoItems.length && visibleRiskItems.length) }">
      <PageCard v-if="visibleTodoItems.length" title="今日待办" description="当前最值得优先处理的工作。" class="page-section focus-card">
        <div class="focus-list">
          <button v-for="item in visibleTodoItems" :key="item.label" class="focus-item" type="button" @click="go(item.path)">
            <div class="focus-item__main">
              <strong>{{ item.label }}</strong>
              <p>{{ item.desc }}</p>
            </div>
            <span class="focus-item__value"><em>{{ item.count }}</em><i>{{ item.unit }}</i></span>
          </button>
        </div>
      </PageCard>

      <PageCard v-if="visibleRiskItems.length" title="风险提醒" description="仅展示当前存在风险的事项。" class="page-section focus-card">
        <div class="focus-list">
          <button v-for="item in visibleRiskItems" :key="item.label" class="focus-item focus-item--risk" type="button" @click="go(item.path)">
            <div class="focus-item__main">
              <strong>{{ item.label }}</strong>
              <p>{{ item.desc }}</p>
            </div>
            <span class="focus-item__value"><em>{{ item.count }}</em><i>{{ item.unit }}</i></span>
          </button>
        </div>
      </PageCard>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import PageCard from '@/components/PageCard.vue';
import { iconRegistry } from '@/constants/menus';
import {
  getAdministrationSummary,
  getApprovalOverview,
  getAttendanceOverview,
  getEmployees,
  getLeaves,
  getPayrollSummary,
  getPerformanceList,
} from '@/api/modules';
import { applyApprovedAssetSyncs } from '@/utils/assetApprovalSync';
import {
  DASHBOARD_DATE,
  DASHBOARD_MONTH,
  buildAdministrationMetrics,
  buildApprovalMetrics,
  buildAttendanceMetrics,
  buildEmployeeMetrics,
  buildPayrollMetrics,
  buildPerformanceMetrics,
  countText,
  normalizeAdministration,
  normalizeEmployee,
} from '@/utils/hrDashboardMetrics';

const router = useRouter();
const employeeRows = ref([]);
const attendanceRows = ref([]);
const leaveRows = ref([]);
const approvalRows = ref([]);
const payrollRows = ref([]);
const performanceRows = ref([]);
const administrationRows = ref([]);

const go = (path) => router.push(path);

const employeeMetrics = computed(() => buildEmployeeMetrics(employeeRows.value, DASHBOARD_DATE));
const headcount = computed(() => employeeMetrics.value.headcount);
const onboardingCount = computed(() => employeeMetrics.value.onboardingCount);
const leavingCount = computed(() => employeeMetrics.value.leavingCount);
const profileRiskCount = computed(() => employeeMetrics.value.profileRiskCount);
const contractExpiringCount = computed(() => employeeMetrics.value.contractExpiringCount);

const attendanceMetrics = computed(() => buildAttendanceMetrics(attendanceRows.value, leaveRows.value, DASHBOARD_MONTH));
const attendanceAbnormal = computed(() => attendanceMetrics.value.attendanceAbnormal);
const attendanceRate = computed(() => attendanceMetrics.value.attendanceRate);
const leaveHours = computed(() => attendanceMetrics.value.leaveHours);
const lateTimes = computed(() => attendanceMetrics.value.lateTimes);

const approvalMetrics = computed(() => buildApprovalMetrics(approvalRows.value, DASHBOARD_DATE));
const pendingApprovals = computed(() => approvalMetrics.value.pendingApprovals);
const todayApprovals = computed(() => approvalMetrics.value.todayApprovals);
const rejectedApprovals = computed(() => approvalMetrics.value.rejectedApprovals);

const performanceMetrics = computed(() => buildPerformanceMetrics(performanceRows.value));
const pendingPerformance = computed(() => performanceMetrics.value.pendingPerformance);
const finishedPerformance = computed(() => performanceMetrics.value.finishedPerformance);
const lowPerformance = computed(() => performanceMetrics.value.lowPerformance);

const payrollMetrics = computed(() => buildPayrollMetrics(payrollRows.value, DASHBOARD_MONTH));
const payrollAbnormal = computed(() => payrollMetrics.value.payrollAbnormal);
const payrollDone = computed(() => payrollMetrics.value.payrollDone);
const payrollMonth = computed(() => payrollMetrics.value.payrollMonth);
const payrollActual = computed(() => payrollMetrics.value.payrollActual);

const administrationMetrics = computed(() => buildAdministrationMetrics(administrationRows.value, DASHBOARD_MONTH));
const administrationLow = computed(() => administrationMetrics.value.administrationLow);
const administrationRepair = computed(() => administrationMetrics.value.administrationRepair);
const administrationIssue = computed(() => administrationMetrics.value.administrationIssue);
const assetKinds = computed(() => administrationMetrics.value.assetKinds);
const assetStock = computed(() => administrationMetrics.value.assetStock);

const summaryCards = computed(() => [
  { key: 'employees', icon: 'Postcard', label: '在职员工', value: countText(headcount.value, '人'), tip: `试用 ${onboardingCount.value} / 离职 ${leavingCount.value}`, desc: '来自员工管理档案与组织状态。', path: '/hr/employees' },
  { key: 'attendance', icon: 'Histogram', label: '今日考勤', value: attendanceRate.value, tip: `异常 ${attendanceAbnormal.value} 人`, desc: `迟到 ${lateTimes.value} 次，请假 ${leaveHours.value} 小时。`, path: '/hr/attendance-report' },
  { key: 'approvals', icon: 'Checked', label: '待审批', value: countText(pendingApprovals.value, '条'), tip: `今日新增 ${todayApprovals.value}`, desc: '对齐审批中心当前待处理记录。', path: '/hr/approvals' },
  { key: 'performance', icon: 'TrendCharts', label: '绩效进度', value: countText(pendingPerformance.value, '项'), tip: `已完成 ${finishedPerformance.value}`, desc: '聚焦待自评、待复评、待审核流程。', path: '/hr/performance' },
  { key: 'payroll', icon: 'Money', label: '薪酬状态', value: countText(payrollDone.value, '条'), tip: `异常 ${payrollAbnormal.value} 条`, desc: `当前实发合计 ¥${payrollActual.value}`, path: '/hr/payroll' },
  { key: 'assets', icon: 'OfficeBuilding', label: '资产预警', value: countText(administrationLow.value, '类'), tip: `待维修 ${administrationRepair.value}`, desc: `品类 ${assetKinds.value} / 库存 ${assetStock.value}`, path: '/hr/administration' },
]);

const visibleTodoItems = computed(() => [
  { label: '待审批事项', count: pendingApprovals.value, unit: '条', desc: '优先处理当前审批中心待办。', path: '/hr/approvals' },
  { label: '考勤异常', count: attendanceAbnormal.value, unit: '人', desc: '跟进异常出勤、缺卡和迟到记录。', path: '/hr/attendance-report' },
  { label: '待处理绩效', count: pendingPerformance.value, unit: '项', desc: '推进待自评、待复评、待审核流程。', path: '/hr/performance' },
  { label: '资产低库存', count: administrationLow.value, unit: '类', desc: '及时采购补货，避免行政物料短缺。', path: '/hr/administration' },
  { label: '资料待完善', count: profileRiskCount.value, unit: '人', desc: '补齐员工手机号、邮箱和身份证信息。', path: '/hr/employees' },
].filter((item) => item.count > 0));

const visibleRiskItems = computed(() => [
  { label: '合同即将到期', count: contractExpiringCount.value, unit: '人', desc: '30 天内到期合同需要续签跟进。', path: '/hr/employees' },
  { label: '审批驳回记录', count: rejectedApprovals.value, unit: '条', desc: '关注已驳回申请是否重新提交。', path: '/hr/approvals' },
  { label: '低绩效提醒', count: lowPerformance.value, unit: '人', desc: '重点关注 C / D 档绩效结果。', path: '/hr/performance' },
  { label: '薪酬异常', count: payrollAbnormal.value, unit: '条', desc: '实发工资低于阈值，需人工复核。', path: '/hr/payroll' },
  { label: '资产维修中', count: administrationRepair.value, unit: '件', desc: '维修资产需持续跟进处理进度。', path: '/hr/administration' },
].filter((item) => item.count > 0));

const totalActionCount = computed(() => visibleTodoItems.value.reduce((sum, item) => sum + item.count, 0) + visibleRiskItems.value.reduce((sum, item) => sum + item.count, 0));

onMounted(async () => {
  const [employees, attendance, leaves, approvals, payroll, performance, administration] = await Promise.all([
    getEmployees(),
    getAttendanceOverview(),
    getLeaves(),
    getApprovalOverview(),
    getPayrollSummary(),
    getPerformanceList({ page: 1, pageSize: 200 }),
    getAdministrationSummary(),
  ]);

  employeeRows.value = (employees.data || []).map(normalizeEmployee);
  attendanceRows.value = attendance.data.records || [];
  leaveRows.value = leaves.data || [];
  approvalRows.value = approvals.data.records || [];
  payrollRows.value = payroll.data.records || [];
  performanceRows.value = performance.data.records || [];
  administrationRows.value = applyApprovedAssetSyncs(administration.data.records || []).map(normalizeAdministration);
});
</script>

<style scoped>
.hr-dashboard{display:grid;gap:16px;align-content:start;align-items:start}.hero-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:18px;align-items:start}.hero-card{display:flex;flex-direction:column;justify-content:flex-start;align-self:start;gap:8px;min-height:0;padding:18px 14px;border:none;border-radius:18px;background:linear-gradient(180deg,#ffffff 0%,#f6f9ff 58%,#f1f6ff 100%);box-shadow:0 18px 40px rgba(26,55,110,.08);cursor:pointer;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;text-align:left;position:relative;overflow:hidden}.hero-card::after{content:'';position:absolute;inset:0;border-radius:inherit;border:1px solid rgba(128,160,220,.16);pointer-events:none}.hero-card:hover,.focus-item:hover{transform:translateY(-2px);box-shadow:0 20px 46px rgba(26,55,110,.12)}.hero-card__top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}.hero-card__head{display:grid;gap:4px}.hero-card__head span{color:#4f6485;font-size:12px;font-weight:800;letter-spacing:.02em}.hero-card__head small{color:#94a3b8;font-size:11px;line-height:1.25}.hero-card__icon{width:34px;height:34px;display:grid;place-items:center;border-radius:12px;background:linear-gradient(135deg,#409eff,#83beff);color:#fff;box-shadow:0 10px 24px rgba(64,158,255,.22);flex-shrink:0}.hero-card__icon :deep(.el-icon){font-size:16px}.hero-card__value{display:flex;align-items:flex-end;color:#14233d;font-size:24px;font-weight:800;line-height:1.02;letter-spacing:-.02em}.hero-card__foot{color:#6d809c;font-size:11px;line-height:1.35}.focus-grid{display:grid;grid-template-columns:1.15fr .95fr;gap:18px;align-items:start}.focus-grid--single{grid-template-columns:1fr}.focus-card{overflow:hidden;align-self:start}.focus-card :deep(.page-card){border-radius:24px;box-shadow:0 16px 34px rgba(28,48,84,.06)}.focus-card :deep(.page-card__header){padding:20px 22px;border-bottom:1px solid #edf2fb;background:linear-gradient(180deg,#ffffff 0%,#f9fbff 100%)}.focus-card :deep(.section-title){font-size:18px}.focus-card :deep(.section-description){line-height:1.7}.focus-card :deep(.page-card__body){padding:18px 22px}.focus-list{display:grid;gap:12px}.focus-item{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 18px;border:none;border-radius:18px;background:linear-gradient(180deg,#f7fbff 0%,#eef5ff 100%);cursor:pointer;transition:transform .18s ease,box-shadow .18s ease;text-align:left;box-shadow:inset 0 0 0 1px rgba(111,161,235,.08)}.focus-item__main{display:grid;gap:6px}.focus-item strong{color:#23314d;font-size:15px}.focus-item p{margin:0;color:#71839f;font-size:12px;line-height:1.7}.focus-item__value{display:inline-flex;align-items:baseline;gap:2px;color:#2e7df6;font-weight:800;line-height:1}.focus-item__value em{font-style:normal;font-size:24px}.focus-item__value i{font-style:normal;font-size:15px}.focus-item--risk{background:linear-gradient(180deg,#fffaf6 0%,#fff2e6 100%);box-shadow:inset 0 0 0 1px rgba(230,126,34,.10)}.focus-item--risk .focus-item__value{color:#e67e22}@media (max-width:1400px){.hero-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media (max-width:980px){.focus-grid{grid-template-columns:1fr;display:grid}}@media (max-width:767px){.hr-dashboard{gap:16px}.hero-grid,.focus-grid{grid-template-columns:1fr;gap:16px}.hero-card{min-height:0;padding:18px 14px}.hero-card__value{font-size:24px}}
</style>
