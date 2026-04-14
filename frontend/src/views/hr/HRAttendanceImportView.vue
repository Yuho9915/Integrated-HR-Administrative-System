<template>
  <div class="page-grid">
    <PageCard title="考勤 Excel 导入" description="上传打卡机导出文件，自动识别异常并生成结果。">
      <div class="two-column">
        <el-form label-position="top">
          <el-form-item label="导入月份">
            <el-date-picker v-model="month" type="month" placeholder="选择月份" style="width: 100%" />
          </el-form-item>
          <el-form-item label="上传考勤文件">
            <el-upload drag action="#" :auto-upload="false" :on-change="handleFileChange" :show-file-list="true" :limit="1">
              <el-icon><UploadFilled /></el-icon>
              <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持 .xlsx / .xls 文件，大小不超过 10MB</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-space wrap>
            <el-button type="primary" :loading="uploading" @click="submitUpload">开始导入</el-button>
            <el-button @click="downloadErrorList">下载异常清单</el-button>
          </el-space>
        </el-form>

        <div class="page-section import-result">
          <h4>导入结果</h4>
          <el-progress :percentage="result.percentage" />
          <el-descriptions :column="1" border>
            <el-descriptions-item label="文件名称">{{ result.fileName || '未上传' }}</el-descriptions-item>
            <el-descriptions-item label="处理状态">{{ result.status }}</el-descriptions-item>
            <el-descriptions-item label="匹配字段">{{ result.matchedFields }}</el-descriptions-item>
            <el-descriptions-item label="异常数量">{{ result.errors.length }}</el-descriptions-item>
          </el-descriptions>
          <el-alert v-if="result.errors.length" :title="result.errors.join('；')" type="warning" :closable="false" show-icon style="margin-top: 16px" />
        </div>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';

import PageCard from '@/components/PageCard.vue';
import { importAttendanceFile } from '@/api/modules';
import { exportWorkbook } from '@/utils/export';

const month = ref('2026-04');
const fileRef = ref(null);
const uploading = ref(false);
const result = reactive({ fileName: '', fileSize: 0, status: '待上传', percentage: 0, matchedFields: '', errors: [] });

const handleFileChange = (file) => {
  fileRef.value = file.raw;
  result.fileName = file.name;
  result.fileSize = file.size;
  result.status = '已选择';
  result.percentage = 30;
};

const submitUpload = async () => {
  if (!fileRef.value) {
    ElMessage.warning('请先选择 Excel 文件');
    return;
  }
  uploading.value = true;
  const formData = new FormData();
  formData.append('file', fileRef.value);
  try {
    const response = await importAttendanceFile(formData);
    result.status = response.message;
    result.percentage = 100;
    result.matchedFields = Object.entries(response.data.import.matchedFields || {}).map(([k, v]) => `${k}:${v}`).join(' / ');
    result.errors = response.data.import.errors || [];
    ElMessage.success('导入成功');
  } finally {
    uploading.value = false;
  }
};

const downloadErrorList = () => {
  exportWorkbook(result.errors.map((item, index) => ({ 序号: index + 1, 异常: item })), '考勤异常清单', 'Abnormal');
};
</script>

<style scoped>
.page-grid {
  display: grid;
}

.import-result {
  padding: 20px;
}
</style>
