<template>
  <div class="page-grid">
    <PageCard title="AI 问答机器人" description="员工可自助查询请假、年假、工资、绩效与行政流程。">
      <div class="assistant-layout">
        <div class="assistant-side page-section">
          <h4>快捷提问</h4>
          <el-space wrap>
            <el-button v-for="item in quickQuestions" :key="item" @click="useQuestion(item)">{{ item }}</el-button>
          </el-space>
          <el-alert title="AI 无法回答时，将引导联系综合管理部。" type="info" :closable="false" show-icon />
        </div>

        <div class="assistant-main page-section">
          <div class="chat-window">
            <div v-for="item in messages" :key="item.id" class="chat-bubble" :class="item.role">
              <strong>{{ item.role === 'user' ? '我' : 'AI 助手' }}</strong>
              <p>{{ item.content }}</p>
            </div>
          </div>
          <div class="chat-input">
            <el-input v-model="question" type="textarea" :rows="3" placeholder="请输入你的问题" />
            <div class="chat-actions">
              <el-button @click="question = ''">清空</el-button>
              <el-button type="primary" :loading="loading" @click="sendQuestion">发送</el-button>
            </div>
          </div>
        </div>
      </div>
    </PageCard>
  </div>
</template>

<script setup>
import { ref } from 'vue';

import PageCard from '@/components/PageCard.vue';
import { askAssistant } from '@/api/modules';
import { aiQuickQuestions } from '@/mock/data';

const quickQuestions = aiQuickQuestions;
const question = ref('');
const loading = ref(false);
const messages = ref([
  { id: 1, role: 'assistant', content: '您好，我是 HR AI 助手，可为您解答年假、请假、工资、绩效与行政流程问题。' },
]);

const useQuestion = (value) => {
  question.value = value;
};

const sendQuestion = async () => {
  if (!question.value.trim()) return;
  const value = question.value;
  messages.value.push({ id: Date.now(), role: 'user', content: value });
  question.value = '';
  loading.value = true;
  try {
    const result = await askAssistant({ prompt: value });
    messages.value.push({ id: Date.now() + 1, role: 'assistant', content: result.data.content });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.page-grid {
  display: grid;
}

.assistant-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
}

.assistant-side,
.assistant-main {
  padding: 20px;
}

.chat-window {
  min-height: 380px;
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
}

.chat-bubble {
  max-width: 76%;
  padding: 14px 16px;
  border-radius: 16px;
  line-height: 1.8;
}

.chat-bubble.user {
  margin-left: auto;
  background: #409eff;
  color: #fff;
}

.chat-bubble.assistant {
  background: #f5f9ff;
  border: 1px solid rgba(64, 158, 255, 0.14);
}

.chat-bubble p,
.chat-bubble strong {
  margin: 0;
}

.chat-input {
  display: grid;
  gap: 12px;
}

.chat-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 900px) {
  .assistant-layout {
    grid-template-columns: 1fr;
  }

  .chat-bubble {
    max-width: 100%;
  }
}
</style>
