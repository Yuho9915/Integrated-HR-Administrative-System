<template>
  <div class="page-grid manager-dashboard">
    <section class="hero-grid">
      <article v-for="item in cards" :key="item.key" class="hero-card" @click="go(item.path)">
        <div class="hero-card__label">{{ item.label }}</div>
        <div class="hero-card__value">{{ item.value }}</div>
        <div class="hero-card__meta">{{ item.meta }}</div>
      </article>
    </section>

    <section class="content-grid">
      <PageCard title="今日待办" description="当前本部门最值得优先处理的事项。">
        <div class="focus-list">
          <button v-for="item in todos" :key="item.label" type="button" class="focus-item" @click="go(item.path)">
            <div>
              <strong>{{ item.label }}</strong>
              <p>{{ item.desc }}</p>
            </div>
            <span>{{ item.count }}</span>
          </button>
          <el-empty v-if="!todos.length" description="暂无待办事项" />
        </div>
      </PageCard>

      <PageCard title="部门概况" description="仅统计当前经理所属部门。">
        <div class="summary-grid">
          <div class="summary-card">
            <span>所属部门</span>
            <strong>{{ departmentName }}</strong>
          </div>
          <div class="summary-card">
            <span>在职人数</span>
            <strong>{{ activeEmployees }}</strong>
          </div>
          <div class="summary-card">
            <span>待经理审核绩效</span>
            <strong>{{ pendingPerformance }}</strong>
          </div>
          <div class="summary-card">
            <span>本月请假人数</span>
            <strong>{{ leaveEmployees }}</strong>
          </div>
        </div>
      </PageCard>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import PageCard from '@/components/PageCard.vue';
import { getApprovalOverview, getAttendanceOverview, getEmployees, getLeaves, getPerformanceList } from '@/api/modules';
import { useAppStore } from '@/stores/app';

const router = useRouter();
const appStore = useAppStore();
const { user } = storeToRefs(appStore);
const employees = ref([]);
const attendanceRows = ref([]);
const leaves = ref([]);
const approvals = ref([]);
const performanceRows = ref([]);

const departmentName = computed(() => user.value?.department || '未分配部门');
const inferDepartment = (item = {}) => {
  if (item.department) return item.department;
  const employeeNo = String(item.employeeNo || item.employee_no || '');
  if (employeeNo.startsWith('HR')) return '综合管理部';
  if (employeeNo.startsWith('OPS')) return '运营中心';
  if (employeeNo.startsWith('DEV')) return '产品技术部';
  if (employeeNo.startsWith('MKT')) return '市场部';
  if (employeeNo.startsWith('SAL')) return '销售部';
  if (employeeNo.startsWith('FIN')) return '财务部';
  return '未分组';
};
const departmentEmployees = computed(() => employees.value.filter((item) => item.department === departmentName.value));
const activeEmployees = computed(() => departmentEmployees.value.filter((item) => item.status !== '离职').length);
const attendanceAbnormal = computed(() => attendanceRows.value.filter((item) => inferDepartment(item) === departmentName.value && item.status !== '正常').length);
const pendingApprovals = computed(() => approvals.value.filter((item) => item.level === 'manager' && item.status === '待审批' && item.applicant_department === departmentName.value).length);
const pendingPerformance = computed(() => performanceRows.value.filter((item) => item.department === departmentName.value && ['待经理审核', '经理退回修改', 'HR退回修改'].includes(item.status)).length);
const leaveEmployees = computed(() => new Set(leaves.value.filter((item) => item.department === departmentName.value).map((item) => item.employee_no || item.employeeNo)).size);

const cards = computed(() => [
  { key: 'employees', label: '本部门员工', value: `${activeEmployees.value} 人`, meta: '查看人员结构与状态', path: '/manager/employees' },
  { key: 'attendance', label: '考勤异常', value: `${attendanceAbnormal.value} 条`, meta: '本月出勤异常记录', path: '/manager/attendance' },
  { key: 'approvals', label: '待审批', value: `${pendingApprovals.value} 条`, meta: '需经理处理的审批', path: '/manager/approvals' },
  { key: 'performance', label: '待评分绩效', value: `${pendingPerformance.value} 条`, meta: '需经理审核评分', path: '/manager/performance-entry' },
]);

const todos = computed(() => [
  { label: '处理本部门审批', count: pendingApprovals.value, desc: '请及时通过或驳回当前待办申请。', path: '/manager/approvals' },
  { label: '完成绩效评分', count: pendingPerformance.value, desc: '推进本部门月度绩效审核。', path: '/manager/performance-entry' },
  { label: '跟进考勤异常', count: attendanceAbnormal.value, desc: '关注迟到、早退、请假和缺卡。', path: '/manager/attendance' },
].filter((item) => item.count > 0));

const go = (path) => router.push(path);

onMounted(async () => {
  const [employeeResult, leaveResult, approvalResult, performanceResult] = await Promise.all([
    getEmployees(),
    getLeaves(),
    getApprovalOverview(),
    getPerformanceList({ page: 1, pageSize: 200 }),
  ]);
  employees.value = employeeResult.data || [];
  leaves.value = leaveResult.data || [];
  approvals.value = approvalResult.data?.records || [];
  performanceRows.value = performanceResult.data?.records || [];

  try {
    const attendanceResult = await getAttendanceOverview({ suppressErrorMessage: true });
    attendanceRows.value = attendanceResult.data?.records || [];
  } catch {
    attendanceRows.value = [];
  }
});
</script>

<style scoped>
.manager-dashboard{display:grid;gap:16px}.hero-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.hero-card{display:grid;gap:8px;padding:18px;border-radius:20px;background:linear-gradient(180deg,#fff 0%,#f6f9ff 100%);border:1px solid rgba(120,146,190,.16);box-shadow:0 14px 32px rgba(31,42,68,.06);cursor:pointer}.hero-card__label{font-size:13px;color:#667892;font-weight:700}.hero-card__value{font-size:30px;color:#20324a;font-weight:900}.hero-card__meta{font-size:12px;color:#8a98ab}.content-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:16px}.focus-list{display:grid;gap:12px}.focus-item{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px;border:none;border-radius:16px;background:linear-gradient(180deg,#f7fbff 0%,#eef5ff 100%);text-align:left;cursor:pointer}.focus-item strong{color:#22324a}.focus-item p{margin:6px 0 0;color:#72829a;font-size:12px;line-height:1.7}.focus-item span{font-size:24px;font-weight:900;color:#409EFF}.summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.summary-card{display:grid;gap:8px;padding:16px;border-radius:16px;background:#f8fbff;border:1px solid #e0ebfa}.summary-card span{font-size:12px;color:#7f8da3}.summary-card strong{font-size:24px;color:#20324a}@media (max-width:900px){.hero-grid,.content-grid,.summary-grid{grid-template-columns:1fr}}
</style>
