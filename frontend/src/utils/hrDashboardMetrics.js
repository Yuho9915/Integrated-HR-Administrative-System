export const DASHBOARD_DATE = '2026-04-14';
export const DASHBOARD_MONTH = DASHBOARD_DATE.slice(0, 7);

export const countText = (value, unit = '项') => `${value}${unit}`;
export const normalizeMonth = (value) => String(value || '').slice(0, 7);

export const inferDepartment = (employeeNo = '', department = '') => {
  if (department) return department;
  if (String(employeeNo).startsWith('HR')) return '综合管理部';
  if (String(employeeNo).startsWith('OPS')) return '运营中心';
  if (String(employeeNo).startsWith('DEV')) return '产品技术部';
  if (String(employeeNo).startsWith('MKT')) return '市场部';
  if (String(employeeNo).startsWith('SAL')) return '销售部';
  if (String(employeeNo).startsWith('FIN')) return '财务部';
  return '未分组';
};

export const normalizeEmployee = (item) => ({
  ...item,
  status: item.status || '在职',
  phone: item.phone || '',
  email: item.email || '',
  id_card_no: item.id_card_no || item.idCardNo || '',
  contractEndDate: item.contract_end_date || item.contractEndDate || '',
});

export const normalizeAdministration = (item) => {
  const details = Array.isArray(item.details) ? item.details : [];
  const total = Number(item.total || item.totalQuantity || details.length || 0);
  const used = details.filter((row) => ['使用中', '借出中', '待维修'].includes(row.status)).length;
  const remain = Math.max(total - used, 0);
  const safe = Number(item.safe || item.safeStock || Math.max(1, Math.ceil(total * 0.2)));
  return {
    ...item,
    total,
    details,
    remain,
    stock: remain > safe ? '充足' : '低库存',
  };
};

export const buildEmployeeMetrics = (employeeRows, dashboardDate = DASHBOARD_DATE) => {
  const now = new Date(dashboardDate);
  const headcount = employeeRows.filter((item) => item.status !== '离职').length;
  const onboardingCount = employeeRows.filter((item) => item.status === '试用').length;
  const leavingCount = employeeRows.filter((item) => item.status === '离职').length;
  const profileRiskCount = employeeRows.filter((item) => !item.phone || !item.email || !item.id_card_no).length;
  const contractExpiringCount = employeeRows.filter((item) => {
    if (!item.contractEndDate) return false;
    const end = new Date(item.contractEndDate);
    const diff = end.getTime() - now.getTime();
    return diff >= 0 && diff <= 30 * 24 * 60 * 60 * 1000;
  }).length;

  return {
    headcount,
    onboardingCount,
    leavingCount,
    profileRiskCount,
    contractExpiringCount,
  };
};

export const buildAttendanceMetrics = (attendanceRows, leaveRows, dashboardMonth = DASHBOARD_MONTH) => {
  const attendanceRowsOfMonth = attendanceRows.filter((item) => normalizeMonth(item.month || item.date) === dashboardMonth);
  const leaveRowsOfMonth = leaveRows.filter((item) => normalizeMonth(item.start_at || item.period) === dashboardMonth);
  const attendanceAbnormal = attendanceRowsOfMonth.reduce((sum, item) => sum + Number(item.abnormalCount || 0), 0);
  const attendanceRateValue = attendanceRowsOfMonth.length
    ? Math.round(attendanceRowsOfMonth.reduce((sum, item) => sum + Number(String(item.attendanceRate || '0').replace('%', '') || 0), 0) / attendanceRowsOfMonth.length)
    : 0;
  const leaveHours = leaveRowsOfMonth.reduce((sum, item) => sum + Number(item.days || 0) * 8, 0);
  const lateTimes = attendanceRowsOfMonth.reduce((sum, item) => sum + Number(item.lateTimes || 0), 0);

  return {
    attendanceRowsOfMonth,
    leaveRowsOfMonth,
    attendanceAbnormal,
    attendanceRate: `${attendanceRateValue}%`,
    leaveHours,
    lateTimes,
  };
};

export const buildApprovalMetrics = (approvalRows, dashboardDate = DASHBOARD_DATE) => ({
  pendingApprovals: approvalRows.filter((item) => item.status === '待审批').length,
  todayApprovals: approvalRows.filter((item) => String(item.apply_time || '').slice(0, 10) === dashboardDate).length,
  rejectedApprovals: approvalRows.filter((item) => item.status === '已驳回').length,
});

export const buildPerformanceMetrics = (performanceRows) => ({
  pendingPerformance: performanceRows.filter((item) => ['待自评', '待复评', '待审核'].includes(item.status)).length,
  finishedPerformance: performanceRows.filter((item) => item.status === '已完成').length,
  lowPerformance: performanceRows.filter((item) => ['C', 'D'].includes(item.grade)).length,
});

export const buildPayrollMetrics = (payrollRows, dashboardMonth = DASHBOARD_MONTH) => {
  const payrollRowsOfMonth = payrollRows.filter((item) => String(item.month || '') === dashboardMonth);
  return {
    payrollRowsOfMonth,
    payrollAbnormal: payrollRowsOfMonth.filter((item) => Number(item.actual || 0) < 0 || Number(item.actual || 0) < 5000).length,
    payrollDone: payrollRowsOfMonth.length,
    payrollMonth: payrollRowsOfMonth[0]?.month || dashboardMonth,
    payrollActual: payrollRowsOfMonth.reduce((sum, item) => sum + Number(item.actual || 0), 0).toFixed(2),
  };
};

export const buildAdministrationMetrics = (administrationRows, dashboardMonth = DASHBOARD_MONTH) => ({
  administrationLow: administrationRows.filter((item) => item.stock === '低库存').length,
  administrationRepair: administrationRows.flatMap((item) => item.details || []).filter((item) => item.status === '待维修').length,
  administrationIssue: administrationRows.flatMap((item) => item.details || []).filter((item) => normalizeMonth(item.receive) === dashboardMonth && ['使用中', '借出中', '待维修'].includes(item.status)).length,
  assetKinds: administrationRows.length,
  assetStock: administrationRows.reduce((sum, item) => sum + Number(item.total || 0), 0),
});
