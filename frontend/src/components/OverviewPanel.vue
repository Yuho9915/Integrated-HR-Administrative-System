<template>
  <div class="overview-grid">
    <section class="hero-card page-section">
      <div>
        <p class="hero-card__eyebrow">YUHO HR · B 端轻量化中枢</p>
        <h1>人事、行政、审批、绩效一体协同</h1>
        <p>
          以浅色高效工作台承载 50 人企业全流程管理，覆盖考勤导入、绩效校验、工资核算与 AI 智能问答。
        </p>
      </div>
      <div class="hero-card__stats">
        <div>
          <strong>7</strong>
          <span>类请假规则</span>
        </div>
        <div>
          <strong>4</strong>
          <span>审批标签域</span>
        </div>
        <div>
          <strong>24h</strong>
          <span>AI 助理在线</span>
        </div>
      </div>
    </section>

    <section class="metric-grid">
      <article v-for="item in metrics" :key="item.label" class="metric-card page-section">
        <p>{{ item.label }}</p>
        <strong>{{ item.value }}</strong>
        <span>{{ item.tip }}</span>
      </article>
    </section>

    <section class="dual-grid">
      <article class="page-section panel-card">
        <div class="panel-card__header">
          <h3 class="section-title">本月待办</h3>
          <el-tag type="warning">优先处理</el-tag>
        </div>
        <el-timeline>
          <el-timeline-item
            v-for="task in tasks"
            :key="task.title"
            :timestamp="task.deadline"
            placement="top"
          >
            <div class="timeline-content">
              <strong>{{ task.title }}</strong>
              <p>{{ task.desc }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>
      </article>

      <article class="page-section panel-card">
        <div class="panel-card__header">
          <h3 class="section-title">规则快照</h3>
          <el-tag type="success">数据库解耦</el-tag>
        </div>
        <ul class="rule-list">
          <li v-for="rule in rules" :key="rule">{{ rule }}</li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script setup>
const metrics = [
  { label: '在职人数', value: '48', tip: '含试用 5 人' },
  { label: '待审批事项', value: '13', tip: '人事/行政/资产/综合' },
  { label: '本月考勤达标率', value: '96.2%', tip: '较上月 +1.8%' },
  { label: '本月应发薪资', value: '¥436,800', tip: 'AI 核算完成率 89%' },
];

const tasks = [
  { title: '导入 4 月考勤 Excel', desc: '同步打卡机导出文件并合并请假数据。', deadline: '今天 18:00 前' },
  { title: '提交绩效 AI 校验', desc: '部门经理录入完成后统一校验 A/B/C/D 分布。', deadline: '明天 10:00' },
  { title: '确认 3 笔采购申请', desc: '行政耗材库存预警触发，待最终审核。', deadline: '本周内' },
];

const rules = [
  '测试环境默认 SQLite，生产环境切换腾讯云 MongoDB。',
  '审批流支持按角色、金额、请假类型灵活编排。',
  'Doubao-Seed-1.6 统一封装在后端服务层，前端仅调用业务接口。',
  '报表导出预留 Excel / PDF 能力，便于 CloudBase 前端交付。',
];
</script>

<style scoped>
.overview-grid {
  display: grid;
  gap: 16px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #edf5ff 100%);
}

.hero-card__eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--hr-primary);
}

.hero-card h1 {
  margin: 0;
  font-size: 24px;
  color: var(--hr-title);
}

.hero-card p {
  max-width: 640px;
  line-height: 1.7;
}

.hero-card__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(88px, 1fr));
  gap: 12px;
  min-width: 290px;
}

.hero-card__stats div,
.metric-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(64, 158, 255, 0.16);
}

.hero-card__stats strong,
.metric-card strong {
  display: block;
  font-size: 24px;
  color: var(--hr-title);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.metric-card p,
.metric-card span {
  margin: 0;
}

.metric-card span {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--hr-info);
}

.dual-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}

.panel-card {
  padding: 20px;
}

.panel-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.timeline-content p,
.rule-list {
  margin: 8px 0 0;
}

.rule-list {
  padding-left: 18px;
  line-height: 1.9;
}

@media (max-width: 1024px) {
  .metric-grid,
  .dual-grid,
  .hero-card {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-card__stats {
    min-width: 100%;
  }
}
</style>
