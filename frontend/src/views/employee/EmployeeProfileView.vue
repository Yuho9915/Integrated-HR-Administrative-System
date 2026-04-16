<template>
  <div class="page-grid home-grid">
    <div class="metric-grid">
      <MetricCard title="剩余年假" :value="`${profile.annualLeave}天`" tip="含调休余额 1 天" icon="休" />
      <MetricCard title="本月出勤率" :value="profile.attendanceRate" tip="较上月提升 1.2%" icon="勤" />
      <MetricCard title="当前绩效" :value="profile.currentPerformance" tip="本月待最终发布" icon="绩" />
    </div>

    <PageCard title="待办事项" description="需员工本人尽快处理的任务提醒。">
      <div class="todo-list">
        <button v-for="item in profile.todos" :key="item.title" type="button" class="todo-item" @click="go(item.path, item.query)">
          <div class="todo-item__time">{{ item.when }}</div>
          <div class="todo-item__main">
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </div>
          <span class="todo-item__action">去处理</span>
        </button>
      </div>
    </PageCard>

    <PageCard title="公告通知" description="公司与部门公告统一收口。">
      <div class="notice-list">
        <article v-for="notice in profile.notices" :key="`${notice.category}-${notice.title}`" class="notice-card">
          <div class="notice-card__meta">
            <el-tag size="small" :type="notice.tagType" effect="light">{{ notice.category }}</el-tag>
            <span>{{ notice.date }}</span>
          </div>
          <strong>{{ notice.title }}</strong>
          <p>{{ notice.summary }}</p>
        </article>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';

const router = useRouter();

const go = (path, query = undefined) => {
  router.push(query ? { path, query } : path);
};

const profile = computed(() => ({
  annualLeave: 6,
  attendanceRate: '97.6%',
  currentPerformance: 'B+',
  todos: [
    { when: '今天', title: '补交 4 月 7 日缺卡说明', desc: '进入申请中心补充缺卡说明并提交补卡申请。', path: '/employee/applications', query: { action: 'supplement', date: '2026-04-07', time: '18:00', reason: '下班外出返程遗漏签退，申请补卡' } },
    { when: '明天', title: '确认本月绩效回执', desc: '查看本月绩效结果与上级评价内容。', path: '/employee/performance' },
    { when: '本周', title: '完成办公用品领用归还登记', desc: '进入申请中心补充行政用品领用登记。', path: '/employee/applications', query: { action: 'detail', type: '办公用品领用', date: '2026-04-18', time: '09:00', endTime: '18:00', status: '待登记', approver: '综合管理部', reason: '请完成办公用品领用归还登记' } },
  ],
  notices: [
    { category: '公司通知', tagType: 'primary', date: '2026-04-24', title: '五一节前请假审批截止提醒', summary: '节前请假、调休申请需在 4 月 28 日 18:00 前完成直属经理与 HR 审批。' },
    { category: '绩效通知', tagType: 'success', date: '2026-04-23', title: '4 月绩效结果进入复核阶段', summary: '本月绩效将在本周五 18:00 前完成最终复核，请及时查看并确认绩效回执。' },
    { category: '行政通知', tagType: 'warning', date: '2026-04-22', title: '办公用品领用台账本周统一补录', summary: '本周需完成个人办公用品领用与归还台账补录，逾期将影响行政盘点准确性。' },
  ],
}));
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

.home-grid,
.todo-list,
.notice-list {
  display: grid;
  gap: 12px;
}

.todo-item,
.notice-card {
  border: 1px solid rgba(64, 158, 255, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 16px;
}

.todo-item {
  width: 100%;
  padding: 14px 16px;
  display: grid;
  grid-template-columns: 68px 1fr auto;
  gap: 14px;
  align-items: center;
  text-align: left;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.todo-item:hover {
  transform: translateY(-1px);
  border-color: rgba(64, 158, 255, 0.24);
  box-shadow: 0 12px 24px rgba(64, 158, 255, 0.08);
}

.todo-item__time,
.todo-item__action {
  color: var(--hr-primary);
  font-size: 12px;
  font-weight: 700;
}

.todo-item__main strong,
.notice-card strong {
  color: var(--hr-title);
}

.todo-item__main p,
.notice-card p {
  margin: 0;
  color: var(--hr-info);
  line-height: 1.7;
  font-size: 12px;
}

.notice-card {
  padding: 14px 16px;
  display: grid;
  gap: 8px;
}

.notice-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.notice-card__meta span {
  color: #8c9bb1;
  font-size: 12px;
}

@media (max-width: 767px) {
  .todo-item,
  .notice-card__meta {
    grid-template-columns: 1fr;
  }

  .todo-item,
  .notice-card__meta {
    display: grid;
    align-items: flex-start;
  }
}
</style>
