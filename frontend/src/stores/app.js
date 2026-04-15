import { defineStore } from 'pinia';

import { getCurrentUser, loginApi, logoutApi } from '@/api/modules';
import { roleMenus } from '@/constants/menus';
import { ROLE_HOME } from '@/constants/roles';

const storageKey = 'hr-system-user';
const tokenKey = 'hr-system-token';
const refreshTokenKey = 'hr-system-refresh-token';

const getStoredUser = () => {
  const raw = localStorage.getItem(storageKey);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

export const useAppStore = defineStore('app', {
  state: () => ({
    user: getStoredUser(),
    token: localStorage.getItem(tokenKey) || '',
    refreshToken: localStorage.getItem(refreshTokenKey) || '',
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    menus: (state) => roleMenus[state.user?.role] || [],
    homePath: (state) => ROLE_HOME[state.user?.role] || '/login',
  },
  actions: {
    async login(payload) {
      const result = await loginApi(payload);
      this.user = result.data.user;
      this.token = result.data.token;
      this.refreshToken = result.data.refreshToken;
      localStorage.setItem(storageKey, JSON.stringify(this.user));
      localStorage.setItem(tokenKey, this.token);
      localStorage.setItem(refreshTokenKey, this.refreshToken);
      return result.data;
    },
    async hydrateUser() {
      if (!this.token) return null;
      const result = await getCurrentUser();
      if (result?.data) {
        this.user = {
          name: result.data.name,
          role: result.data.role,
          department: result.data.department,
          employeeNo: result.data.employeeNo,
          position: result.data.position,
          hireDate: result.data.hire_date,
          resignationDate: result.data.resignation_date,
          politicalStatus: result.data.political_status,
          status: result.data.status,
          phone: result.data.phone,
          email: result.data.email,
          gender: result.data.gender,
          birthDate: result.data.birth_date,
          ethnicity: result.data.ethnicity,
          education: result.data.education,
          graduateSchool: result.data.graduate_school,
          major: result.data.major,
          jobLevel: result.data.job_level,
          reportTo: result.data.report_to,
          workLocation: result.data.work_location,
          probationEndDate: result.data.probation_end_date,
          contractType: result.data.contract_type,
          contractSignDate: result.data.contract_sign_date,
          contractEndDate: result.data.contract_end_date,
          currentAddress: result.data.current_address,
          emergencyContact: result.data.emergency_contact,
          emergencyContactPhone: result.data.emergency_contact_phone,
          idCardAttachments: result.data.id_card_attachments || [],
          educationCertificateAttachments: result.data.education_certificate_attachments || [],
          laborContractAttachments: result.data.labor_contract_attachments || [],
          medicalReportAttachments: result.data.medical_report_attachments || [],
        };
        localStorage.setItem(storageKey, JSON.stringify(this.user));
      }
      return this.user;
    },
    async logout() {
      try {
        if (this.refreshToken) {
          await logoutApi({ refresh_token: this.refreshToken });
        }
      } finally {
        this.user = null;
        this.token = '';
        this.refreshToken = '';
        localStorage.removeItem(tokenKey);
        localStorage.removeItem(refreshTokenKey);
        localStorage.removeItem(storageKey);
      }
    },
  },
});
