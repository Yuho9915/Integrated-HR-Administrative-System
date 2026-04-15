import { createSupplement, getSupplements } from '@/api/modules';

export const listSupplementApplications = async (employeeNo = '') => {
  const result = await getSupplements();
  const items = result.data || [];
  return items
    .filter((item) => !employeeNo || item.employee_no === employeeNo || item.employeeNo === employeeNo)
    .sort((a, b) => String(b.created_at || b.createdAt || '').localeCompare(String(a.created_at || a.createdAt || '')));
};

export const countMonthlySupplementApplications = async (employeeNo, month) => {
  const items = await listSupplementApplications(employeeNo);
  return items.filter((item) => String(item.date || '').slice(0, 7) === month).length;
};

export const findSupplementApplicationByDate = async (employeeNo, date) => {
  const items = await listSupplementApplications(employeeNo);
  return items.find((item) => item.date === date) || null;
};

export const findSupplementApplicationById = async (id) => {
  const result = await getSupplements();
  return (result.data || []).find((item) => item.id === id) || null;
};

export const createSupplementApplication = async ({ employeeNo, date, time, reason }) => {
  const result = await createSupplement({ employee_no: employeeNo, date, time, reason });
  return result.data?.supplement || null;
};

export const toApplicationRow = (item) => ({
  id: item.id,
  leave_type: item.leave_type || item.type || '补卡申请',
  start_at: item.start_at || `${item.date} ${item.time}`,
  end_at: item.end_at || `${item.date} ${item.time}`,
  days: item.days || 0,
  reason: item.reason,
  status: item.status,
  approver: item.approver,
  employeeNo: item.employee_no || item.employeeNo,
  kind: 'supplement',
  raw: item,
});
