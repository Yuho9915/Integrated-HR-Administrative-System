import request from './request';

export const loginApi = (payload) => request.post('/auth/login', payload);
export const refreshTokenApi = (payload) => request.post('/auth/refresh', payload);
export const logoutApi = (payload) => request.post('/auth/logout', payload);
export const getCurrentUser = () => request.get('/auth/me');

export const getDashboardSummary = () => request.get('/dashboard/summary');
export const getAttendanceOverview = () => request.get('/attendance/overview');
export const generateAttendanceSummaryReport = (payload) => request.post('/attendance/ai/generate-summary-report', payload);
export const parseAttendanceFile = (formData) => request.post('/attendance/import/parse', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});
export const importAttendanceFile = (formData) => request.post('/attendance/import', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

export const getLeaves = () => request.get('/leaves');
export const createLeave = (payload) => request.post('/leaves', payload);

export const getAssistantHealth = () => request.get('/ai/health');
export const askAssistant = (payload) => request.post('/ai/chat', payload);
export const parseResume = (payload) => request.post('/ai/resume/parse', payload);
export const parseIdCard = (payload) => request.post('/ai/id-card/parse', payload);

export const getEmployees = () => request.get('/employees');
export const getEmployeeMeta = () => request.get('/employees/meta');
export const employeeAiHealthCheck = (payload) => request.post('/employees/ai/health-check', payload);
export const generateEmployeeWorkforceReport = (payload) => request.post('/employees/ai/workforce-report', payload);
export const createDepartment = (payload) => request.post('/employees/departments', payload);
export const createPosition = (payload) => request.post('/employees/positions', payload);
export const checkEmployeeUnique = (params) => request.get('/employees/check-unique', { params });
export const getEmployeeAttachment = (employeeId, field, index) => request.get(`/employees/${employeeId}/attachments/${field}/${index}`);
export const downloadEmployeeAttachment = (employeeId, field, index) => request.get(`/employees/${employeeId}/attachments/${field}/${index}/download`, { responseType: 'blob', skipAuthRedirect: true });
export const createEmployee = (payload) => request.post('/employees', payload);
export const updateEmployee = (id, payload) => request.put(`/employees/${id}`, payload);
export const deleteEmployee = (id) => request.delete(`/employees/${id}`);

export const getPerformanceList = (params) => request.get('/performance/list', { params });
export const getPerformanceSummary = () => request.get('/performance/summary');
export const getPerformanceOptions = () => request.get('/performance/options');
export const getPerformanceDetail = (id) => request.get(`/performance/${id}/detail`);
export const createPerformance = (payload) => request.post('/performance/create', payload);
export const updatePerformance = (id, payload) => request.put(`/performance/${id}`, payload);
export const deletePerformance = (id) => request.delete(`/performance/${id}`);
export const parsePerformanceImport = (formData, params) => request.post('/performance/import/parse', formData, {
  params,
  headers: { 'Content-Type': 'multipart/form-data' },
});
export const confirmPerformanceImport = (payload) => request.post('/performance/import/confirm', payload);
export const exportPerformance = (params) => request.get('/performance/export', { params });
export const checkPerformance = (payload) => request.post('/performance/check', payload);
export const generatePerformanceIndicators = (payload) => request.post('/performance/ai/generate-indicators', payload);
export const autoScorePerformance = (payload) => request.post('/performance/ai/auto-score', payload);
export const generatePerformanceComment = (payload) => request.post('/performance/ai/generate-comment', payload);
export const diagnosePerformance = (payload) => request.post('/performance/ai/diagnose', payload);
export const generatePerformanceReport = (payload) => request.post('/performance/ai/generate-report', payload);
export const reviewPerformanceAppeal = (payload) => request.post('/performance/ai/appeal-review', payload);

export const getPayrollSummary = () => request.get('/payroll/summary');
export const calculatePayroll = (payload) => request.post('/payroll/calculate', payload);

export const getApprovalOverview = (params) => request.get('/approvals/overview', { params });
export const getApprovalDetail = (id) => request.get(`/approvals/${id}`);
export const decideApproval = (id, payload) => request.post(`/approvals/${id}/decision`, payload);
export const batchDecideApproval = (payload) => request.post('/approvals/batch-decision', payload);

export const getReportsSummary = () => request.get('/reports/summary');
export const getAdministrationSummary = () => request.get('/administration/summary');
export const createAsset = (payload) => request.post('/administration/assets', payload);
