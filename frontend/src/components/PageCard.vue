<template>
  <div class="page-card">
    <div v-if="!hideHeader" class="page-card__header">
      <div>
        <h3 class="section-title">{{ title }}</h3>
        <p class="section-description">{{ description }}</p>
      </div>
      <slot name="actions" />
    </div>
    <div class="page-card__body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  hideHeader: { type: Boolean, default: false },
});
</script>

<style scoped>
.page-card {
  background: var(--hr-surface);
  border: 1px solid var(--hr-border);
  border-radius: 8px;
  box-shadow: var(--hr-shadow);
}

.page-card__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid var(--hr-border);
}

.page-card__body {
  padding: 20px;
}

@media (max-width: 767px) {
  .page-card__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
