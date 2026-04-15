<template>
  <div class="page-grid archive-grid">
    <PageCard title="个人档案" description="查看档案基础信息，并维护员工本人可修改的资料。">
      <template #actions>
        <div class="archive-actions">
          <el-button v-if="!editing" type="primary" plain @click="startEdit">编辑资料</el-button>
          <template v-else>
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
          </template>
        </div>
      </template>

      <div class="profile-sheet">
        <section class="profile-hero">
          <div class="profile-hero__avatar-wrap">
            <el-avatar :size="72" class="profile-hero__avatar">{{ avatarText }}</el-avatar>
            <span class="profile-hero__avatar-note">员工头像占位</span>
          </div>
          <div class="profile-hero__main">
            <div class="profile-hero__head">
              <div>
                <h3>{{ safeUser.name }}</h3>
                <p>{{ safeUser.employeeNo }} · {{ safeUser.department }} / {{ safeUser.position }}</p>
              </div>
              <el-tag :type="statusTagType" effect="light">{{ safeUser.status }}</el-tag>
            </div>
            <div class="profile-hero__meta">
              <div v-for="item in heroMeta" :key="item.label" class="meta-chip">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">基础信息</div>
          <div class="info-grid">
            <article v-for="item in identityItems" :key="item.label" class="info-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </article>
          </div>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">任职与合同</div>
          <div class="info-grid info-grid--employment">
            <article v-for="item in employmentItems" :key="item.label" class="info-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </article>
          </div>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">本人可维护资料</div>
          <el-form ref="formRef" :model="editForm" :rules="rules" label-position="top" class="edit-form">
            <div class="info-grid info-grid--editable">
              <el-form-item label="性别" prop="gender">
                <el-select v-model="editForm.gender" :disabled="!editing" placeholder="请选择性别">
                  <el-option label="男" value="男" />
                  <el-option label="女" value="女" />
                </el-select>
              </el-form-item>
              <el-form-item label="出生日期" prop="birthDate">
                <el-date-picker v-model="editForm.birthDate" type="date" value-format="YYYY-MM-DD" :disabled="!editing" placeholder="请选择出生日期" style="width: 100%" />
              </el-form-item>
              <el-form-item label="民族" prop="ethnicity">
                <el-input v-model="editForm.ethnicity" :disabled="!editing" placeholder="请输入民族" />
              </el-form-item>
              <el-form-item label="学历" prop="education">
                <el-select v-model="editForm.education" :disabled="!editing" placeholder="请选择学历">
                  <el-option v-for="item in educationOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
              <el-form-item label="毕业院校" prop="graduateSchool">
                <el-input v-model="editForm.graduateSchool" :disabled="!editing" placeholder="请输入毕业院校" />
              </el-form-item>
              <el-form-item label="专业" prop="major">
                <el-input v-model="editForm.major" :disabled="!editing" placeholder="请输入专业" />
              </el-form-item>
              <el-form-item label="现居住地址" prop="currentAddress" class="span-two">
                <el-input v-model="editForm.currentAddress" :disabled="!editing" placeholder="请输入现居住地址" />
              </el-form-item>
              <el-form-item label="紧急联系人" prop="emergencyContact">
                <el-input v-model="editForm.emergencyContact" :disabled="!editing" placeholder="请输入紧急联系人" />
              </el-form-item>
              <el-form-item label="紧急联系人电话" prop="emergencyContactPhone">
                <el-input v-model="editForm.emergencyContactPhone" :disabled="!editing" placeholder="请输入紧急联系人电话" />
              </el-form-item>
            </div>
          </el-form>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">档案材料状态</div>
          <div class="material-grid">
            <article v-for="item in materialItems" :key="item.label" class="material-card">
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.desc }}</p>
              </div>
              <el-tag :type="item.tagType" effect="light">{{ item.status }}</el-tag>
            </article>
          </div>
        </section>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { getEmployees, updateEmployee } from '@/api/modules';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
const formRef = ref();
const editing = ref(false);
const saving = ref(false);
const educationOptions = ['高中', '大专', '本科', '硕士', '博士'];

const safeUser = computed(() => ({
  name: store.user?.name || '—',
  employeeNo: store.user?.employeeNo || '—',
  department: store.user?.department || '—',
  position: store.user?.position || '—',
  status: store.user?.status || '—',
  hireDate: store.user?.hireDate || '—',
  gender: store.user?.gender || '—',
  birthDate: store.user?.birthDate || '—',
  ethnicity: store.user?.ethnicity || '—',
  education: store.user?.education || '—',
  graduateSchool: store.user?.graduateSchool || '—',
  major: store.user?.major || '—',
  workLocation: store.user?.workLocation || '—',
  reportTo: store.user?.reportTo || '—',
  jobLevel: store.user?.jobLevel || '—',
  probationEndDate: store.user?.probationEndDate || '—',
  contractType: store.user?.contractType || '—',
  contractSignDate: store.user?.contractSignDate || '—',
  contractEndDate: store.user?.contractEndDate || '—',
  currentAddress: store.user?.currentAddress || '',
  emergencyContact: store.user?.emergencyContact || '',
  emergencyContactPhone: store.user?.emergencyContactPhone || '',
  idCardAttachments: store.user?.idCardAttachments || [],
  educationCertificateAttachments: store.user?.educationCertificateAttachments || [],
  laborContractAttachments: store.user?.laborContractAttachments || [],
  medicalReportAttachments: store.user?.medicalReportAttachments || [],
}));

const editForm = reactive({
  gender: '',
  birthDate: '',
  ethnicity: '',
  education: '',
  graduateSchool: '',
  major: '',
  currentAddress: '',
  emergencyContact: '',
  emergencyContactPhone: '',
});

const syncEditForm = () => {
  editForm.gender = safeUser.value.gender === '—' ? '' : safeUser.value.gender;
  editForm.birthDate = safeUser.value.birthDate === '—' ? '' : safeUser.value.birthDate;
  editForm.ethnicity = safeUser.value.ethnicity === '—' ? '' : safeUser.value.ethnicity;
  editForm.education = safeUser.value.education === '—' ? '' : safeUser.value.education;
  editForm.graduateSchool = safeUser.value.graduateSchool === '—' ? '' : safeUser.value.graduateSchool;
  editForm.major = safeUser.value.major === '—' ? '' : safeUser.value.major;
  editForm.currentAddress = safeUser.value.currentAddress || '';
  editForm.emergencyContact = safeUser.value.emergencyContact || '';
  editForm.emergencyContactPhone = safeUser.value.emergencyContactPhone || '';
};

syncEditForm();

const avatarText = computed(() => String(safeUser.value.name || '员').slice(0, 1));
const statusTagType = computed(() => {
  if (safeUser.value.status === '在职') return 'success';
  if (safeUser.value.status === '试用') return 'warning';
  if (safeUser.value.status === '离职') return 'danger';
  return 'info';
});

const heroMeta = computed(() => [
  { label: '入职日期', value: safeUser.value.hireDate },
  { label: '工作地点', value: safeUser.value.workLocation },
  { label: '汇报上级', value: safeUser.value.reportTo },
  { label: '职级', value: safeUser.value.jobLevel },
]);

const identityItems = computed(() => [
  { label: '性别', value: safeUser.value.gender },
  { label: '出生日期', value: safeUser.value.birthDate },
  { label: '民族', value: safeUser.value.ethnicity },
  { label: '学历', value: safeUser.value.education },
  { label: '毕业院校', value: safeUser.value.graduateSchool },
  { label: '专业', value: safeUser.value.major },
]);

const employmentItems = computed(() => [
  { label: '部门', value: safeUser.value.department },
  { label: '岗位', value: safeUser.value.position },
  { label: '职级', value: safeUser.value.jobLevel },
  { label: '汇报上级', value: safeUser.value.reportTo },
  { label: '试用期结束', value: safeUser.value.probationEndDate },
  { label: '合同类型', value: safeUser.value.contractType },
  { label: '合同签订日期', value: safeUser.value.contractSignDate },
  { label: '合同到期日期', value: safeUser.value.contractEndDate },
]);

const attachmentStatus = (items, uploadedText, missingText = '待补充') => {
  const count = Array.isArray(items) ? items.length : 0;
  if (count > 0) {
    return { status: count > 1 ? `已上传 ${count} 份` : uploadedText, tagType: 'success' };
  }
  return { status: missingText, tagType: 'warning' };
};

const materialItems = computed(() => {
  const idCard = attachmentStatus(safeUser.value.idCardAttachments, '已上传');
  const education = attachmentStatus(safeUser.value.educationCertificateAttachments, '已上传');
  const contract = attachmentStatus(safeUser.value.laborContractAttachments, '已归档', '待归档');
  const medical = attachmentStatus(safeUser.value.medicalReportAttachments, '已上传');
  return [
    { label: '身份证材料', ...idCard, desc: idCard.tagType === 'success' ? '身份证正反面已归档，可供 HR 核验。' : '请联系 HR 补充身份证材料。' },
    { label: '学历证明', ...education, desc: education.tagType === 'success' ? '学历与学位证明材料已同步档案。' : '请联系 HR 补充学历证明材料。' },
    { label: '劳动合同', ...contract, desc: contract.tagType === 'success' ? '当前劳动合同已签署并完成归档。' : '合同材料尚未归档，请联系 HR 确认。' },
    { label: '体检报告', ...medical, desc: medical.tagType === 'success' ? '体检报告材料已上传归档。' : '请在本月内补充最新体检报告。' },
  ];
});

const rules = {
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birthDate: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
  ethnicity: [{ required: true, message: '请输入民族', trigger: 'blur' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  graduateSchool: [{ required: true, message: '请输入毕业院校', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  currentAddress: [{ required: true, message: '请输入现居住地址', trigger: 'blur' }],
  emergencyContact: [{ required: true, message: '请输入紧急联系人', trigger: 'blur' }],
  emergencyContactPhone: [{ required: true, message: '请输入紧急联系人电话', trigger: 'blur' }, { pattern: /^\d{11}$/, message: '紧急联系人电话需为 11 位数字', trigger: 'blur' }],
};

const startEdit = () => {
  syncEditForm();
  editing.value = true;
};

const cancelEdit = () => {
  syncEditForm();
  editing.value = false;
  formRef.value?.clearValidate?.();
};

const saveProfile = async () => {
  await formRef.value?.validate();
  saving.value = true;
  try {
    const employeesResult = await getEmployees();
    const records = employeesResult.data || [];
    const current = records.find((item) => String(item.employee_no || item.employeeNo) === String(safeUser.value.employeeNo));
    if (!current?.id) {
      throw new Error('未找到当前员工档案');
    }

    const payload = {
      ...current,
      employee_no: current.employee_no || current.employeeNo,
      name: current.name,
      department: current.department,
      position: current.position,
      role: current.role || store.user?.role || 'employee',
      salary_base: Number(current.salary_base || 0.01),
      performance_base: Number(current.performance_base || 0),
      hire_date: current.hire_date || store.user?.hireDate || '',
      resignation_date: current.resignation_date || '',
      status: current.status || store.user?.status || '在职',
      id_card_no: current.id_card_no || '',
      phone: current.phone || store.user?.phone || '',
      email: current.email || store.user?.email || '',
      probation_end_date: current.probation_end_date || store.user?.probationEndDate || '',
      emergency_contact: editForm.emergencyContact,
      emergency_contact_phone: editForm.emergencyContactPhone,
      political_status: current.political_status || store.user?.politicalStatus || '',
      gender: editForm.gender,
      birth_date: editForm.birthDate,
      registered_address: current.registered_address || '',
      current_address: editForm.currentAddress,
      ethnicity: editForm.ethnicity,
      education: editForm.education,
      graduate_school: editForm.graduateSchool,
      major: editForm.major,
      contract_type: current.contract_type || store.user?.contractType || '',
      contract_sign_date: current.contract_sign_date || store.user?.contractSignDate || '',
      contract_end_date: current.contract_end_date || store.user?.contractEndDate || '',
      social_security_base: Number(current.social_security_base || 0),
      housing_fund_base: Number(current.housing_fund_base || 0),
      bank_account: current.bank_account || '',
      bank_name: current.bank_name || '',
      job_level: current.job_level || store.user?.jobLevel || '',
      report_to: current.report_to || store.user?.reportTo || '',
      work_location: current.work_location || store.user?.workLocation || '',
      id_card_attachments: current.id_card_attachments || [],
      education_certificate_attachments: current.education_certificate_attachments || [],
      labor_contract_attachments: current.labor_contract_attachments || [],
      medical_report_attachments: current.medical_report_attachments || [],
    };

    await updateEmployee(current.id, payload);
    await store.hydrateUser();
    syncEditForm();
    editing.value = false;
    ElMessage.success('个人档案已更新');
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || error?.message || '保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
.archive-grid,
.profile-sheet,
.profile-hero__meta,
.info-grid,
.material-grid {
  display: grid;
  gap: 12px;
}

.archive-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.profile-sheet {
  gap: 18px;
}

.profile-hero {
  display: grid;
  grid-template-columns: 108px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(135deg, #f7fbff 0%, #eef5ff 100%);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.profile-hero__avatar-wrap {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.profile-hero__avatar {
  background: linear-gradient(135deg, #4c8dff, #2ecf8f);
  color: #fff;
  font-size: 26px;
  font-weight: 700;
}

.profile-hero__avatar-note {
  color: #8c9bb1;
  font-size: 12px;
}

.profile-hero__main,
.profile-section {
  display: grid;
  gap: 16px;
}

.profile-hero__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.profile-hero__head h3 {
  margin: 0;
  color: var(--hr-title);
  font-size: 22px;
}

.profile-hero__head p {
  margin: 6px 0 0;
  color: var(--hr-info);
  font-size: 13px;
}

.profile-hero__meta {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.meta-chip,
.info-card,
.material-card {
  border: 1px solid rgba(64, 158, 255, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 16px;
}

.meta-chip,
.info-card {
  padding: 12px 14px;
  display: grid;
  gap: 6px;
}

.meta-chip span,
.info-card span,
.material-card p {
  color: var(--hr-info);
  font-size: 12px;
  line-height: 1.7;
  margin: 0;
}

.meta-chip strong,
.info-card strong,
.material-card strong,
.profile-section__title {
  color: var(--hr-title);
}

.profile-section__title {
  font-size: 14px;
  font-weight: 700;
}

.info-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.info-grid--employment {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.info-grid--editable {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.edit-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.span-two {
  grid-column: span 2;
}

.material-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.material-card {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

@media (max-width: 1360px) {
  .profile-hero__meta,
  .info-grid--employment,
  .info-grid--editable {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .profile-hero,
  .material-grid,
  .info-grid,
  .info-grid--editable {
    grid-template-columns: 1fr;
  }

  .span-two {
    grid-column: span 1;
  }
}

@media (max-width: 767px) {
  .profile-hero__head,
  .material-card {
    display: grid;
    grid-template-columns: 1fr;
    align-items: flex-start;
  }
}
</style>
