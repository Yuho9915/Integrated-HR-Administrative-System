import { createRouter, createWebHistory } from 'vue-router';

import MainLayout from '@/layout/MainLayout.vue';
import LoginView from '@/views/LoginView.vue';

import EmployeeProfileView from '@/views/employee/EmployeeProfileView.vue';
import EmployeeArchiveView from '@/views/employee/EmployeeArchiveView.vue';
import EmployeeAttendanceView from '@/views/employee/EmployeeAttendanceView.vue';
import EmployeePayrollView from '@/views/employee/EmployeePayrollView.vue';
import EmployeePerformanceView from '@/views/employee/EmployeePerformanceView.vue';
import EmployeeApplicationsView from '@/views/employee/EmployeeApplicationsView.vue';
import EmployeeAssistantView from '@/views/employee/EmployeeAssistantView.vue';

import ManagerPerformanceEntryView from '@/views/manager/ManagerPerformanceEntryView.vue';
import ManagerPerformanceCheckView from '@/views/manager/ManagerPerformanceCheckView.vue';
import ManagerApprovalsView from '@/views/manager/ManagerApprovalsView.vue';

import HRDashboardView from '@/views/hr/HRDashboardView.vue';
import HREmployeesView from '@/views/hr/HREmployeesView.vue';
import HRAttendanceReportView from '@/views/hr/HRAttendanceReportView.vue';
import HRPerformanceView from '@/views/hr/HRPerformanceView.vue';
import HRPayrollView from '@/views/hr/HRPayrollView.vue';
import HRApprovalsView from '@/views/hr/HRApprovalsView.vue';
import HRAdministrationView from '@/views/hr/HRAdministrationView.vue';

import BossOverviewView from '@/views/boss/BossOverviewView.vue';
import BossReportsView from '@/views/boss/BossReportsView.vue';
import BossCostsView from '@/views/boss/BossCostsView.vue';

import { ROLE_HOME } from '@/constants/roles';
import { useAppStore } from '@/stores/app';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true, title: '登录系统', description: '支持员工、部门经理、人事行政、老板四类角色登录。' },
  },
  {
    path: '/',
    redirect: () => {
      const store = useAppStore();
      return store.homePath;
    },
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: 'employee/profile', component: EmployeeProfileView, meta: { role: 'employee', title: '个人中心', description: '员工查看待办、通知与个人工作台信息。' } },
      { path: 'employee/archive', component: EmployeeArchiveView, meta: { role: 'employee', title: '个人档案', description: '查看员工基础身份、任职信息与档案材料状态。' } },
      { path: 'employee/attendance', component: EmployeeAttendanceView, meta: { role: 'employee', title: '考勤查询', description: '查询月度出勤、迟到早退与请假记录。' } },
      { path: 'employee/payroll', component: EmployeePayrollView, meta: { role: 'employee', title: '工资查询', description: '查看工资条、发放状态与导出。' } },
      { path: 'employee/performance', component: EmployeePerformanceView, meta: { role: 'employee', title: '绩效查询', description: '查看绩效成绩、等级与历史趋势。' } },
      { path: 'employee/applications', component: EmployeeApplicationsView, meta: { role: 'employee', title: '申请中心', description: '提交请假、加班、领用、报修等申请。' } },
      { path: 'employee/assistant', component: EmployeeAssistantView, meta: { role: 'employee', title: 'AI问答机器人', description: '7×24 小时智能问答与制度咨询。' } },

      { path: 'manager/performance-entry', component: ManagerPerformanceEntryView, meta: { role: 'manager', title: '部门绩效录入', description: '批量录入部门绩效等级与分数。' } },
      { path: 'manager/performance-check', component: ManagerPerformanceCheckView, meta: { role: 'manager', title: '绩效校验', description: '提交 AI 校验等级分布与异常情况。' } },
      { path: 'manager/approvals', component: ManagerApprovalsView, meta: { role: 'manager', title: '本部门审批', description: '审批请假、加班、绩效异议等事项。' } },

      { path: 'hr/dashboard', component: HRDashboardView, meta: { role: 'hr', title: 'HR首页', description: '查看人事行政六大模块的一屏总览看板。' } },
      { path: 'hr/employees', component: HREmployeesView, meta: { role: 'hr', title: '员工管理', description: '维护员工档案、组织架构、合同与状态。' } },
      { path: 'hr/attendance-report', component: HRAttendanceReportView, meta: { role: 'hr', title: '考勤报表', description: '汇总出勤率、异常率、请假时长与导出。' } },
      { path: 'hr/payroll', component: HRPayrollView, meta: { role: 'hr', title: '薪酬核算', description: 'AI 汇总工资、扣款、补贴并导出。' } },
      { path: 'hr/performance', component: HRPerformanceView, meta: { role: 'hr', title: '绩效管理', description: '查看部门绩效分布、异议申请与统计。' } },
      { path: 'hr/approvals', component: HRApprovalsView, meta: { role: 'hr', title: '审批中心', description: '统一管理人事、行政、资产、综合审批。' } },
      { path: 'hr/administration', component: HRAdministrationView, meta: { role: 'hr', title: '行政/资产管理', description: '管理物品库存、资产、用车、会议室和报修。' } },

      { path: 'boss/overview', component: BossOverviewView, meta: { role: 'boss', title: '数据总览', description: '查看公司级经营、人力与考勤概览。' } },
      { path: 'boss/reports', component: BossReportsView, meta: { role: 'boss', title: '图表报表', description: '查看部门趋势、结构统计与报表导出。' } },
      { path: 'boss/costs', component: BossCostsView, meta: { role: 'boss', title: '人力成本总览', description: '查看人力成本趋势、预算执行和成本结构。' } },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () => {
      const store = useAppStore();
      return store.isAuthenticated ? store.homePath : '/login';
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  const store = useAppStore();
  document.title = `${to.meta.title || '首页'} - 人事行政一体化HR系统`;

  if (to.meta.public) {
    next();
    return;
  }

  if (!store.isAuthenticated) {
    next('/login');
    return;
  }

  if (!store.user) {
    try {
      await store.hydrateUser();
    } catch {
      store.logout();
      next('/login');
      return;
    }
  }

  if (to.meta.role && to.meta.role !== store.user?.role) {
    next(ROLE_HOME[store.user?.role] || '/login');
    return;
  }

  next();
});

export default router;
