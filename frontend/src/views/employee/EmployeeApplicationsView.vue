<template>
  <div class="page-grid applications-page">
    <PageCard class="applications-card">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">新的申请</el-button>
      </template>

      <div class="applications-history">
        <el-table :data="rows" width="100%" v-loading="loading">
          <template #empty>
            <el-empty description="暂无申请记录" />
          </template>
          <el-table-column prop="leave_type" label="类型" min-width="120" />
          <el-table-column label="时间" min-width="220">
            <template #default="scope">{{ formatPeriod(scope.row) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="120" />
          <el-table-column prop="approver" label="审批人" min-width="120" />
          <el-table-column label="操作" min-width="120">
            <template #default="scope">
              <el-button link type="primary" @click="openDetail(scope.row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </PageCard>

    <el-dialog v-model="showCreateDialog" width="560px" title="新的申请" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="applications-form">
        <el-form-item label="申请类型" prop="leave_type">
          <el-select v-model="form.leave_type" placeholder="请选择申请类型">
            <el-option
              v-for="item in applicationTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
              :disabled="item.disabled"
            />
          </el-select>
        </el-form-item>
        <div class="apps-type-tip">已同步 HR 审批类型，资产类、行政资源类、人事异动类与加班申请均已支持专属表单。</div>
        <template v-if="isOfficeSupplyType">
          <el-form-item label="用品名称" prop="item_name">
            <el-input v-model="form.item_name" placeholder="如：A4纸、签字笔、文件夹" />
          </el-form-item>
          <el-form-item label="申请数量" prop="quantity">
            <el-input-number v-model="form.quantity" :min="1" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="需求时间" prop="needed_by">
            <el-input v-model="form.needed_by" placeholder="如：2026-04-20 10:00 / 尽快" />
          </el-form-item>
          <el-form-item label="申请说明" prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入领用用途说明" />
          </el-form-item>
        </template>
        <template v-else-if="isAssetRequestType">
          <el-form-item label="资产名称" prop="asset_code">
            <el-select v-model="form.asset_code" placeholder="请选择资产">
              <el-option
                v-for="item in assetOptions"
                :key="item.code"
                :label="item.label"
                :value="item.code"
                :disabled="item.disabled"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="申请数量" prop="quantity">
            <el-input-number v-model="form.quantity" :min="1" :max="selectedAssetAvailable || 1" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="需求时间" prop="needed_by">
            <el-input v-model="form.needed_by" placeholder="如：2026-04-20 10:00 / 尽快" />
          </el-form-item>
          <div v-if="selectedAssetMeta" class="apps-asset-meta">
            <span>类型：{{ selectedAssetMeta.type }}</span>
            <span>总量：{{ selectedAssetMeta.total }}</span>
            <span>可用：{{ selectedAssetAvailable }}</span>
          </div>
          <el-form-item label="申请说明" prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入领用用途说明" />
          </el-form-item>
        </template>
        <template v-else-if="isGeneralRequestType">
          <template v-if="isAdminResourceType">
            <el-form-item label="资源名称" prop="resource_code">
              <el-select v-model="form.resource_code" placeholder="请选择资源">
                <el-option
                  v-for="item in resourceOptions"
                  :key="item.code"
                  :label="item.label"
                  :value="item.code"
                  :disabled="item.disabled"
                />
              </el-select>
            </el-form-item>
            <el-form-item v-if="needsGeneralTimeRange" label="开始时间" prop="start_at">
              <el-input v-model="form.start_at" placeholder="2026-04-16 09:00" />
            </el-form-item>
            <el-form-item v-if="needsGeneralTimeRange" label="结束时间" prop="end_at">
              <el-input v-model="form.end_at" placeholder="2026-04-16 18:00" />
            </el-form-item>
            <el-form-item v-if="needsGeneralQuantity" label="申请数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="申请说明" prop="reason">
              <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请说明" />
            </el-form-item>
          </template>
          <template v-else-if="isHrChangeType">
            <el-form-item label="申请标题" prop="resource_name">
              <el-input v-model="form.resource_name" :placeholder="generalPrimaryPlaceholder" />
            </el-form-item>
            <el-form-item v-if="form.leave_type === '调岗申请'" label="目标岗位" prop="target_position">
              <el-input v-model="form.target_position" placeholder="请输入目标岗位" />
            </el-form-item>
            <el-form-item label="生效日期" prop="effective_date">
              <el-input v-model="form.effective_date" placeholder="2026-05-01" />
            </el-form-item>
            <template v-if="form.leave_type === '薪酬异动'">
              <el-form-item label="当前薪资" prop="current_salary">
                <el-input v-model="form.current_salary" placeholder="如：12000" />
              </el-form-item>
              <el-form-item label="期望薪资" prop="expected_salary">
                <el-input v-model="form.expected_salary" placeholder="如：15000" />
              </el-form-item>
            </template>
            <el-form-item label="申请说明" prop="reason">
              <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请说明" />
            </el-form-item>
          </template>
          <template v-else-if="isOvertimeType">
            <el-form-item label="加班事项" prop="resource_name">
              <el-input v-model="form.resource_name" placeholder="如：项目上线支持" />
            </el-form-item>
            <el-form-item label="开始时间" prop="start_at">
              <el-input v-model="form.start_at" placeholder="2026-04-16 18:30" />
            </el-form-item>
            <el-form-item label="结束时间" prop="end_at">
              <el-input v-model="form.end_at" placeholder="2026-04-16 22:00" />
            </el-form-item>
            <el-form-item label="申请说明" prop="reason">
              <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入加班原因" />
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item :label="generalPrimaryLabel" prop="resource_name">
              <el-input v-model="form.resource_name" :placeholder="generalPrimaryPlaceholder" />
            </el-form-item>
            <el-form-item label="申请说明" prop="reason">
              <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请说明" />
            </el-form-item>
          </template>
        </template>
        <template v-else>
          <el-form-item label="起始时间" prop="start_at">
            <el-input v-model="form.start_at" placeholder="2026-04-16 09:00" />
          </el-form-item>
          <el-form-item label="结束时间" prop="end_at">
            <el-input v-model="form.end_at" placeholder="2026-04-17 18:00" />
          </el-form-item>
          <el-form-item label="请假天数" prop="days">
            <el-input-number v-model="form.days" :min="0" :step="0.5" style="width: 100%" />
          </el-form-item>
          <el-form-item label="申请说明" prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请原因" />
          </el-form-item>
        </template>
        <div class="apps-form-actions">
          <el-button @click="showCreateDialog = false" :disabled="submitting">取消</el-button>
          <el-button type="primary" :loading="submitting" :disabled="submitting" @click="submit">提交申请</el-button>
          <span v-if="supplementHint" class="apps-hint">{{ supplementHint }}</span>
        </div>
      </el-form>
    </el-dialog>

    <el-dialog v-model="showDetail" width="540px" :title="detailTitle">
      <div v-if="detailRow" class="apps-detail">
        <div class="apps-detail__grid">
          <div><span>申请类型</span><strong>{{ detailRow.leave_type }}</strong></div>
          <div><span>审批状态</span><strong>{{ detailRow.status }}</strong></div>
          <div><span>开始时间</span><strong>{{ detailRow.start_at || '—' }}</strong></div>
          <div><span>结束时间</span><strong>{{ detailRow.end_at || '—' }}</strong></div>
          <div><span>审批人</span><strong>{{ detailRow.approver || '待分配' }}</strong></div>
          <div><span>申请人</span><strong>{{ store.user?.name }}</strong></div>
          <div v-if="detailRow.item_name"><span>用品/资产名称</span><strong>{{ detailRow.item_name }}</strong></div>
          <div v-if="detailRow.quantity"><span>申请数量</span><strong>{{ detailRow.quantity }}</strong></div>
        </div>
        <div class="apps-detail__reason"><span>申请说明</span><p>{{ detailRow.reason || '无' }}</p></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute } from 'vue-router';

import PageCard from '@/components/PageCard.vue';
import {
  createAssetRequest,
  createGeneralRequest,
  createLeave,
  createOfficeSupplyRequest,
  getAdministrationSummary,
  getAssetRequests,
  getGeneralRequests,
  getLeaves,
  getOfficeSupplyRequests,
} from '@/api/modules';
import { useAppStore } from '@/stores/app';
import {
  countMonthlySupplementApplications,
  createSupplementApplication,
  findSupplementApplicationById,
  listSupplementApplications,
  toApplicationRow,
} from '@/utils/supplementApplications';

const store = useAppStore();
const route = useRoute();
const formRef = ref();
const loading = ref(false);
const submitting = ref(false);
const rows = ref([]);
const assetOptions = ref([]);
const showDetail = ref(false);
const showCreateDialog = ref(false);
const detailRow = ref(null);
const supplementCountValue = ref(0);
const applicationTypeOptions = [
  { label: '病假', value: '病假' },
  { label: '事假', value: '事假' },
  { label: '丧假', value: '丧假' },
  { label: '年假', value: '年假' },
  { label: '婚假', value: '婚假' },
  { label: '产假', value: '产假' },
  { label: '调休', value: '调休' },
  { label: '补卡申请', value: '补卡申请' },
  { label: '出差申请', value: '出差申请' },
  { label: '外出申请', value: '外出申请' },
  { label: '加班申请', value: '加班申请' },
  { label: '转正申请', value: '转正申请' },
  { label: '调岗申请', value: '调岗申请' },
  { label: '离职申请', value: '离职申请' },
  { label: '薪酬异动', value: '薪酬异动' },
  { label: '办公用品领用', value: '办公用品领用' },
  { label: '资产领用', value: '资产领用' },
  { label: '办公设备领用', value: '办公设备领用' },
  { label: '公章使用', value: '公章使用' },
  { label: '会议室申请', value: '会议室申请' },
  { label: '会议室预约', value: '会议室预约' },
  { label: '用车申请', value: '用车申请' },
];
const createDefaultForm = () => ({
  employee_no: store.user?.employeeNo || '',
  leave_type: '',
  start_at: '2026-04-16 09:00',
  end_at: '2026-04-17 18:00',
  days: 1,
  reason: '',
  item_name: '',
  asset_code: '',
  resource_name: '',
  resource_code: '',
  quantity: 1,
  needed_by: '',
  target_position: '',
  effective_date: '',
  current_salary: '',
  expected_salary: '',
});
const form = reactive(createDefaultForm());
const currentMonth = computed(() => String(form.start_at || '').slice(0, 7));
const supplementHint = computed(() => form.leave_type === '补卡申请' ? `本月已申请 ${supplementCountValue.value}/3 次补卡` : '');
const detailTitle = computed(() => detailRow.value ? `${detailRow.value.leave_type}详情` : '申请详情');
const isOfficeSupplyType = computed(() => form.leave_type === '办公用品领用');
const isAssetRequestType = computed(() => ['资产领用', '办公设备领用'].includes(form.leave_type));
const generalRequestTypes = ['公章使用', '会议室申请', '会议室预约', '用车申请', '转正申请', '调岗申请', '离职申请', '薪酬异动', '加班申请'];
const adminResourceTypes = ['公章使用', '会议室申请', '会议室预约', '用车申请'];
const hrChangeTypes = ['转正申请', '调岗申请', '离职申请', '薪酬异动'];
const isGeneralRequestType = computed(() => generalRequestTypes.includes(form.leave_type));
const isAdminResourceType = computed(() => adminResourceTypes.includes(form.leave_type));
const isHrChangeType = computed(() => hrChangeTypes.includes(form.leave_type));
const isOvertimeType = computed(() => form.leave_type === '加班申请');
const selectedAssetMeta = computed(() => assetOptions.value.find((item) => item.code === form.asset_code));
const selectedAssetAvailable = computed(() => selectedAssetMeta.value?.available || 0);
const resourceOptions = computed(() => {
  const typeMap = {
    公章使用: ['印章'],
    会议室申请: ['会议资源'],
    会议室预约: ['会议资源'],
    用车申请: ['车辆'],
  };
  const allow = typeMap[form.leave_type] || [];
  return assetOptions.value.filter((item) => allow.includes(item.type));
});
const generalPrimaryLabel = computed(() => ({
  公章使用: '印章名称',
  会议室申请: '会议室名称',
  会议室预约: '会议室名称',
  用车申请: '车辆名称',
  转正申请: '申请标题',
  调岗申请: '调岗目标',
  离职申请: '离职事项',
  薪酬异动: '异动事项',
  加班申请: '加班事项',
}[form.leave_type] || '申请标题'));
const generalPrimaryPlaceholder = computed(() => ({
  公章使用: '如：合同章',
  会议室申请: '如：会议室 A',
  会议室预约: '如：会议室 B',
  用车申请: '如：商务用车',
  转正申请: '如：试用期满转正申请',
  调岗申请: '如：招商主管 → 区域招商主管',
  离职申请: '如：个人原因离职申请',
  薪酬异动: '如：岗位晋升调薪申请',
  加班申请: '如：项目上线加班',
}[form.leave_type] || '请输入申请标题'));
const needsGeneralTimeRange = computed(() => ['会议室申请', '会议室预约', '用车申请', '加班申请'].includes(form.leave_type));
const needsGeneralQuantity = computed(() => ['公章使用'].includes(form.leave_type));
const rules = computed(() => {
  if (isOfficeSupplyType.value) {
    return {
      leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
      item_name: [{ required: true, message: '请输入用品名称', trigger: 'blur' }],
      quantity: [{ required: true, message: '请输入申请数量', trigger: 'change' }],
      reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }],
    };
  }
  if (isAssetRequestType.value) {
    return {
      leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
      asset_code: [{ required: true, message: '请选择资产', trigger: 'change' }],
      quantity: [{ required: true, message: '请输入申请数量', trigger: 'change' }],
      reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }],
    };
  }
  if (isGeneralRequestType.value) {
    return {
      leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
      ...(isAdminResourceType.value
        ? { resource_code: [{ required: true, message: '请选择资源', trigger: 'change' }] }
        : { resource_name: [{ required: true, message: `请输入${generalPrimaryLabel.value}`, trigger: 'blur' }] }),
      ...(needsGeneralTimeRange.value ? {
        start_at: [{ required: true, message: '请输入开始时间', trigger: 'blur' }],
        end_at: [{ required: true, message: '请输入结束时间', trigger: 'blur' }],
      } : {}),
      ...(form.leave_type === '调岗申请' ? { target_position: [{ required: true, message: '请输入目标岗位', trigger: 'blur' }] } : {}),
      ...(form.leave_type === '薪酬异动' ? {
        current_salary: [{ required: true, message: '请输入当前薪资', trigger: 'blur' }],
        expected_salary: [{ required: true, message: '请输入期望薪资', trigger: 'blur' }],
      } : {}),
      ...(isHrChangeType.value ? { effective_date: [{ required: true, message: '请输入生效日期', trigger: 'blur' }] } : {}),
      reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }],
    };
  }
  return {
    leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }],
    start_at: [{ required: true, message: '请输入开始时间', trigger: 'blur' }],
    end_at: [{ required: true, message: '请输入结束时间', trigger: 'blur' }],
    reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }],
  };
});

const resetForm = () => {
  Object.assign(form, createDefaultForm());
  formRef.value?.clearValidate?.();
};

const refreshSupplementMeta = async () => {
  supplementCountValue.value = await countMonthlySupplementApplications(store.user?.employeeNo || '', currentMonth.value);
};

const refreshAssetOptions = async () => {
  const result = await getAdministrationSummary();
  assetOptions.value = (result.data?.records || []).map((item) => {
    const available = (item.details || []).filter((detail) => ['闲置', '库存', '可用'].includes(detail.status)).length;
    return {
      code: item.code,
      name: item.name,
      type: item.type,
      total: item.total || 0,
      available,
      disabled: available <= 0,
      label: `${item.name}（${item.type}｜可用 ${available}/${item.total || 0}）`,
    };
  });
};

const loadHistoryRows = async () => {
  const [leaveResult, supplementRows, officeSupplyResult, assetRequestResult, generalRequestResult] = await Promise.all([
    getLeaves(),
    listSupplementApplications(store.user?.employeeNo || ''),
    getOfficeSupplyRequests(),
    getAssetRequests(),
    getGeneralRequests(),
  ]);
  const leaveRows = (leaveResult.data || []).map((item) => ({ ...item, kind: 'leave' }));
  const officeSupplyRows = (officeSupplyResult.data || []).map((item) => ({
    ...item,
    leave_type: '办公用品领用',
    start_at: item.needed_by || item.start_at || '',
    end_at: item.needed_by || item.end_at || '',
    approver: item.approver || '于浩',
  }));
  const assetRequestRows = (assetRequestResult.data || []).map((item) => ({
    ...item,
    leave_type: item.request_type || item.leave_type || item.type,
    start_at: item.needed_by || item.start_at || '',
    end_at: item.needed_by || item.end_at || '',
    approver: item.approver || '于浩',
    item_name: item.asset_name,
  }));
  const generalRequestRows = (generalRequestResult.data || []).map((item) => ({
    ...item,
    leave_type: item.request_type || item.leave_type || item.type,
    start_at: item.start_at || item.needed_by || '',
    end_at: item.end_at || '',
    approver: item.approver || '于浩',
    item_name: item.resource_name || item.title,
    quantity: item.quantity,
  }));
  rows.value = [...generalRequestRows, ...assetRequestRows, ...officeSupplyRows, ...supplementRows.map(toApplicationRow), ...leaveRows]
    .sort((a, b) => String(b.start_at || b.created_at || '').localeCompare(String(a.start_at || a.created_at || '')));
};

const loadData = async () => {
  loading.value = true;
  try {
    await loadHistoryRows();
    await refreshSupplementMeta();
  } finally {
    loading.value = false;
  }
};

const formatPeriod = (row) => {
  if (row.leave_type === '办公用品领用') return row.start_at || '尽快';
  return `${row.start_at || '—'} ~ ${row.end_at || '—'}`;
};

const submit = async () => {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await formRef.value.validate();
    form.employee_no = store.user?.employeeNo || '';
    if (form.leave_type === '办公用品领用') {
      await createOfficeSupplyRequest({
        employee_no: store.user?.employeeNo || '',
        item_name: form.item_name,
        quantity: form.quantity,
        needed_by: form.needed_by,
        reason: form.reason,
      });
      ElMessage.success('办公用品领用申请已提交');
    } else if (isAssetRequestType.value) {
      const selected = selectedAssetMeta.value;
      await createAssetRequest({
        employee_no: store.user?.employeeNo || '',
        request_type: form.leave_type,
        asset_code: form.asset_code,
        asset_name: selected?.name || '',
        quantity: form.quantity,
        needed_by: form.needed_by,
        reason: form.reason,
      });
      ElMessage.success(`${form.leave_type}已提交`);
    } else if (isGeneralRequestType.value) {
      const selectedResource = resourceOptions.value.find((item) => item.code === form.resource_code);
      await createGeneralRequest({
        employee_no: store.user?.employeeNo || '',
        request_type: form.leave_type,
        title: isAdminResourceType.value ? (selectedResource?.name || '') : form.resource_name,
        resource_code: form.resource_code,
        resource_name: isAdminResourceType.value ? (selectedResource?.name || '') : form.resource_name,
        quantity: form.quantity,
        start_at: form.start_at,
        end_at: form.end_at,
        needed_by: form.needed_by,
        reason: form.reason,
        meta: {
          目标岗位: form.target_position,
          生效日期: form.effective_date,
          当前薪资: form.current_salary,
          期望薪资: form.expected_salary,
        },
      });
      ElMessage.success(`${form.leave_type}已提交`);
    } else if (form.leave_type === '补卡申请') {
      if (supplementCountValue.value >= 3) return ElMessage.warning('每月最多只能申请 3 次补卡');
      await createSupplementApplication({
        employeeNo: store.user?.employeeNo || '',
        date: String(form.start_at).slice(0, 10),
        time: String(form.start_at).slice(11, 16),
        reason: form.reason,
      });
      ElMessage.success('补卡申请已提交，并已同步审批中心');
    } else {
      await createLeave(form);
      ElMessage.success('申请已提交');
    }
    showCreateDialog.value = false;
    resetForm();
    await Promise.all([loadHistoryRows(), refreshSupplementMeta()]);
  } finally {
    submitting.value = false;
  }
};

const openDetail = (row) => {
  detailRow.value = row;
  showDetail.value = true;
};

const openCreateDialog = async () => {
  resetForm();
  await Promise.all([refreshSupplementMeta(), refreshAssetOptions()]);
  showCreateDialog.value = true;
};

const openMockDetail = () => {
  const type = String(route.query.type || '');
  const date = String(route.query.date || '');
  if (!type || !date) return;
  openDetail({
    id: String(route.query.applicationId || ''),
    leave_type: type,
    start_at: `${date} ${String(route.query.time || '09:00')}`,
    end_at: `${date} ${String(route.query.endTime || route.query.time || '18:00')}`,
    status: String(route.query.status || '待审批'),
    approver: String(route.query.approver || '直属经理'),
    reason: String(route.query.reason || '无'),
  });
};

const applyRouteAction = async () => {
  const action = String(route.query.action || '');
  const date = String(route.query.date || '');
  const time = String(route.query.time || '09:00');
  const reason = String(route.query.reason || '');
  const applicationId = String(route.query.applicationId || '');
  if (action === 'supplement' && date) {
    resetForm();
    form.leave_type = '补卡申请';
    form.start_at = `${date} ${time}`;
    form.end_at = `${date} ${time}`;
    form.days = 0;
    form.reason = reason || '补充当日漏打卡说明';
    await refreshSupplementMeta();
    showCreateDialog.value = true;
  }
  if (action === 'detail') {
    const supplement = applicationId ? await findSupplementApplicationById(applicationId) : null;
    if (supplement) openDetail(toApplicationRow(supplement));
    else openMockDetail();
  }
};

onMounted(async () => {
  await loadData();
  await applyRouteAction();
});
</script>

<style scoped>
.applications-page {
  display: grid;
  gap: 16px;
}

.applications-card :deep(.page-card__body) {
  display: grid;
  gap: 16px;
}

.applications-history {
  display: grid;
  gap: 14px;
}

.applications-form {
  display: grid;
  gap: 4px;
}

.apps-form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.apps-hint {
  color: var(--hr-info);
  font-size: 12px;
}

.apps-type-tip {
  margin: -4px 0 8px;
  color: var(--hr-info);
  font-size: 12px;
  line-height: 1.6;
}

.apps-asset-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: -4px 0 8px;
  color: var(--hr-info);
  font-size: 12px;
}

.apps-detail {
  display: grid;
  gap: 16px;
}

.apps-detail__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.apps-detail__grid div,
.apps-detail__reason {
  padding: 12px 14px;
  border-radius: 16px;
  background: #f8fbff;
}

.apps-detail span {
  display: block;
  color: var(--hr-info);
  font-size: 12px;
  margin-bottom: 6px;
}

.apps-detail strong,
.apps-detail p {
  color: var(--hr-title);
  margin: 0;
}
</style>
