<template>
  <div class="page-grid archive-grid">
    <PageCard title="个人档案" hide-header>

      <div class="profile-sheet">
        <section class="profile-hero">
          <div class="profile-hero__avatar-wrap">
            <template v-if="editing">
              <div class="profile-photo-editor">
                <el-avatar :size="72" class="profile-hero__avatar" :src="photoPreview || undefined">{{ !photoPreview ? avatarText : '' }}</el-avatar>
                <el-upload :auto-upload="false" :show-file-list="false" accept="image/png,image/jpeg,image/jpg" :on-change="handlePhotoChange">
                  <el-button size="small" plain>上传证件照</el-button>
                </el-upload>
                <span class="profile-hero__avatar-note">支持 JPG / PNG，建议 1MB 内</span>
              </div>
            </template>
            <template v-else>
              <el-avatar :size="72" class="profile-hero__avatar" :src="photoPreview || undefined">{{ !photoPreview ? avatarText : '' }}</el-avatar>
              <span class="profile-hero__avatar-note">员工证件照</span>
            </template>
          </div>
          <div class="profile-hero__main">
            <div class="profile-hero__head">
              <div class="profile-hero__identity">
                <div class="profile-hero__name-row">
                  <h3>{{ safeUser.name }}</h3>
                  <el-tag :type="statusTagType" effect="light">{{ safeUser.status }}</el-tag>
                </div>
                <p>{{ safeUser.employeeNo }} · {{ safeUser.department }} / {{ safeUser.position }}</p>
              </div>
              <div class="archive-actions archive-actions--hero">
                <el-button v-if="!editing" type="primary" plain @click="startEdit">编辑档案</el-button>
                <template v-else>
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" :loading="saving" @click="saveProfile">保存修改</el-button>
                </template>
              </div>
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
          <el-form ref="formRef" :model="editForm" :rules="rules" label-position="top" class="edit-form">
            <div class="info-grid info-grid--editable">
              <template v-for="item in identityItems" :key="item.label">
                <article v-if="!item.editable || !editing" class="info-card">
                  <span>{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </article>
                <el-form-item v-else :label="item.label" :prop="item.prop">
                  <el-select v-if="item.type === 'select'" v-model="editForm[item.prop]" placeholder="请选择">
                    <el-option v-for="option in item.options" :key="option" :label="option" :value="option" />
                  </el-select>
                  <el-date-picker
                    v-else-if="item.type === 'date'"
                    v-model="editForm[item.prop]"
                    type="date"
                    value-format="YYYY-MM-DD"
                    placeholder="请选择日期"
                    style="width: 100%"
                  />
                  <el-input v-else v-model="editForm[item.prop]" :placeholder="`请输入${item.label}`" />
                </el-form-item>
              </template>
            </div>
          </el-form>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">任职与合同</div>
          <div class="info-grid info-grid--employment">
            <template v-for="item in employmentItems" :key="item.label">
              <article v-if="!item.editable || !editing" class="info-card">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </article>
              <el-form-item v-else :label="item.label" :prop="item.prop" class="employment-form-item">
                <el-input v-model="editForm[item.prop]" :placeholder="`请输入${item.label}`" />
              </el-form-item>
            </template>
          </div>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">联系信息</div>
          <div class="info-grid info-grid--editable">
            <template v-for="item in contactItems" :key="item.label">
              <article v-if="!editing" class="info-card" :class="item.className">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </article>
              <el-form-item v-else :label="item.label" :prop="item.prop" :class="item.className">
                <el-input v-model="editForm[item.prop]" :placeholder="`请输入${item.label}`" />
              </el-form-item>
            </template>
          </div>
        </section>

        <section class="profile-section">
          <div class="profile-section__title">档案材料状态</div>
          <div class="material-grid">
            <article v-for="item in materialItems" :key="item.label" class="material-card">
              <div>
                <strong>{{ item.label }}</strong>
                <p>{{ item.desc }}</p>
              </div>
              <div class="material-card__side">
                <el-tag :type="item.tagType" effect="light">{{ item.status }}</el-tag>
                <div class="material-card__actions">
                  <el-button v-if="item.canPreview" size="small" text @click="previewAttachment(item)">查看</el-button>
                  <el-button v-if="editing && item.canDelete" size="small" text type="danger" @click="removeMaterial(item)">删除</el-button>
                  <el-upload
                    v-if="editing && item.canUpload"
                    :auto-upload="false"
                    :show-file-list="false"
                    :accept="item.accept"
                    :on-change="(file) => handleMaterialChange(item, file)"
                  >
                    <el-button size="small" text>{{ getUploadButtonText(item) }}</el-button>
                  </el-upload>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>

      <el-dialog v-model="previewVisible" :title="previewTitle" width="720px">
        <div v-if="previewLoading" class="material-preview__empty">材料加载中...</div>
        <template v-else>
          <div v-if="previewType === 'image-list'" class="material-preview__carousel-wrap">
            <el-carousel height="520px" indicator-position="outside" arrow="always">
              <el-carousel-item v-for="item in previewContent" :key="item.name">
                <div class="material-preview__carousel-item">
                  <img :src="item.src" class="material-preview__image" :alt="item.name" />
                  <p class="material-preview__caption">{{ item.name }}</p>
                </div>
              </el-carousel-item>
            </el-carousel>
          </div>
          <img v-else-if="previewType === 'image'" :src="previewContent[0]?.src" class="material-preview__image" alt="档案材料预览" />
          <iframe v-else-if="previewType === 'pdf'" :src="previewContent[0]?.src" class="material-preview__frame" />
          <div v-else class="material-preview__empty">当前材料暂不支持在线预览</div>
        </template>
      </el-dialog>
    </PageCard>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

import PageCard from '@/components/PageCard.vue';
import { getEmployeeAttachment, updateMyArchive } from '@/api/modules';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
const formRef = ref();
const editing = ref(false);
const saving = ref(false);
const previewVisible = ref(false);
const previewLoading = ref(false);
const previewContent = ref([]);
const previewType = ref('');
const previewTitle = ref('材料查看');
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
  photoAttachment: store.user?.photoAttachment || {},
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
  photoAttachment: {},
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
  editForm.photoAttachment = safeUser.value.photoAttachment || {};
};

syncEditForm();

const photoPreview = computed(() => {
  const attachment = editing.value ? editForm.photoAttachment : safeUser.value.photoAttachment;
  if (!attachment?.content_base64) return '';
  return `data:${attachment.mime_type || 'image/png'};base64,${attachment.content_base64}`;
});

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
  { label: '性别', value: safeUser.value.gender, prop: 'gender', editable: true, type: 'select', options: ['男', '女'] },
  { label: '出生日期', value: safeUser.value.birthDate, prop: 'birthDate', editable: true, type: 'date' },
  { label: '民族', value: safeUser.value.ethnicity, prop: 'ethnicity', editable: true, type: 'text' },
  { label: '学历', value: safeUser.value.education, prop: 'education', editable: true, type: 'select', options: educationOptions },
  { label: '毕业院校', value: safeUser.value.graduateSchool, prop: 'graduateSchool', editable: true, type: 'text' },
  { label: '专业', value: safeUser.value.major, prop: 'major', editable: true, type: 'text' },
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

const contactItems = computed(() => [
  { label: '紧急联系人', value: safeUser.value.emergencyContact || '—', prop: 'emergencyContact' },
  { label: '紧急联系人电话', value: safeUser.value.emergencyContactPhone || '—', prop: 'emergencyContactPhone' },
  { label: '现居住地址', value: safeUser.value.currentAddress || '—', prop: 'currentAddress', className: 'span-two contact-row-two' },
]);

const getUploadButtonText = (item) => {
  if (item.apiField !== 'id_card_attachments') return '上传';
  const currentCount = Array.isArray(safeUser.value[item.field]) ? safeUser.value[item.field].length : 0;
  return currentCount === 0 ? '上传正面' : '上传反面';
};

const attachmentStatus = (items, uploadedText, missingText = '待补充') => {
  const count = Array.isArray(items) ? items.length : 0;
  if (count > 0) {
    return { status: count > 1 ? `已上传 ${count} 份` : uploadedText, tagType: 'success', hasAttachment: true };
  }
  return { status: missingText, tagType: 'warning', hasAttachment: false };
};

const materialItems = computed(() => {
  const idCard = attachmentStatus(safeUser.value.idCardAttachments, '已上传');
  const education = attachmentStatus(safeUser.value.educationCertificateAttachments, '已上传');
  const contract = attachmentStatus(safeUser.value.laborContractAttachments, '已归档', '待归档');
  const medical = attachmentStatus(safeUser.value.medicalReportAttachments, '已上传');
  return [
    {
      label: '身份证材料',
      field: 'idCardAttachments',
      apiField: 'id_card_attachments',
      previewField: 'id_card_attachments',
      accept: '.png,.jpg,.jpeg,.pdf',
      canUpload: true,
      maxCount: 2,
      canDelete: idCard.hasAttachment,
      canPreview: idCard.hasAttachment,
      ...idCard,
      desc: idCard.tagType === 'success' ? '身份证正反面已归档，可供 HR 核验。' : '请上传身份证正反面扫描件。',
    },
    {
      label: '学历证明',
      field: 'educationCertificateAttachments',
      apiField: 'education_certificate_attachments',
      previewField: 'education_certificate_attachments',
      accept: '.png,.jpg,.jpeg,.pdf',
      canUpload: true,
      maxCount: 1,
      canDelete: education.hasAttachment,
      canPreview: education.hasAttachment,
      ...education,
      desc: education.tagType === 'success' ? '学历与学位证明材料已同步档案。' : '请上传学历或学位证明材料。',
    },
    {
      label: '劳动合同',
      field: 'laborContractAttachments',
      apiField: 'labor_contract_attachments',
      previewField: 'labor_contract_attachments',
      accept: '',
      canUpload: false,
      maxCount: 1,
      canDelete: false,
      canPreview: contract.hasAttachment,
      ...contract,
      desc: contract.tagType === 'success' ? '当前劳动合同已签署并完成归档。' : '合同材料尚未归档，请联系 HR 确认。',
    },
    {
      label: '体检报告',
      field: 'medicalReportAttachments',
      apiField: 'medical_report_attachments',
      previewField: 'medical_report_attachments',
      accept: '.png,.jpg,.jpeg,.pdf',
      canUpload: true,
      maxCount: 1,
      canDelete: medical.hasAttachment,
      canPreview: medical.hasAttachment,
      ...medical,
      desc: medical.tagType === 'success' ? '体检报告材料已上传归档。' : '请上传最新体检报告。',
    },
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

const handlePhotoChange = async (uploadFile) => {
  const source = uploadFile?.raw;
  if (!source) return;
  const isValidType = ['image/jpeg', 'image/png'].includes(source.type);
  if (!isValidType) {
    ElMessage.error('证件照仅支持 JPG / PNG');
    return;
  }
  if (source.size > 1024 * 1024) {
    ElMessage.error('证件照大小不能超过 1MB');
    return;
  }
  try {
    const contentBase64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
      reader.onerror = reject;
      reader.readAsDataURL(source);
    });
    editForm.photoAttachment = {
      name: source.name,
      mime_type: source.type,
      size: source.size,
      content_base64: contentBase64,
    };
  } catch {
    ElMessage.error('证件照读取失败，请重试');
  }
};

const handleMaterialChange = async (item, uploadFile) => {
  const source = uploadFile?.raw;
  if (!source) return;
  const fileName = source.name.toLowerCase();
  const isImage = ['image/jpeg', 'image/png'].includes(source.type);
  const isPdf = source.type === 'application/pdf' || fileName.endsWith('.pdf');
  if (!isImage && !isPdf) {
    ElMessage.error(`${item.label}仅支持 JPG / PNG / PDF`);
    return;
  }
  if (source.size > 2 * 1024 * 1024) {
    ElMessage.error(`${item.label}大小不能超过 2MB`);
    return;
  }
  const currentAttachments = Array.isArray(safeUser.value[item.field]) ? [...safeUser.value[item.field]] : [];
  if (currentAttachments.length >= item.maxCount) {
    ElMessage.warning(`${item.label}最多上传 ${item.maxCount} 份`);
    return;
  }
  saving.value = true;
  try {
    const contentBase64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
      reader.onerror = reject;
      reader.readAsDataURL(source);
    });
    const nextAttachments = [...currentAttachments, {
      name: source.name,
      mime_type: isPdf ? 'application/pdf' : source.type,
      size: source.size,
      content_base64: contentBase64,
    }];
    const payload = {
      employee_no: safeUser.value.employeeNo,
      name: safeUser.value.name,
      department: safeUser.value.department,
      position: safeUser.value.position,
      role: store.user?.role || 'employee',
      salary_base: 0.01,
      performance_base: 0,
      hire_date: safeUser.value.hireDate === '—' ? '' : safeUser.value.hireDate,
      resignation_date: store.user?.resignationDate || '',
      status: safeUser.value.status === '—' ? '在职' : safeUser.value.status,
      id_card_no: 'SELF-LOCKED',
      phone: store.user?.phone || '13800000000',
      email: store.user?.email || 'employee@local.dev',
      probation_end_date: safeUser.value.probationEndDate === '—' ? '' : safeUser.value.probationEndDate,
      emergency_contact: editForm.emergencyContact,
      emergency_contact_phone: editForm.emergencyContactPhone,
      political_status: store.user?.politicalStatus || '',
      gender: editForm.gender,
      birth_date: editForm.birthDate,
      registered_address: '',
      current_address: editForm.currentAddress,
      ethnicity: editForm.ethnicity,
      education: editForm.education,
      graduate_school: editForm.graduateSchool,
      major: editForm.major,
      contract_type: safeUser.value.contractType === '—' ? '' : safeUser.value.contractType,
      contract_sign_date: safeUser.value.contractSignDate === '—' ? '' : safeUser.value.contractSignDate,
      contract_end_date: safeUser.value.contractEndDate === '—' ? '' : safeUser.value.contractEndDate,
      social_security_base: 0,
      housing_fund_base: 0,
      bank_account: '',
      bank_name: '',
      job_level: safeUser.value.jobLevel === '—' ? '' : safeUser.value.jobLevel,
      report_to: safeUser.value.reportTo === '—' ? '' : safeUser.value.reportTo,
      work_location: safeUser.value.workLocation === '—' ? '' : safeUser.value.workLocation,
      photo_attachment: editForm.photoAttachment || {},
      id_card_attachments: item.apiField === 'id_card_attachments' ? nextAttachments : safeUser.value.idCardAttachments,
      education_certificate_attachments: item.apiField === 'education_certificate_attachments' ? nextAttachments : safeUser.value.educationCertificateAttachments,
      labor_contract_attachments: safeUser.value.laborContractAttachments,
      medical_report_attachments: item.apiField === 'medical_report_attachments' ? nextAttachments : safeUser.value.medicalReportAttachments,
    };
    await updateMyArchive(payload);
    await store.hydrateUser();
    syncEditForm();
    ElMessage.success(`${item.label}上传成功`);
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || error?.message || `${item.label}上传失败，请稍后重试`);
  } finally {
    saving.value = false;
  }
};

const removeMaterial = async (item) => {
  try {
    await ElMessageBox.confirm(`确认删除${item.label}吗？删除后将从档案中移除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    });
  } catch {
    return;
  }

  saving.value = true;
  try {
    const payload = {
      employee_no: safeUser.value.employeeNo,
      name: safeUser.value.name,
      department: safeUser.value.department,
      position: safeUser.value.position,
      role: store.user?.role || 'employee',
      salary_base: 0.01,
      performance_base: 0,
      hire_date: safeUser.value.hireDate === '—' ? '' : safeUser.value.hireDate,
      resignation_date: store.user?.resignationDate || '',
      status: safeUser.value.status === '—' ? '在职' : safeUser.value.status,
      id_card_no: 'SELF-LOCKED',
      phone: store.user?.phone || '13800000000',
      email: store.user?.email || 'employee@local.dev',
      probation_end_date: safeUser.value.probationEndDate === '—' ? '' : safeUser.value.probationEndDate,
      emergency_contact: editForm.emergencyContact,
      emergency_contact_phone: editForm.emergencyContactPhone,
      political_status: store.user?.politicalStatus || '',
      gender: editForm.gender,
      birth_date: editForm.birthDate,
      registered_address: '',
      current_address: editForm.currentAddress,
      ethnicity: editForm.ethnicity,
      education: editForm.education,
      graduate_school: editForm.graduateSchool,
      major: editForm.major,
      contract_type: safeUser.value.contractType === '—' ? '' : safeUser.value.contractType,
      contract_sign_date: safeUser.value.contractSignDate === '—' ? '' : safeUser.value.contractSignDate,
      contract_end_date: safeUser.value.contractEndDate === '—' ? '' : safeUser.value.contractEndDate,
      social_security_base: 0,
      housing_fund_base: 0,
      bank_account: '',
      bank_name: '',
      job_level: safeUser.value.jobLevel === '—' ? '' : safeUser.value.jobLevel,
      report_to: safeUser.value.reportTo === '—' ? '' : safeUser.value.reportTo,
      work_location: safeUser.value.workLocation === '—' ? '' : safeUser.value.workLocation,
      photo_attachment: editForm.photoAttachment || {},
      id_card_attachments: item.apiField === 'id_card_attachments' ? [] : safeUser.value.idCardAttachments,
      education_certificate_attachments: item.apiField === 'education_certificate_attachments' ? [] : safeUser.value.educationCertificateAttachments,
      labor_contract_attachments: safeUser.value.laborContractAttachments,
      medical_report_attachments: item.apiField === 'medical_report_attachments' ? [] : safeUser.value.medicalReportAttachments,
    };
    await updateMyArchive(payload);
    await store.hydrateUser();
    syncEditForm();
    if (previewVisible.value && previewTitle.value === item.label) {
      previewVisible.value = false;
    }
    ElMessage.success(`${item.label}已删除`);
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || error?.message || `${item.label}删除失败，请稍后重试`);
  } finally {
    saving.value = false;
  }
};

const previewAttachment = async (item) => {
  previewVisible.value = true;
  previewLoading.value = true;
  previewTitle.value = item.label;
  previewContent.value = [];
  previewType.value = '';
  try {
    const attachments = Array.isArray(safeUser.value[item.field]) ? safeUser.value[item.field] : [];
    const results = await Promise.all(
      attachments.map((_, index) => getEmployeeAttachment(safeUser.value.employeeNo, item.previewField, index)),
    );
    const files = results
      .map((result) => result?.data)
      .filter((attachment) => attachment?.content_base64)
      .map((attachment) => ({
        name: attachment.name,
        mimeType: attachment.mime_type || 'image/png',
        src: `data:${attachment.mime_type || 'image/png'};base64,${attachment.content_base64}`,
      }));
    if (!files.length) {
      throw new Error('附件内容不存在');
    }
    previewContent.value = files;
    const allImages = files.every((file) => file.mimeType !== 'application/pdf');
    if (allImages && files.length > 1) {
      previewType.value = 'image-list';
    } else if (files[0].mimeType === 'application/pdf') {
      previewType.value = 'pdf';
    } else {
      previewType.value = 'image';
    }
  } catch (error) {
    previewVisible.value = false;
    ElMessage.error(error?.response?.data?.detail || error?.message || '查看失败，请稍后重试');
  } finally {
    previewLoading.value = false;
  }
};

const saveProfile = async () => {
  await formRef.value?.validate();
  saving.value = true;
  try {
    const payload = {
      employee_no: safeUser.value.employeeNo,
      name: safeUser.value.name,
      department: safeUser.value.department,
      position: safeUser.value.position,
      role: store.user?.role || 'employee',
      salary_base: 0.01,
      performance_base: 0,
      hire_date: safeUser.value.hireDate === '—' ? '' : safeUser.value.hireDate,
      resignation_date: store.user?.resignationDate || '',
      status: safeUser.value.status === '—' ? '在职' : safeUser.value.status,
      id_card_no: 'SELF-LOCKED',
      phone: store.user?.phone || '13800000000',
      email: store.user?.email || 'employee@local.dev',
      probation_end_date: safeUser.value.probationEndDate === '—' ? '' : safeUser.value.probationEndDate,
      emergency_contact: editForm.emergencyContact,
      emergency_contact_phone: editForm.emergencyContactPhone,
      political_status: store.user?.politicalStatus || '',
      gender: editForm.gender,
      birth_date: editForm.birthDate,
      registered_address: '',
      current_address: editForm.currentAddress,
      ethnicity: editForm.ethnicity,
      education: editForm.education,
      graduate_school: editForm.graduateSchool,
      major: editForm.major,
      contract_type: safeUser.value.contractType === '—' ? '' : safeUser.value.contractType,
      contract_sign_date: safeUser.value.contractSignDate === '—' ? '' : safeUser.value.contractSignDate,
      contract_end_date: safeUser.value.contractEndDate === '—' ? '' : safeUser.value.contractEndDate,
      social_security_base: 0,
      housing_fund_base: 0,
      bank_account: '',
      bank_name: '',
      job_level: safeUser.value.jobLevel === '—' ? '' : safeUser.value.jobLevel,
      report_to: safeUser.value.reportTo === '—' ? '' : safeUser.value.reportTo,
      work_location: safeUser.value.workLocation === '—' ? '' : safeUser.value.workLocation,
      photo_attachment: editForm.photoAttachment || {},
      id_card_attachments: safeUser.value.idCardAttachments,
      education_certificate_attachments: safeUser.value.educationCertificateAttachments,
      labor_contract_attachments: safeUser.value.laborContractAttachments,
      medical_report_attachments: safeUser.value.medicalReportAttachments,
    };

    await updateMyArchive(payload);
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

.archive-actions--hero {
  justify-content: flex-end;
  align-items: center;
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

.profile-photo-editor {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.profile-hero__main,
.profile-section {
  display: grid;
  gap: 16px;
}

.profile-hero__identity {
  display: grid;
  gap: 6px;
}

.profile-hero__name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
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

.edit-form :deep(.el-form-item),
.info-grid :deep(.el-form-item) {
  margin-bottom: 0;
}

.info-grid :deep(.el-form-item__label) {
  padding-bottom: 6px;
  color: var(--hr-info);
}

.info-grid :deep(.el-input__wrapper),
.info-grid :deep(.el-select__wrapper),
.info-grid :deep(.el-textarea__inner) {
  border-radius: 16px;
}

.contact-row-two {
  grid-column: 1 / -1;
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

  .span-two,
  .contact-row-two {
    grid-column: span 1;
  }
}

.material-card__side {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.material-card__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.material-preview__carousel-wrap {
  padding: 0 8px 8px;
}

.material-preview__carousel-item {
  height: 100%;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 12px;
}

.material-preview__caption {
  margin: 0;
  color: var(--hr-info);
  font-size: 12px;
}

.material-preview__image {
  width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 12px;
  border: 1px solid rgba(64, 158, 255, 0.12);
}

.material-preview__frame {
  width: 100%;
  height: 70vh;
  border: 0;
  border-radius: 12px;
  background: #f5f7fa;
}

.material-preview__empty {
  min-height: 160px;
  display: grid;
  place-items: center;
  color: var(--hr-info);
}

@media (max-width: 767px) {
  .profile-hero__head,
  .material-card {
    display: grid;
    grid-template-columns: 1fr;
    align-items: flex-start;
  }

  .material-card__side {
    justify-items: start;
  }
}
</style>
