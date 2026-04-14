<template>
  <div class="page-grid">
    <div class="metric-grid">
      <MetricCard title="剩余年假" :value="`${profile.annualLeave}天`" tip="含调休余额 1 天" icon="休" />
      <MetricCard title="本月出勤率" :value="profile.attendanceRate" tip="较上月提升 1.2%" icon="勤" />
      <MetricCard title="预估工资" :value="profile.monthSalary" tip="含绩效与补贴" icon="薪" />
      <MetricCard title="当前绩效" :value="profile.currentPerformance" tip="本月待最终发布" icon="绩" />
    </div>

    <div class="two-column">
      <PageCard title="个人档案" description="查看个人基础资料与岗位信息。">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ user.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ user.employeeNo }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ user.department }}</el-descriptions-item>
          <el-descriptions-item label="岗位">{{ user.position }}</el-descriptions-item>
          <el-descriptions-item label="角色">员工</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ user.phone || '—' }}</el-descriptions-item>
          <el-descriptions-item label="在职状态">{{ user.status || '—' }}</el-descriptions-item>
          <el-descriptions-item label="政治面貌">{{ user.politicalStatus || '—' }}</el-descriptions-item>
          <el-descriptions-item label="入职日期">{{ user.hireDate || '—' }}</el-descriptions-item>
          <el-descriptions-item label="离职日期">{{ user.resignationDate || '—' }}</el-descriptions-item>
        </el-descriptions>
      </PageCard>

      <PageCard title="待办事项" description="需员工本人尽快处理的任务提醒。">
        <el-timeline>
          <el-timeline-item timestamp="今天" placement="top">补交 4 月 7 日缺卡说明</el-timeline-item>
          <el-timeline-item timestamp="明天" placement="top">确认本月绩效回执</el-timeline-item>
          <el-timeline-item timestamp="本周" placement="top">完成办公用品领用归还登记</el-timeline-item>
        </el-timeline>
      </PageCard>
    </div>

    <PageCard title="公告通知" description="公司与部门公告统一收口。">
      <el-alert
        v-for="notice in profile.notices"
        :key="notice"
        :title="notice"
        type="info"
        :closable="false"
        show-icon
        class="notice-item"
      />
    </PageCard>
  </div>
</template>

<script setup>
import { computed } from 'vue';

import MetricCard from '@/components/charts/MetricCard.vue';
import PageCard from '@/components/PageCard.vue';
import { useAppStore } from '@/stores/app';

const store = useAppStore();
const user = store.user;

const profile = computed(() => ({
  annualLeave: 6,
  attendanceRate: '97.6%',
  monthSalary: '¥12,860',
  currentPerformance: 'B+',
  notices: ['五一节前请于 4 月 28 日前完成请假审批。', '4 月绩效将于本周五 18:00 前完成复核。'],
}));
</script>

<style scoped>
.page-grid {
  display: grid;
  gap: 16px;
}

.notice-item + .notice-item {
  margin-top: 12px;
}
</style>
