<template>
  <div class="ap">
    <section class="mg">
      <article v-for="card in cards" :key="card.t" :class="['mc', `is-${card.c}`]">
        <div class="mi">{{ card.i }}</div>
        <div><p>{{ card.t }}</p><strong>{{ card.v }}</strong><span>{{ card.d }}</span></div>
      </article>
    </section>

    <section class="sh">
      <div class="cal page-section">
        <div class="ctl">
          <div class="bar bar--center">
            <div class="nav"><el-button text @click="changeMonth(-1)">‹ 上月</el-button><strong>{{ title }}</strong><el-button text @click="changeMonth(1)">下月 ›</el-button></div>
          </div>
        </div>

        <div class="wk"><span v-for="d in weekdays" :key="d">{{ d }}</span></div>

        <div class="gd">
          <button v-for="day in days" :key="day.key" type="button" :class="['dy', day.current ? '' : 'm', day.weekend ? 'w' : '', day.today ? 't' : '', day.selected ? 's' : '']" @click="pick(day.date)">
            <div class="dh"><span class="dn">{{ day.num }}</span><span class="dd">{{ day.note }}</span></div>
            <div class="dt">
              <template v-if="day.records.length">
                <span v-for="r in day.records.slice(0, 2)" :key="`${day.key}-${r.id}`" :class="['pill', `is-${tone(r.status)}`]">{{ label(r) }}</span>
                <span v-if="day.records.length > 2" class="pill is-more">+{{ day.records.length - 2 }}</span>
              </template>
              <span v-if="day.supplement" class="pill is-supplement">已补卡</span>
            </div>
          </button>
        </div>
      </div>
    </section>

    <el-dialog v-model="showDetail" width="620px" :title="selectedTitle" class="detail-dialog">
      <div class="pop-head"><span class="pop-note">{{ selectedRows.length ? '当日打卡详情与关联申请' : '该日期暂无打卡记录' }}</span></div>
      <el-table :data="detailRows" width="100%" empty-text="暂无打卡记录">
        <el-table-column prop="type" label="类型" min-width="90" />
        <el-table-column prop="checkIn" label="上班打卡" min-width="100" />
        <el-table-column prop="checkOut" label="下班打卡" min-width="100" />
        <el-table-column prop="status" label="状态" min-width="90"><template #default="s"><span :class="['pill', `is-${tone(s.row.status)}`]">{{ s.row.status }}</span></template></el-table-column>
        <el-table-column label="操作" min-width="120">
          <template #default="s">
            <el-button v-if="hasApplication(s.row)" link type="primary" @click="openRowApplicationDetail(s.row)">查看申请详情</el-button>
            <el-button v-else-if="canApplyRowSupplement(s.row)" link type="primary" @click="goApplySupplement(s.row)">申请补卡</el-button>
            <span v-else-if="s.row.status.includes('缺卡') && supplementCount >= 3" class="op-tip">补卡已达上限</span>
            <span v-else class="op-tip">—</span>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="selectedRows.length" class="remarks"><div v-for="row in selectedRows" :key="row.id" class="remark-item"><strong>{{ row.type }}</strong><span>{{ row.remark || '无备注' }}</span></div></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAppStore } from '@/stores/app';
import { countMonthlySupplementApplications, findSupplementApplicationByDate, listSupplementApplications } from '@/utils/supplementApplications';

const store = useAppStore();
const router = useRouter();
const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
const month = ref(new Date().toISOString().slice(0, 7));
const loading = ref(false);
const selectedDate = ref('');
const showDetail = ref(false);
const supplementCount = ref(0);
const supplementMap = ref({});

const userNo = computed(() => String(store.user?.employeeNo || 'EMP-1024').trim());
const userName = computed(() => store.user?.name || '陈晓雨');
const userDept = computed(() => store.user?.department || '市场部');
const monthDate = computed(() => new Date(`${month.value}-01T00:00:00`));
const title = computed(() => `${monthDate.value.getFullYear()}年${String(monthDate.value.getMonth() + 1).padStart(2, '0')}月`);
const monthRows = computed(() => buildMockAttendance(userNo.value, userName.value, userDept.value, month.value));
const byDate = computed(() => monthRows.value.reduce((m, i) => ((m[i.date] ||= []).push(i), m), {}));
const selectedRows = computed(() => byDate.value[selectedDate.value] || []);
const detailRows = computed(() => selectedRows.value);
const selectedTitle = computed(() => selectedDate.value ? `${selectedDate.value} 打卡详情` : '打卡详情');
const summary = computed(() => ({ attendance: new Set(monthRows.value.map((i) => i.date)).size, missing: monthRows.value.filter((i) => i.status.includes('缺卡')).length, late: monthRows.value.filter((i) => i.status.includes('迟到')).length, early: monthRows.value.filter((i) => i.status.includes('早退')).length, overtime: monthRows.value.reduce((s, i) => s + Number(i.overtimeHours || 0), 0), leave: monthRows.value.filter((i) => i.status.includes('请假')).length }));
const cards = computed(() => [
  { t: '出勤天数', v: `${summary.value.attendance}天`, d: '本月已记录出勤日', i: '勤', c: 'green' },
  { t: '缺卡', v: String(summary.value.missing), d: '需补卡/说明', i: '卡', c: 'amber' },
  { t: '迟到', v: String(summary.value.late), d: '当月迟到次数', i: '迟', c: 'orange' },
  { t: '早退', v: String(summary.value.early), d: '当月早退次数', i: '退', c: 'yellow' },
  { t: '加班', v: `${summary.value.overtime}h`, d: '累计加班时长', i: '班', c: 'cyan' },
  { t: '请假', v: String(summary.value.leave), d: '本月请假次数', i: '假', c: 'blue' },
]);
const days = computed(() => {
  const first = new Date(monthDate.value); const start = new Date(first); start.setDate(first.getDate() - first.getDay());
  return Array.from({ length: 42 }, (_, idx) => {
    const d = new Date(start); d.setDate(start.getDate() + idx); const date = fmt(d); const records = byDate.value[date] || [];
    return { key: date, date, num: d.getDate(), records, supplement: supplementMap.value[date], current: date.startsWith(month.value), weekend: d.getDay() === 0 || d.getDay() === 6, today: date === fmt(new Date()), selected: date === selectedDate.value, note: records.some((i) => i.status.includes('请假')) ? '请假' : ((d.getDay() === 0 || d.getDay() === 6) ? '休息' : '工作日') };
  });
});

function fmt(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function buildMockAttendance(employeeNo,name,department,monthValue){const start=new Date(`${monthValue}-01T00:00:00`),total=new Date(start.getFullYear(),start.getMonth()+1,0).getDate(),leaveDays=new Set([7,24]),lateDays=new Set([3,15]),earlyDays=new Set([11]),missingDays=new Set([9,18,21,30]),overtimeDays=new Set([8,22,29]),tripDays=new Set([13]),rows=[];for(let day=1;day<=total;day+=1){const current=new Date(start.getFullYear(),start.getMonth(),day),week=current.getDay();if(week===0||week===6)continue;const date=fmt(current);let status='正常',type='工作日',checkIn='08:56',checkOut='18:08',overtimeHours=0,remark='正常出勤';if(leaveDays.has(day)){status='请假';type='年假';checkIn='—';checkOut='—';remark='已提交并审批通过';}else if(lateDays.has(day)){status='迟到';checkIn=day===15?'09:18':'09:12';remark='通勤高峰延误';}else if(earlyDays.has(day)){status='早退';checkOut='17:36';remark='外出客户拜访后未回司';}else if(missingDays.has(day)){status='缺卡';checkOut='—';remark=day===9?'外出返程遗漏签退':day===21?'午后外出后忘记补签':day===30?'月末加班后漏打卡':'下班忘记打卡';}else if(overtimeDays.has(day)){status='加班';checkOut=day===29?'21:06':'20:18';overtimeHours=day===29?3:2;remark='项目节点加班';}else if(tripDays.has(day)){status='外勤';checkIn='09:01';checkOut='18:12';remark='客户现场拜访';}rows.push({id:`${monthValue}-${day}`,employeeNo,name,department,month:monthValue,date,type,checkIn,checkOut,status,overtimeHours,remark});}return rows;}
function tone(s=''){if(s.includes('旷工')||s.includes('异常'))return 'danger';if(s.includes('迟到'))return 'late';if(s.includes('早退'))return 'early';if(s.includes('加班'))return 'overtime';if(s.includes('请假'))return 'leave';if(s.includes('缺卡'))return 'warning';return 'success';}
function label(r){return r.status==='加班'?`加班 ${Number(r.overtimeHours||0)}h`:r.status;}
function hasApplication(row){return Boolean(row.status.includes('请假')||row.status.includes('加班')||supplementMap.value[row.date]);}
function canApplyRowSupplement(row){return row.status.includes('缺卡')&&!supplementMap.value[row.date]&&supplementCount.value<3;}
function openRowApplicationDetail(row){if(row.status.includes('请假')){showDetail.value=false;router.push({path:'/employee/applications',query:{action:'detail',type:row.type,date:row.date,time:'09:00',endTime:'18:00',status:'已通过',approver:'直属经理',reason:row.remark||'年假申请已审批通过'}});return;}if(row.status.includes('加班')){showDetail.value=false;router.push({path:'/employee/applications',query:{action:'detail',type:'加班申请',date:row.date,time:row.checkOut,endTime:row.checkOut,status:'已通过',approver:'直属经理',reason:row.remark||'加班申请已审批通过'}});return;}const supplement=supplementMap.value[row.date];if(supplement){showDetail.value=false;router.push({path:'/employee/applications',query:{action:'detail',applicationId:supplement.id}});}}
function pick(date){selectedDate.value=date;showDetail.value=true;}
function changeMonth(step){const d=new Date(monthDate.value);d.setMonth(d.getMonth()+step);month.value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;}
function ensureSelected(){const today=fmt(new Date());selectedDate.value=today.startsWith(month.value)?today:`${month.value}-01`;}
async function loadData(){loading.value=true;try{ensureSelected();const items=await listSupplementApplications(userNo.value);supplementMap.value=Object.fromEntries(items.map((item)=>[item.date,item]));supplementCount.value=await countMonthlySupplementApplications(userNo.value,month.value);}finally{loading.value=false;}}
function goApplySupplement(row){const targetRow=row||selectedRows.value.find((item)=>item.status.includes('缺卡'));if(!targetRow)return;if(supplementCount.value>=3){ElMessage.warning('每月最多只能申请 3 次补卡');return;}const time=targetRow?.checkIn&&targetRow.checkIn!=='—'?targetRow.checkIn:'18:00';showDetail.value=false;router.push({path:'/employee/applications',query:{action:'supplement',date:targetRow.date,time,reason:targetRow?.remark||'因遗漏打卡，申请补卡'}});}
watch(month,()=>{loadData();showDetail.value=false;},{immediate:true});
onMounted(loadData);
</script>

<style scoped>
.ap{display:grid;gap:12px;height:calc(100vh - 148px);grid-template-rows:auto minmax(0,1fr);overflow:hidden}.mg{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}.mc,.cal{border-radius:24px;box-shadow:0 16px 40px rgba(31,42,68,.06)}.mc{display:flex;align-items:center;gap:12px;padding:14px 16px;background:linear-gradient(180deg,#fff 0%,#f7fbff 100%);border:1px solid rgba(64,158,255,.08);min-height:92px}.mi{width:40px;height:40px;border-radius:14px;display:grid;place-items:center;color:#fff;font-weight:700}.mc p{margin:0 0 4px;color:var(--hr-info);font-size:12px}.mc strong{display:block;color:var(--hr-title);font-size:22px;line-height:1}.mc span{display:block;margin-top:4px;color:#8c9bb1;font-size:11px}.is-green .mi{background:linear-gradient(135deg,#2ecf8f,#13b77d)}.is-amber .mi{background:linear-gradient(135deg,#ffb648,#f59e0b)}.is-orange .mi{background:linear-gradient(135deg,#ff8b5d,#ff6a3d)}.is-yellow .mi{background:linear-gradient(135deg,#ffc94d,#f6b100)}.is-cyan .mi{background:linear-gradient(135deg,#3ecfcd,#13b4c8)}.is-blue .mi{background:linear-gradient(135deg,#4c8dff,#2f6cff)}.sh{min-height:0;overflow:hidden}.cal{height:100%;padding:16px;overflow:hidden;display:grid;grid-template-rows:auto auto minmax(0,1fr);gap:12px}.ctl{display:grid;grid-template-columns:1fr;align-items:center;gap:10px}.bar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.bar--center{justify-content:center}.nav{display:flex;align-items:center;gap:8px}.nav strong{min-width:110px;text-align:center;color:var(--hr-title);font-size:15px}.wk,.gd{display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}.wk{gap:8px}.wk span{background:#f8f9fa;border-radius:12px;text-align:center;padding:8px 0;color:#7d8aa5;font-weight:600;font-size:12px}.gd{gap:8px;align-content:stretch;grid-template-rows:repeat(6,minmax(0,1fr))}.dy{border:1px solid #edf1f7;border-radius:16px;background:#fff;padding:10px;text-align:left;display:grid;grid-template-rows:auto minmax(0,1fr);gap:8px;min-height:0}.dh{display:flex;align-items:center;justify-content:space-between;gap:8px}.dn{color:var(--hr-title);font-weight:700;font-size:14px}.dd{color:#b0b9ca;font-size:11px}.dt{display:flex;flex-direction:column;align-items:flex-start;gap:4px;overflow:hidden}.dy.m{background:#fafbfd}.dy.w .dn,.dy.w .dd,.dy.m .dn{color:#b7bfce}.dy.t{border-color:rgba(64,158,255,.25)}.dy.s{border-color:#409eff;box-shadow:0 10px 20px rgba(64,158,255,.12)}.pill{display:inline-flex;align-items:center;justify-content:center;min-height:20px;padding:0 8px;border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap}.pill.is-success{color:#12b76a;background:rgba(18,183,106,.12)}.pill.is-warning{color:#f59e0b;background:rgba(245,158,11,.14)}.pill.is-late{color:#ff8b5d;background:rgba(255,139,93,.14)}.pill.is-early{color:#ffb648;background:rgba(255,182,72,.14)}.pill.is-danger{color:#e34d59;background:rgba(227,77,89,.14)}.pill.is-overtime{color:#7c3aed;background:rgba(124,58,237,.12)}.pill.is-leave{color:#2f6cff;background:rgba(47,108,255,.12)}.pill.is-more{color:#7d8aa5;background:#f3f6fb}.pill.is-supplement{color:#3378ff;background:rgba(51,120,255,.14)}.pop-head{margin-bottom:10px;text-align:center}.pop-note{color:var(--hr-info);font-size:12px;display:inline-block}.remarks{display:grid;gap:8px;margin-top:14px}.remark-item{display:grid;gap:2px;padding:10px 12px;border-radius:14px;background:#f8fbff;text-align:center}.remark-item strong{font-size:12px;color:var(--hr-title)}.remark-item span{font-size:12px;color:var(--hr-info)}.op-tip{color:#b0b9ca;font-size:12px}.detail-dialog :deep(.el-dialog__header){text-align:center}.detail-dialog :deep(.el-table th.el-table__cell),.detail-dialog :deep(.el-table td.el-table__cell){text-align:center}.detail-dialog :deep(.cell){justify-content:center;text-align:center}.detail-dialog :deep(.el-table th.el-table__cell){background:#f8f9fa}@media (max-width:1360px){.mg{grid-template-columns:repeat(3,minmax(0,1fr))}}@media (max-width:1024px){.ap{height:auto;overflow:visible}.sh,.cal{overflow:visible;height:auto}}@media (max-width:767px){.mg{grid-template-columns:repeat(2,minmax(0,1fr))}.gd{gap:6px;grid-template-rows:none}.dy{padding:8px;min-height:78px}}
</style>