<template>
  <el-breadcrumb separator=">">
    <el-breadcrumb-item v-for="(item, index) in items" :key="`${index}-${item}`">{{ item }}</el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
});
</script>
