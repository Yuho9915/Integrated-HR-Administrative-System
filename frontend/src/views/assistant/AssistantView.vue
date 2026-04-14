<template>
  <PlaceholderPage
    title="AI 员工问答"
    eyebrow="Doubao-Seed-1.6"
    description="支持年假、请假、绩效、工资、领用、报修等高频制度问答，后端统一封装 AI 接口与知识上下文。"
    role="全员"
    note="前端只调用业务接口，不暴露模型接入信息；支持记录问答日志与失败回退。"
  />
</template>

<script setup>
import PlaceholderPage from '@/components/PlaceholderPage.vue';
</script>
