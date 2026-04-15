<template>
  <div class="page-grid">
    <PageCard title="申请中心" description="提交请假、加班、出差、领用等申请。">
      <div class="two-column apps-layout">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="申请类型" prop="leave_type">
            <el-select v-model="form.leave_type" placeholder="请选择申请类型">
              <el-option label="病假" value="病假" />
              <el-option label="事假" value="事假" />
              <el-option label="婚假" value="婚假" />
              <el-option label="调休" value="调休" />
              <el-option label="补卡申请" value="补卡申请" />
            </el-select>
          </el-form-item>
          <el-form-item label="起始时间" prop="start_at"><el-input v-model="form.start_at" placeholder="2026-04-16 09:00" /></el-form-item>
          <el-form-item label="结束时间" prop="end_at"><el-input v-model="form.end_at" placeholder="2026-04-17 18:00" /></el-form-item>
          <el-form-item label="请假天数" prop="days"><el-input-number v-model="form.days" :min="0" :step="0.5" style="width: 100%" /></el-form-item>
          <el-form-item label="申请说明" prop="reason"><el-input v-model="form.reason" type="textarea" :rows="5" placeholder="请输入申请原因" /></el-form-item>
          <div class="apps-form-actions"><el-button type="primary" @click="submit">提交申请</el-button><span v-if="supplementHint" class="apps-hint">{{ supplementHint }}</span></div>
        </el-form>

        <el-table :data="rows" width="100%" v-loading="loading">
          <el-table-column prop="leave_type" label="类型" min-width="120" />
          <el-table-column label="时间" min-width="180"><template #default="scope">{{ scope.row.start_at }} ~ {{ scope.row.end_at }}</template></el-table-column>
          <el-table-column prop="status" label="状态" min-width="120" />
          <el-table-column prop="approver" label="审批人" min-width="120" />
          <el-table-column label="操作" min-width="120"><template #default="scope"><el-button link type="primary" @click="openDetail(scope.row)">查看详情</el-button></template></el-table-column>
        </el-table>
      </div>
    </PageCard>

    <el-dialog v-model="showDetail" width="540px" :title="detailTitle">
      <div v-if="detailRow" class="apps-detail">
        <div class="apps-detail__grid">
          <div><span>申请类型</span><strong>{{ detailRow.leave_type }}</strong></div>
          <div><span>审批状态</span><strong>{{ detailRow.status }}</strong></div>
          <div><span>开始时间</span><strong>{{ detailRow.start_at }}</strong></div>
          <div><span>结束时间</span><strong>{{ detailRow.end_at }}</strong></div>
          <div><span>审批人</span><strong>{{ detailRow.approver || '待分配' }}</strong></div>
          <div><span>申请人</span><strong>{{ store.user?.name }}</strong></div>
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
import { createLeave, getLeaves } from '@/api/modules';
import { useAppStore } from '@/stores/app';
import { countMonthlySupplementApplications, createSupplementApplication, findSupplementApplicationById, listSupplementApplications, toApplicationRow } from '@/utils/supplementApplications';

const store = useAppStore();
const route = useRoute();
const formRef = ref();
const loading = ref(false);
const rows = ref([]);
const showDetail = ref(false);
const detailRow = ref(null);
const supplementCountValue = ref(0);
const form = reactive({ employee_no: store.user?.employeeNo || '', leave_type: '', start_at: '2026-04-16 09:00', end_at: '2026-04-17 18:00', days: 1, reason: '' });
const currentMonth = computed(() => String(form.start_at || '').slice(0, 7));
const supplementHint = computed(() => form.leave_type === '补卡申请' ? `本月已申请 ${supplementCountValue.value}/3 次补卡` : '');
const detailTitle = computed(() => detailRow.value ? `${detailRow.value.leave_type}详情` : '申请详情');
const rules = { leave_type: [{ required: true, message: '请选择申请类型', trigger: 'change' }], start_at: [{ required: true, message: '请输入开始时间', trigger: 'blur' }], end_at: [{ required: true, message: '请输入结束时间', trigger: 'blur' }], reason: [{ required: true, message: '请输入申请说明', trigger: 'blur' }] };

const refreshSupplementMeta = async () => {
  supplementCountValue.value = await countMonthlySupplementApplications(store.user?.employeeNo || '', currentMonth.value);
};

const loadData = async () => {
  loading.value = true;
  try {
    const [leaveResult, supplementRows] = await Promise.all([
      getLeaves(),
      listSupplementApplications(store.user?.employeeNo || ''),
    ]);
    const leaveRows = (leaveResult.data || []).map((item) => ({ ...item, kind: 'leave' }));
    rows.value = [...supplementRows.map(toApplicationRow), ...leaveRows];
    await refreshSupplementMeta();
  } finally { loading.value = false; }
};

const submit = async () => {
  await formRef.value.validate();
  form.employee_no = store.user?.employeeNo || '';
  if (form.leave_type === '补卡申请') {
    if (supplementCountValue.value >= 3) return ElMessage.warning('每月最多只能申请 3 次补卡');
    await createSupplementApplication({ employeeNo: store.user?.employeeNo || '', date: String(form.start_at).slice(0, 10), time: String(form.start_at).slice(11, 16), reason: form.reason });
    ElMessage.success('补卡申请已提交，并已同步审批中心');
    return loadData();
  }
  await createLeave(form);
  ElMessage.success('申请已提交');
  await loadData();
};

const openDetail = (row) => { detailRow.value = row; showDetail.value = true; };

const openMockDetail = () => {
  const type = String(route.query.type || '');
  const date = String(route.query.date || '');
  if (!type || !date) return;
  openDetail({ id: String(route.query.applicationId || ''), leave_type: type, start_at: `${date} ${String(route.query.time || '09:00')}`, end_at: `${date} ${String(route.query.endTime || route.query.time || '18:00')}`, status: String(route.query.status || '待审批'), approver: String(route.query.approver || '直属经理'), reason: String(route.query.reason || '无') });
};

const applyRouteAction = async () => {
  const action = String(route.query.action || '');
  const date = String(route.query.date || '');
  const time = String(route.query.time || '09:00');
  const reason = String(route.query.reason || '');
  const applicationId = String(route.query.applicationId || '');
  if (action === 'supplement' && date) {
    form.leave_type = '补卡申请';
    form.start_at = `${date} ${time}`;
    form.end_at = `${date} ${time}`;
    form.days = 0;
    form.reason = reason || '补充当日漏打卡说明';
    await refreshSupplementMeta();
  }
  if (action === 'detail') {
    const supplement = applicationId ? await findSupplementApplicationById(applicationId) : null;
    if (supplement) openDetail(toApplicationRow(supplement));
    else openMockDetail();
  }
};

onMounted(async () => { await loadData(); await applyRouteAction(); });
</script>

<style scoped>
.apps-layout{align-items:start}.apps-form-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.apps-hint{color:var(--hr-info);font-size:12px}.apps-detail{display:grid;gap:16px}.apps-detail__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.apps-detail__grid div,.apps-detail__reason{padding:12px 14px;border-radius:16px;background:#f8fbff}.apps-detail span{display:block;color:var(--hr-info);font-size:12px;margin-bottom:6px}.apps-detail strong,.apps-detail p{color:var(--hr-title);margin:0}
</style>
