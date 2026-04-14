export const ROLE_MAP = {
  employee: '员工',
  manager: '部门经理',
  hr: '人事行政',
  boss: '老板',
};

export const ROLE_OPTIONS = Object.entries(ROLE_MAP).map(([value, label]) => ({
  value,
  label,
}));

export const ROLE_HOME = {
  employee: '/employee/profile',
  manager: '/manager/performance-entry',
  hr: '/hr/dashboard',
  boss: '/boss/overview',
};
