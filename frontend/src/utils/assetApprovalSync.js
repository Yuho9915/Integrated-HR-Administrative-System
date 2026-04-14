const STORAGE_KEY = 'hr-admin-approved-asset-syncs';

const clone = (value) => JSON.parse(JSON.stringify(value));
const nowDate = () => new Date().toISOString().slice(0, 10);
const slug = (value = '') => String(value).replace(/\s+/g, '').toUpperCase();
const num = (value) => {
  const match = String(value || '').match(/(\d+)/);
  return match ? Number(match[1]) : 1;
};

const readList = () => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
};

const writeList = (list) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
};

const isAssetType = (type = '') => ['办公用品领用', '资产领用', '办公设备领用', '公章使用', '会议室申请', '会议室预约', '用车申请'].some((item) => String(type).includes(item));

const pickInfo = (record, labels) => {
  const items = [...(record?.asset_info || []), ...(record?.related_info || [])];
  const hit = items.find((item) => labels.some((label) => String(item.label || '').includes(label)));
  return hit?.value || '';
};

const inferName = (record) => {
  const direct = pickInfo(record, ['资产名称', '用品名称', '物品名称', '资源名称', '公章名称', '会议室', '车辆']);
  if (direct) return String(direct);
  const duration = String(record?.duration || '');
  const m = duration.match(/^(.+?)\s*\d+/);
  if (m?.[1]) return m[1].trim();
  if (String(record?.type || '').includes('公章')) return '合同章';
  if (String(record?.type || '').includes('会议室')) return '会议室 A';
  if (String(record?.type || '').includes('用车')) return '商务用车';
  return String(record?.type || '审批资产');
};

const inferCategoryType = (record, assetName) => {
  const type = String(record?.type || '');
  if (type.includes('公章')) return '印章';
  if (type.includes('会议室')) return '会议资源';
  if (type.includes('用车')) return '车辆';
  if (type.includes('办公用品')) return '办公耗材';
  if (type.includes('设备')) return '办公设备';
  if (/打印纸|文件夹|耗材|门禁卡/.test(assetName)) return '办公耗材';
  if (/公章|合同章/.test(assetName)) return '印章';
  if (/会议室/.test(assetName)) return '会议资源';
  if (/用车|车辆|商务车/.test(assetName)) return '车辆';
  if (/打印机|投影仪|显示器/.test(assetName)) return '办公设备';
  if (/电脑|笔记本/.test(assetName)) return '固定资产';
  return '行政物料';
};

const inferStatus = (record) => {
  const type = String(record?.type || '');
  if (type.includes('公章') || type.includes('会议室') || type.includes('用车')) return '借出中';
  return '使用中';
};

const inferQuantity = (record) => {
  const quantity = pickInfo(record, ['数量', '申请数量', '领用数量']);
  if (quantity) return Math.max(num(quantity), 1);
  return Math.max(num(record?.duration), 1);
};

const inferDepartment = (record) => {
  return pickInfo(record, ['申请部门', '使用部门', '所属部门']) || record?.department || '综合管理部';
};

const inferLocation = (categoryType) => {
  return {
    固定资产: '办公区',
    会议设备: '会议设备柜',
    办公设备: '办公设备区',
    办公耗材: '行政仓库',
    会议资源: '会议区',
    印章: '行政保险柜',
    车辆: '地下车库',
    办公家具: '办公区',
    行政物料: '前台储物柜',
    后勤保障: '后勤区',
  }[categoryType] || '综合区';
};

export const persistApprovedAssetRequest = (record) => {
  if (!record || !isAssetType(record.type) || record.status === '已驳回') return false;
  const list = readList();
  const approvalId = record.id || `${record.type}-${record.applicant}-${record.apply_time}`;
  if (list.some((item) => item.approvalId === approvalId)) return false;
  const name = inferName(record);
  const categoryType = inferCategoryType(record, name);
  list.push({
    approvalId,
    applicant: record.applicant || '待分配',
    department: inferDepartment(record),
    assetName: name,
    categoryType,
    quantity: inferQuantity(record),
    status: inferStatus(record),
    applyDate: String(record.apply_time || nowDate()).slice(0, 10),
    location: pickInfo(record, ['存放位置', '使用地点']) || inferLocation(categoryType),
    remark: `审批同步：${record.type}`,
  });
  writeList(list);
  return true;
};

export const applyApprovedAssetSyncs = (rows = []) => {
  const next = clone(rows || []);
  const syncs = readList();
  syncs.forEach((sync) => {
    const target = next.find((item) => item.name === sync.assetName || slug(item.name) === slug(sync.assetName));
    const row = target || (() => {
      const created = {
        code: `CAT-SYNC-${String(next.length + 1).padStart(3, '0')}`,
        name: sync.assetName,
        type: sync.categoryType,
        total: 0,
        safe: 1,
        buyDate: sync.applyDate,
        value: 0,
        details: [],
      };
      next.unshift(created);
      return created;
    })();
    for (let i = 0; i < sync.quantity; i += 1) {
      row.total += 1;
      row.details = row.details || [];
      row.details.push({
        no: `${row.code}-S${String(row.details.length + 1).padStart(3, '0')}`,
        owner: sync.applicant,
        dept: sync.department,
        status: sync.status,
        receive: sync.applyDate,
        back: '',
        loc: sync.location,
        remark: sync.remark,
      });
    }
  });
  return next;
};

export const clearApprovedAssetSyncs = () => {
  writeList([]);
};
