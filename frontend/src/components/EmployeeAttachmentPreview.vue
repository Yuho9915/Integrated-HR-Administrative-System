<template>
  <el-dialog v-model="visibleProxy" title="附件预览" width="min(92vw, 1080px)" top="4vh" class="attachment-preview-dialog" destroy-on-close>
    <div class="preview-shell">
      <div class="preview-toolbar">
        <div>
          <strong>{{ attachment?.name || '附件预览' }}</strong>
          <p>{{ typeLabel }}</p>
        </div>
        <div class="preview-actions">
          <el-button type="primary" round @click="$emit('download')">下载</el-button>
        </div>
      </div>

      <div v-if="isImage" class="image-wrap">
        <img v-if="previewUrl" :src="previewUrl" :alt="attachment?.name || '附件图片'" />
        <el-empty v-else description="图片内容不可用" />
      </div>

      <div v-else-if="isPdf" class="pdf-wrap">
        <div class="pdf-toolbar">
          <div class="pdf-meta">
            <span>PDF 在线预览</span>
            <span>{{ Math.round(scale * 100) }}%</span>
          </div>
          <div class="pdf-actions">
            <el-button class="ghost-btn" @click="zoomOut">缩小</el-button>
            <el-button class="ghost-btn" @click="zoomIn">放大</el-button>
            <el-button class="ghost-btn" @click="prevPage">上一页</el-button>
            <el-button class="ghost-btn" @click="nextPage">下一页</el-button>
            <el-button class="ghost-btn" @click="openInNewTab">新页签打开</el-button>
          </div>
        </div>
        <div class="pdf-page-note">第 {{ page }} / {{ totalPages }} 页（浏览器原生预览）</div>
        <iframe v-if="pdfFrameUrl" class="pdf-frame" :src="pdfFrameUrl" title="PDF 预览"></iframe>
        <el-empty v-else description="PDF 内容不可用" />
      </div>

      <el-empty v-else description="暂不支持该附件格式预览" />
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  attachment: { type: Object, default: null },
});
const emit = defineEmits(['update:modelValue', 'download']);

const visibleProxy = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});
const scale = ref(1);
const page = ref(1);
const totalPages = ref(1);
const objectUrl = ref('');

const typeLabel = computed(() => {
  if (props.attachment?.mime_type?.includes('pdf')) return 'PDF 在线预览';
  if (props.attachment?.mime_type?.startsWith('image/')) return '图片在线预览';
  return '附件内容';
});
const isImage = computed(() => props.attachment?.mime_type?.startsWith('image/'));
const isPdf = computed(() => props.attachment?.mime_type?.includes('pdf'));
const previewUrl = computed(() => objectUrl.value);
const pdfFrameUrl = computed(() => objectUrl.value ? `${objectUrl.value}#page=${page.value}&zoom=${Math.round(scale.value * 100)}` : '');

const revokeObjectUrl = () => {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value);
    objectUrl.value = '';
  }
};
const base64ToBlob = (contentBase64, mimeType) => {
  const binary = atob(contentBase64 || '');
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type: mimeType || 'application/octet-stream' });
};
const rebuildObjectUrl = () => {
  revokeObjectUrl();
  const attachment = props.attachment;
  if (!attachment) return;
  if (attachment.raw instanceof File) {
    objectUrl.value = URL.createObjectURL(attachment.raw);
    return;
  }
  if (!attachment.content_base64) return;
  objectUrl.value = URL.createObjectURL(base64ToBlob(attachment.content_base64, attachment.mime_type));
};
const openInNewTab = () => {
  const target = pdfFrameUrl.value || previewUrl.value;
  if (target) window.open(target, '_blank', 'noopener,noreferrer');
};
const zoomIn = () => { scale.value = Math.min(scale.value + 0.25, 2); };
const zoomOut = () => { scale.value = Math.max(scale.value - 0.25, 0.75); };
const nextPage = () => { page.value += 1; totalPages.value = Math.max(totalPages.value, page.value); };
const prevPage = () => { page.value = Math.max(1, page.value - 1); };
watch(() => props.attachment, () => { scale.value = 1; page.value = 1; totalPages.value = 1; rebuildObjectUrl(); }, { immediate: true });
onBeforeUnmount(revokeObjectUrl);
</script>

<style scoped>
.preview-shell{display:grid;gap:16px;min-height:60vh}.preview-toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:4px 0 12px;border-bottom:1px solid var(--hr-border)}.preview-toolbar strong{color:var(--hr-title);font-size:16px}.preview-toolbar p{margin:6px 0 0;color:var(--hr-info);font-size:12px}.preview-actions :deep(.el-button){border-radius:8px;background:#409EFF;border-color:#409EFF}.image-wrap,.pdf-frame{background:linear-gradient(180deg,#f8fbff 0%,#eff5ff 100%);border:1px solid rgba(64,158,255,.12);border-radius:8px}.image-wrap{display:flex;justify-content:center;align-items:flex-start;padding:16px;min-height:52vh;overflow:auto}.image-wrap img{max-width:100%;height:auto;border-radius:8px;box-shadow:var(--hr-shadow-soft)}.pdf-wrap{display:grid;gap:12px}.pdf-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.pdf-meta{display:flex;align-items:center;gap:10px;color:var(--hr-title);font-weight:600}.pdf-actions{display:flex;gap:8px;flex-wrap:wrap}.pdf-page-note{font-size:12px;color:var(--hr-info)}.pdf-frame{width:100%;min-height:60vh}.ghost-btn{border-radius:8px;border-color:#409EFF;color:#409EFF;background:#fff}.ghost-btn:hover{background:#409EFF;color:#fff;border-color:#409EFF}.attachment-preview-dialog :deep(.el-dialog__body){padding-top:12px}@media (max-width:767px){.preview-toolbar{flex-direction:column;align-items:flex-start}.pdf-toolbar{align-items:flex-start;justify-content:flex-start}}
</style>
