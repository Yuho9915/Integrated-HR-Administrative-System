<template>
  <div class="placeholder page-section">
    <div>
      <p class="placeholder__eyebrow">{{ eyebrow }}</p>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="页面定位">{{ title }}</el-descriptions-item>
      <el-descriptions-item label="适配角色">{{ role }}</el-descriptions-item>
      <el-descriptions-item label="交互约束">{{ note }}</el-descriptions-item>
    </el-descriptions>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  role: { type: String, required: true },
  note: { type: String, required: true },
  eyebrow: { type: String, default: '模块占位页' },
});
</script>

<style scoped>
.placeholder {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 16px;
  padding: 16px;
}

.placeholder__eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--hr-primary);
  letter-spacing: 0.12em;
}

.placeholder h2 {
  margin: 0 0 12px;
  font-size: 20px;
  color: var(--hr-title);
}

.placeholder p {
  margin: 0;
  line-height: 1.8;
}

@media (max-width: 900px) {
  .placeholder {
    grid-template-columns: 1fr;
  }
}
</style>
