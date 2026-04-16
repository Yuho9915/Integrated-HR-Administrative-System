<template>
  <div class="floating-ai" :class="{ 'is-open': showDialog }">
    <button class="floating-ai__fab" type="button" @click="openDialog" aria-label="打开 AI 助手">
      <span class="floating-ai__pulse"></span>
      <span class="floating-ai__avatar">
        <img class="floating-ai__avatar-image floating-ai__avatar-image--fab" :src="robotImage" alt="AI机器人" />
      </span>
    </button>

    <el-dialog
      v-model="showDialog"
      width="920px"
      class="floating-ai__dialog"
      :show-close="false"
      destroy-on-close
      align-center
    >
      <template #header>
        <div class="floating-ai__window-actions">
          <button class="floating-ai__window-btn floating-ai__window-btn--ghost" type="button" aria-label="最小化">—</button>
          <button class="floating-ai__window-btn" type="button" @click="showDialog = false" aria-label="关闭 AI 助手">×</button>
        </div>
      </template>

      <div class="floating-ai__panel">
        <div class="floating-ai__hero">
          <div class="floating-ai__hero-avatar">
            <img class="floating-ai__avatar-image floating-ai__avatar-image--hero" :src="robotImage" alt="小助理" />
          </div>
          <h3>Hi，欢迎使用小助理</h3>
          <p>我可以帮你解答考勤、绩效、薪酬、流程等问题</p>
        </div>

        <div class="floating-ai__quick">
          <button
            v-for="item in quickQuestions"
            :key="item"
            type="button"
            class="floating-ai__quick-card"
            @click="useQuestion(item)"
          >
            <strong>{{ item }}</strong>
            <span>点击快速发起咨询</span>
          </button>
        </div>

        <div v-if="answer || loading" class="floating-ai__answer">
          <div class="floating-ai__answer-head">
            <span>AI 回复</span>
            <el-tag v-if="loading" size="small" type="primary">思考中</el-tag>
          </div>
          <p v-if="!loading">{{ answer }}</p>
          <div v-else class="floating-ai__skeleton">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div class="floating-ai__composer-shell">
          <div class="floating-ai__composer">
            <el-input
              v-model="question"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="输入你想咨询的 HR 相关问题..."
              @keydown.enter.exact.prevent="sendQuestion"
            />

            <div class="floating-ai__composer-bottom">
              <span class="floating-ai__tips">Enter 发送，Shift + Enter 换行</span>
              <button class="floating-ai__send" type="button" :disabled="loading" @click="sendQuestion" aria-label="发送">
                <span v-if="!loading">➜</span>
                <span v-else>...</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

import { askAssistant } from '@/api/modules';
import { useAppStore } from '@/stores/app';
import robotImage from '../../../../机器人.webp';

const store = useAppStore();
const roleQuickQuestionMap = {
  employee: [
    '我本月还能请几天年假？',
    '补卡申请怎么提交？',
    '工资条在哪里查看？',
    '办公用品领用怎么申请？',
  ],
  manager: [
    '待我审批的事项有哪些？',
    '部门绩效录入后还要做什么？',
    '调岗申请需要几级审批？',
    '怎么查看本部门员工考勤异常？',
  ],
  hr: [
    '怎么处理转正申请？',
    '审批中心如何区分人事和行政审批？',
    '员工档案缺失材料怎么补齐？',
    '薪酬异动申请通常怎么流转？',
  ],
  boss: [
    '本月人力成本重点看什么？',
    '如何快速查看组织绩效表现？',
    '哪些审批需要总经理处理？',
    '怎么理解当前考勤异常趋势？',
  ],
};

const quickQuestions = computed(() => roleQuickQuestionMap[store.user?.role] || roleQuickQuestionMap.employee);
const showDialog = ref(false);
const question = ref('');
const answer = ref('');
const loading = ref(false);

const openDialog = () => {
  showDialog.value = true;
};

const useQuestion = (value) => {
  question.value = value;
};

const sendQuestion = async () => {
  const prompt = question.value.trim();
  if (!prompt || loading.value) return;
  loading.value = true;
  answer.value = '';
  try {
    const result = await askAssistant({ prompt });
    answer.value = result.data.content || '暂未获取到回复';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.floating-ai__fab {
  position: fixed;
  right: 26px;
  bottom: 26px;
  z-index: 60;
  display: grid;
  place-items: center;
  width: 78px;
  height: 78px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(127, 211, 255, 0.95), rgba(52, 141, 255, 0.96) 52%, rgba(31, 93, 255, 0.98) 100%);
  box-shadow: 0 20px 42px rgba(31, 93, 255, 0.3), 0 0 0 6px rgba(126, 209, 255, 0.14);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.floating-ai__fab:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 26px 48px rgba(31, 93, 255, 0.36), 0 0 0 8px rgba(126, 209, 255, 0.18);
}

.floating-ai__pulse {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.18) 50%, transparent 100%);
  transform: translateX(-120%);
  animation: floating-ai-sheen 4s linear infinite;
}

.floating-ai__avatar {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.floating-ai__avatar-image {
  display: block;
  object-fit: cover;
}

.floating-ai__avatar-image--fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  box-shadow: 0 8px 18px rgba(31, 93, 255, 0.22);
}

.floating-ai__avatar-image--hero {
  width: 92px;
  height: 92px;
  border-radius: 28px;
  box-shadow: 0 18px 36px rgba(31, 93, 255, 0.12);
}

:deep(.floating-ai__dialog .el-dialog) {
  max-width: calc(100vw - 48px);
  border-radius: 34px;
  overflow: hidden;
  background: linear-gradient(180deg, #fcfdff 0%, #f5f8fd 100%);
  box-shadow: 0 28px 80px rgba(56, 87, 122, 0.16);
}

:deep(.floating-ai__dialog .el-dialog__header) {
  margin-right: 0;
  padding: 0;
}

:deep(.floating-ai__dialog .el-dialog__body) {
  padding: 0 36px 36px;
}

.floating-ai__window-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 18px 20px 0;
}

.floating-ai__window-btn {
  width: 34px;
  height: 34px;
  border: 1px solid rgba(24, 46, 94, 0.08);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #5c6b80;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.floating-ai__window-btn:hover {
  background: #fff;
  color: #31425a;
  box-shadow: 0 6px 14px rgba(58, 78, 120, 0.08);
}

.floating-ai__window-btn--ghost {
  font-size: 20px;
}

.floating-ai__panel {
  display: grid;
  gap: 28px;
  padding-top: 8px;
}

.floating-ai__hero {
  display: grid;
  justify-items: center;
  text-align: center;
  gap: 14px;
  padding: 4px 0 2px;
}

.floating-ai__hero-avatar {
  width: 128px;
  height: 128px;
  display: grid;
  place-items: center;
  border-radius: 36px;
  background: radial-gradient(circle at top, rgba(142, 197, 255, 0.18), rgba(255, 255, 255, 0.94) 66%);
}

.floating-ai__hero h3,
.floating-ai__hero p {
  margin: 0;
}

.floating-ai__hero h3 {
  color: var(--hr-title);
  font-size: 34px;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.floating-ai__hero p {
  color: #7b8aa2;
  font-size: 15px;
}

.floating-ai__quick {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.floating-ai__quick-card {
  min-height: 88px;
  padding: 16px 16px 14px;
  border: 1px solid rgba(72, 112, 182, 0.08);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.floating-ai__quick-card:hover {
  background: #fff;
  border-color: rgba(72, 112, 182, 0.16);
  box-shadow: 0 12px 24px rgba(58, 95, 160, 0.08);
  transform: translateY(-2px);
}

.floating-ai__quick-card strong {
  display: block;
  color: var(--hr-title);
  font-size: 14px;
  line-height: 1.5;
}

.floating-ai__quick-card span {
  display: block;
  margin-top: 8px;
  color: #98a5b8;
  font-size: 12px;
}

.floating-ai__answer {
  padding: 18px 20px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(72, 112, 182, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.floating-ai__answer-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.floating-ai__answer-head span {
  color: #6d7d93;
  font-size: 13px;
}

.floating-ai__answer p {
  margin: 0;
  color: var(--hr-title);
  line-height: 1.9;
  white-space: pre-wrap;
}

.floating-ai__composer-shell {
  padding-top: 6px;
}

.floating-ai__composer {
  padding: 18px 20px 16px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(72, 112, 182, 0.08);
  box-shadow: 0 14px 30px rgba(65, 92, 136, 0.08);
}

:deep(.floating-ai__composer .el-textarea__inner) {
  min-height: 116px !important;
  padding: 4px 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  color: var(--hr-title);
  font-size: 16px;
  line-height: 1.8;
}

:deep(.floating-ai__composer .el-textarea__inner::placeholder) {
  color: #9aa7b8;
}

.floating-ai__composer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.floating-ai__tips {
  color: #98a5b8;
  font-size: 12px;
}

.floating-ai__send {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, #9dd6ff, #5b8fff 45%, #4a67ff);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(75, 103, 255, 0.22);
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.floating-ai__send:hover:not(:disabled) {
  transform: translateY(-1px);
}

.floating-ai__send:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.floating-ai__skeleton {
  display: grid;
  gap: 8px;
}

.floating-ai__skeleton span {
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(31, 93, 255, 0.08), rgba(31, 93, 255, 0.18), rgba(31, 93, 255, 0.08));
  background-size: 200% 100%;
  animation: floating-ai-loading 1.2s linear infinite;
}

.floating-ai__skeleton span:nth-child(2) {
  width: 88%;
}

.floating-ai__skeleton span:nth-child(3) {
  width: 70%;
}

@keyframes floating-ai-sheen {
  0% { transform: translateX(-120%); }
  100% { transform: translateX(120%); }
}

@keyframes floating-ai-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 960px) {
  :deep(.floating-ai__dialog .el-dialog) {
    width: calc(100vw - 24px) !important;
  }

  :deep(.floating-ai__dialog .el-dialog__body) {
    padding: 0 18px 18px;
  }

  .floating-ai__hero h3 {
    font-size: 28px;
  }

  .floating-ai__quick {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .floating-ai__fab {
    right: 14px;
    bottom: 14px;
    width: 68px;
    height: 68px;
  }

  .floating-ai__avatar {
    width: 56px;
    height: 56px;
  }

  .floating-ai__avatar-image--fab {
    width: 48px;
    height: 48px;
  }

  .floating-ai__window-actions {
    padding: 14px 14px 0;
  }

  .floating-ai__quick {
    grid-template-columns: 1fr;
  }

  .floating-ai__composer {
    padding: 16px;
  }

  .floating-ai__composer-bottom {
    align-items: flex-end;
  }
}
</style>
