import { adminAssetsRows, approvalRows, attendanceRows, employeeRows, performanceRows } from '@/mock/data';
import { applyApprovedAssetSyncs } from '@/utils/assetApprovalSync';

const K='hr-dev-lite';
const c=(v)=>JSON.parse(JSON.stringify(v));
const p=(u='')=>String(u).replace(/^https?:\/\/[^/]+/i,'').replace(/^\/api\/v1/,'');
const on=()=>import.meta.env.DEV&&import.meta.env.VITE_FORCE_REMOTE_API!=='true';
const ok=(data,message='操作成功')=>({code:0,message,data});
const gid=(x)=>`${x}-${Date.now()}-${Math.random().toString(36).slice(2,6)}`;
const q=(cfg,k)=>cfg?.params?.[k];
const n=(v,d=0)=>Number.isFinite(Number(v))?Number(v):d;

const emp=()=>employeeRows.map((e,i)=>({id:e.employeeNo,employee_no:e.employeeNo,name:e.name,department:e.department,position:e.position,role:e.department==='综合管理部'?'hr':'employee',status:e.status,salary_base:e.department==='产品技术部'?12000:9800,performance_base:e.department==='销售部'?2400:1800,hire_date:`2025-${String((i%9)+1).padStart(2,'0')}-15`,resignation_date:e.status==='离职'?'2026-03-31':'',id_card_no:`31010119900101${String(1000+i)}`,phone:`1380000${String(1000+i).slice(-4)}`,email:`${e.employeeNo.toLowerCase()}@yuhohr.local`,probation_end_date:'2025-04-15',emergency_contact:'家属联系人',emergency_contact_phone:`1390000${String(2000+i).slice(-4)}`,political_status:i%3===0?'中共党员':'群众',gender:i%2?'男':'女',birth_date:'1995-01-01',registered_address:'示例户籍地址',current_address:'示例居住地址',ethnicity:'汉族',education:'本科',graduate_school:'示例大学',major:'示例专业',contract_type:'固定期限劳动合同',contract_sign_date:'2025-01-01',contract_end_date:'2027-12-31',social_security_base:6200,housing_fund_base:3200,bank_account:`622200000000${String(1000+i).padStart(4,'0')}`,bank_name:'招商银行',job_level:'P3',report_to:'部门负责人',work_location:'总部办公区',id_card_attachments:[],education_certificate_attachments:[],labor_contract_attachments:[],medical_report_attachments:[]}));
const coef=(g='B')=>({S:1.5,A:1.2,B:1,C:0.8,D:0.5}[g]||1);
const perf=(es)=>es.filter(e=>e.status!=='离职').slice(0,12).map((e,i)=>{const r=performanceRows[i%performanceRows.length]||{};const g=(({'A+':'S','B+':'A','C+':'C'}[r.grade]||r.grade||'B')+'').replace('+','');const s=n(r.score,85);return{id:`PERF-${i+1}`,employeeNo:e.employee_no,name:e.name,department:e.department,position:e.position,cycleType:'月度',assessmentYear:2026,assessmentMonth:4,performanceScore:s,attitudeScore:84,abilityScore:86,totalScore:s,grade:g,coefficient:coef(g),status:r.status||'待复核',reviewer:r.reviewer||'于浩',selfReview:`${e.name} 本月表现稳定。`,managerReview:`${e.name} 完成度较好。`,remark:'开发态数据',indicators:[{name:'工作达成率',weight:100,targetValue:'100%',actualValue:'95%',completionRate:95,score:s}]};});
const att=(es)=>es.filter(e=>e.status!=='离职').slice(0,18).flatMap((e,i)=>['2026-04-01','2026-04-02','2026-04-03'].map((d,j)=>{const s=attendanceRows[(i+j)%attendanceRows.length];return{id:`${e.employee_no}-${d}`,employeeNo:e.employee_no,name:e.name,department:e.department,date:d,month:d.slice(0,7),shouldAttendance:1,actualAttendance:/请假|旷工/.test(s.status)?0:1,checkIn:s.checkIn==='—'?'':s.checkIn,checkOut:s.checkOut==='—'?'':s.checkOut,status:s.status,lateMinutes:s.status.includes('迟到')?12:0,earlyMinutes:s.status.includes('早退')?8:0,absenteeismDays:s.status.includes('旷工')?1:0,missingCardCount:s.status.includes('缺卡')?1:0,leaveType:s.status.includes('请假')?'年假':'',overtimeHours:s.status.includes('加班')?2:0,remark:`${e.name} 考勤记录`};}));
const leaves=(es)=>es.slice(0,6).map((e,i)=>({id:`LEV-${i+1}`,employee_no:e.employee_no,department:e.department,days:i%2?0.5:1,start_at:`2026-04-${String(i+5).padStart(2,'0')} 09:00:00`,status:'已通过'}));
const pay=(es,m='2026-04')=>es.filter(e=>e.status!=='离职').slice(0,18).map((e,i)=>{const b=n(e.salary_base,9800),su=[600,800,1000][i%3],pf=n(e.performance_base,1800)*[1,1.1,0.9][i%3],ot=[0,120,240][i%3],ad=[0,50,0][i%3],ld=[0,0,120][i%3],tax=200,ss=620,hf=280,pre=b+su+pf+ot-ad-ld;return{id:`PAY-${i+1}`,employeeNo:e.employee_no,name:e.name,department:e.department,month:m,basic:b,subsidy:su,performance_coefficient:Number((pf/Math.max(n(e.performance_base,1800),1)).toFixed(2)),performance:Number(pf.toFixed(2)),overtime_pay:ot,attendance_deduction:ad,leave_deduction:ld,pre_tax_salary:Number(pre.toFixed(2)),social_security_personal:ss,housing_fund_personal:hf,social_security_employer:1180,housing_fund_employer:640,tax,actual:Number((pre-ss-hf-tax).toFixed(2)),grade:['A','B','S'][i%3]};});
const init=()=>{const es=emp();return{employees:es,approvals:c(approvalRows),performance:perf(es),attendance:att(es),leaves:leaves(es),payroll:pay(es),administration:c(adminAssetsRows)}};
const read=()=>{try{return JSON.parse(localStorage.getItem(K)||'null')||init()}catch{return init()}};
const write=(s)=>(localStorage.setItem(K,JSON.stringify(s)),s);
const st=()=>write(read());

export const shouldHandleDevMock=(cfg={})=>on()&&[/^\/employees(?:\/|$)/,/^\/approvals(?:\/|$)/,/^\/performance(?:\/|$)/,/^\/payroll(?:\/|$)/,/^\/attendance(?:\/|$)/,/^\/leaves(?:\/|$)/,/^\/administration\/summary$/].some(r=>r.test(p(cfg.url)));

export const handleDevMock=async(cfg={})=>{const s=st(),u=p(cfg.url),m=String(cfg.method||'get').toLowerCase(),d=typeof cfg.data==='string'?JSON.parse(cfg.data||'{}'):(cfg.data||{});
if(m==='get'&&u==='/employees')return ok(c(s.employees));
if(m==='get'&&u==='/employees/meta')return ok({departments:[...new Set(s.employees.map(i=>i.department))].sort(),positions:s.employees.reduce((a,i)=>((a[i.department]=[...new Set([...(a[i.department]||[]),i.position])].sort()),a),{})});
if(m==='get'&&u==='/employees/check-unique')return ok({duplicate:s.employees.some(i=>i.id!==q(cfg,'exclude_id')&&String(i[q(cfg,'field')]||'')===String(q(cfg,'value')||''))});
if(m==='post'&&u==='/employees'){write({...s,employees:[{id:gid('EMP'),...d,employee_no:d.employee_no||d.employeeNo},...s.employees]});return ok({},'员工创建成功');}
if(m==='put'&&/^\/employees\/[^/]+$/.test(u)){write({...s,employees:s.employees.map(i=>i.id===u.split('/').pop()?{...i,...d}:i)});return ok({},'员工更新成功');}
if(m==='delete'&&/^\/employees\/[^/]+$/.test(u)){write({...s,employees:s.employees.filter(i=>i.id!==u.split('/').pop())});return ok({},'员工删除成功');}
if(m==='post'&&(u==='/employees/departments'||u==='/employees/positions'))return ok({},'保存成功');
if(m==='post'&&u==='/employees/ai/health-check')return ok({items:[],total:0},'AI 信息体检完成');
if(m==='post'&&u==='/employees/ai/workforce-report')return ok({title:'AI人力结构报表',content:'当前组织结构整体稳定，建议持续补强关键岗位梯队。'},'AI 人力结构报表生成完成');
if(m==='get'&&u==='/approvals/overview')return ok({records:s.approvals.filter(i=>(!q(cfg,'status')||i.status===q(cfg,'status'))&&(!q(cfg,'type')||i.type===q(cfg,'type'))),total:s.approvals.length});
if(m==='get'&&/^\/approvals\/[^/]+$/.test(u))return ok(c(s.approvals.find(i=>i.id===u.split('/').pop())||null));
if(m==='post'&&/^\/approvals\/[^/]+\/decision$/.test(u)){write({...s,approvals:s.approvals.map(i=>i.id===u.split('/')[2]?{...i,status:d.decision}:i)});return ok({},d.decision==='已通过'?'审批通过':'已驳回');}
if(m==='post'&&u==='/approvals/batch-decision'){write({...s,approvals:s.approvals.map(i=>(d.ids||[]).includes(i.id)?{...i,status:d.decision}:i)});return ok({},d.decision==='已通过'?'批量审批通过':'批量驳回成功');}
if(m==='get'&&u==='/performance/options')return ok({cycleOptions:['月度','季度','年度'],statusOptions:['待自评','待复核','已发布','已确认','已归档'],employeeOptions:s.employees.filter(i=>i.status!=='离职').map(i=>({employeeNo:i.employee_no,name:i.name,department:i.department,position:i.position}))});
if(m==='get'&&u==='/performance/list'){const page=Number(q(cfg,'page')||1),size=Number(q(cfg,'pageSize')||10),kw=String(q(cfg,'keyword')||'');let rs=c(s.performance).filter(i=>(!kw||i.employeeNo.includes(kw)||i.name.includes(kw))&&(!q(cfg,'department')||i.department===q(cfg,'department'))&&(!q(cfg,'position')||i.position===q(cfg,'position'))&&(!q(cfg,'cycleType')||i.cycleType===q(cfg,'cycleType'))&&(!q(cfg,'assessmentYear')||i.assessmentYear===Number(q(cfg,'assessmentYear')))&&(!q(cfg,'assessmentMonth')||i.assessmentMonth===Number(q(cfg,'assessmentMonth'))));return ok({records:rs.slice((page-1)*size,page*size),total:rs.length});}
if(m==='get'&&/^\/performance\/[^/]+\/detail$/.test(u))return ok(c(s.performance.find(i=>i.id===u.split('/')[2])||null));
if(m==='post'&&u==='/performance/create'){write({...s,performance:[{id:gid('PERF'),...d},...s.performance]});return ok({},'绩效创建成功');}
if(m==='put'&&/^\/performance\/[^/]+$/.test(u)){write({...s,performance:s.performance.map(i=>i.id===u.split('/').pop()?{...i,...d}:i)});return ok({},'绩效更新成功');}
if(m==='delete'&&/^\/performance\/[^/]+$/.test(u)){write({...s,performance:s.performance.filter(i=>i.id!==u.split('/').pop())});return ok({},'绩效删除成功');}
if(m==='post'&&u==='/performance/import/parse')return ok({parsed:{records:s.performance.slice(0,2),errors:[{row:5,employeeNo:'EMP-ERROR',message:'示例异常：工号不存在'}],total_count:3,success_count:2,error_count:1}},'绩效文件解析完成');
if(m==='post'&&u==='/performance/import/confirm'){write({...s,performance:[...(d.records||[]).map(i=>({id:gid('PERF'),...i})),...s.performance]});return ok({},'绩效导入成功');}
if(m==='get'&&u==='/performance/export')return ok({records:c(s.performance),fileName:'绩效报表'});
if(m==='post'&&u.startsWith('/performance/ai/'))return ok({indicators:[{name:'业务目标完成率',weight:100,targetValue:'100%'}],performanceScore:88,attitudeScore:86,abilityScore:90,totalScore:88.4,grade:'A',coefficient:1.2,content:'AI 生成评语。',summary:'本期绩效整体良好。',issues:['协同效率可提升'],reasons:['高峰期任务集中'],highlights:['交付质量稳定'],suggestions:['建议双周复盘'],title:'AI部门绩效报表',overview:'部门绩效表现平稳。',departmentComparison:['产品技术部得分较高'],excellentCases:['张琳表现突出'],improvementCases:['周峰需持续提升'],analysis:['整体结构健康'],evidence:['评分记录完整'],decision:'建议维持原评定',reason:'申诉依据不足'},'AI 操作完成');
if(m==='get'&&u==='/payroll/summary')return ok({records:c(s.payroll)});
if(m==='post'&&u==='/payroll/calculate'){write({...s,payroll:pay(s.employees,d.month||'2026-04')});return ok({records:c(read().payroll)},'薪酬核算完成');}
if(m==='get'&&u==='/attendance/overview')return ok({records:c(s.attendance)});
if(m==='post'&&u==='/attendance/import/parse')return ok({parsed:{total_count:18,success_count:17,error_count:1,errors:[{row:9,employeeNo:'OPS-9999',message:'示例异常：员工不存在'}]}},'考勤文件解析完成');
if(m==='post'&&u==='/attendance/import'){write({...s,attendance:att(s.employees)});return ok({},'考勤导入成功');}
if(m==='post'&&u==='/attendance/ai/generate-summary-report')return ok({title:'AI考勤汇总报表',content:'本月整体出勤率保持稳定，运营中心迟到次数偏高，建议加强提醒。'},'AI考勤汇总生成完成');
if(m==='get'&&u==='/leaves')return ok(c(s.leaves));
if(m==='post'&&u==='/leaves'){write({...s,leaves:[{id:gid('LEV'),...d},...s.leaves]});return ok({},'请假申请创建成功');}
if(m==='get'&&u==='/administration/summary')return ok({records:applyApprovedAssetSyncs(c(s.administration))});
throw new Error(`Unhandled dev mock: ${m.toUpperCase()} ${u}`);
};
