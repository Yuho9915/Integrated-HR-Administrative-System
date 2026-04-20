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
      @closed="resetConversation"
    >
      <template #header>
        <div class="floating-ai__window-actions">
          <button class="floating-ai__window-btn" type="button" @click="closeDialog" aria-label="关闭小助理">×</button>
        </div>
      </template>

      <div class="floating-ai__panel" :class="{ 'is-chat-mode': hasConversation }">
        <template v-if="!hasConversation">
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
        </template>

        <div v-else class="floating-ai__chat-window">
          <div class="floating-ai__messages">
            <div v-for="item in messages" :key="item.id" class="floating-ai__message" :class="`is-${item.role}`">
              <div class="floating-ai__message-bubble">
                <span class="floating-ai__message-role">{{ item.role === 'user' ? '你' : '小助理' }}</span>
                <p>{{ item.content }}</p>
              </div>
            </div>

            <div v-if="loading" class="floating-ai__message is-assistant">
              <div class="floating-ai__message-bubble">
                <span class="floating-ai__message-role">小助理</span>
                <div class="floating-ai__skeleton">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="floating-ai__composer-shell">
          <div class="floating-ai__composer">
            <el-input
              v-model="question"
              type="textarea"
              :rows="2"
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
const loading = ref(false);
const messages = ref([]);
const hasConversation = computed(() => messages.value.length > 0);

const openDialog = () => {
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
};

const resetConversation = () => {
  question.value = '';
  loading.value = false;
  messages.value = [];
};

const useQuestion = (value) => {
  question.value = value;
};

const sendQuestion = async () => {
  const prompt = question.value.trim();
  if (!prompt || loading.value) return;

  messages.value.push({ id: `user-${Date.now()}`, role: 'user', content: prompt });
  question.value = '';
  loading.value = true;

  try {
    const result = await askAssistant({ prompt });
    const content = result?.data?.content || '当前请求失败，请稍后重试。';
    messages.value.push({ id: `assistant-${Date.now()}`, role: 'assistant', content });
  } catch {
    messages.value.push({ id: `assistant-${Date.now()}`, role: 'assistant', content: '当前请求失败，请稍后重试。' });
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
  width: 38px;
  height: 38px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(127, 211, 255, 0.95), rgba(52, 141, 255, 0.96) 52%, rgba(31, 93, 255, 0.98) 100%);
  box-shadow: 0 12px 26px rgba(31, 93, 255, 0.24), 0 0 0 3px rgba(126, 209, 255, 0.12);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.floating-ai__fab:hover {
  transform: translateY(-2px) scale(1.03);
  box-shadow: 0 16px 30px rgba(31, 93, 255, 0.3), 0 0 0 4px rgba(126, 209, 255, 0.16);
}

.floating-ai__pulse {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.18) 50%, transparent 100%);
  transform: translateX(-120%);
  animation: floating-ai-sheen 4s linear infinite;
}

.floating-ai__avatar {
  width: 30px;
  height: 30px;
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
  width: 26px;
  height: 26px;
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(31, 93, 255, 0.18);
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
  padding: 18px 20px 0;
}

.floating-ai__window-btn {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(116, 136, 171, 0.14);
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 253, 0.98));
  color: #7d8ca3;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(119, 139, 172, 0.08);
  transition: all 0.2s ease;
}

.floating-ai__window-btn:hover {
  color: #50627d;
  border-color: rgba(116, 136, 171, 0.22);
  box-shadow: 0 10px 22px rgba(119, 139, 172, 0.12);
  transform: translateY(-1px);
}

.floating-ai__panel {
  display: grid;
  gap: 24px;
  padding-top: 8px;
}

.floating-ai__panel.is-chat-mode {
  gap: 18px;
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

.floating-ai__chat-window {
  display: grid;
  min-height: 420px;
  max-height: 420px;
  padding-top: 4px;
}

.floating-ai__messages {
  display: grid;
  gap: 14px;
  align-content: start;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 6px;
}

.floating-ai__message {
  display: flex;
}

.floating-ai__message.is-user {
  justify-content: flex-end;
}

.floating-ai__message.is-assistant {
  justify-content: flex-start;
}

.floating-ai__message-bubble {
  max-width: 78%;
  padding: 14px 16px;
  border-radius: 22px;
  background: #ffffff;
  border: 1px solid rgba(72, 112, 182, 0.08);
  box-shadow: 0 8px 18px rgba(65, 92, 136, 0.04);
}

.floating-ai__message.is-user .floating-ai__message-bubble {
  background: linear-gradient(135deg, #edf5ff, #f7fbff);
}

.floating-ai__message-role {
  display: block;
  margin-bottom: 8px;
  color: #7b8aa2;
  font-size: 12px;
}

.floating-ai__message-bubble p {
  margin: 0;
  color: var(--hr-title);
  line-height: 1.85;
  white-space: pre-wrap;
}

.floating-ai__composer-shell {
  padding-top: 6px;
}

.floating-ai__composer {
  padding: 14px 18px 12px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(72, 112, 182, 0.08);
  box-shadow: 0 14px 30px rgba(65, 92, 136, 0.08);
}

:deep(.floating-ai__composer .el-textarea__inner) {
  min-height: 64px !important;
  padding: 2px 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  color: var(--hr-title);
  font-size: 15px;
  line-height: 1.7;
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
    width: 38px;
    height: 38px;
  }

  .floating-ai__avatar {
    width: 30px;
    height: 30px;
  }

  .floating-ai__avatar-image--fab {
    width: 26px;
    height: 26px;
  }

  .floating-ai__window-actions {
    padding: 14px 14px 0;
  }

  .floating-ai__quick {
    grid-template-columns: 1fr;
  }

  .floating-ai__chat-window {
    min-height: 360px;
    max-height: 360px;
  }

  .floating-ai__message-bubble {
    max-width: 100%;
  }

  .floating-ai__composer {
    padding: 14px;
  }

  .floating-ai__composer-bottom {
    align-items: flex-end;
  }
}
</style>
