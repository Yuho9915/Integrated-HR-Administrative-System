<template>
  <div class="metric-card compact-card">
    <div>
      <p>{{ title }}</p>
      <strong>{{ value }}</strong>
      <span>{{ tip }}</span>
    </div>
    <div class="compact-card__icon">{{ icon }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: String,
  tip: String,
  icon: { type: String, default: '·' },
});
</script>

<style scoped>
.compact-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 147.99px;
}

.compact-card__icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(64, 158, 255, 0.1);
  color: var(--hr-primary);
  font-size: 20px;
}
</style>
