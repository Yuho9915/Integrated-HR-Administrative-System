<template>
  <div class="assistant-page-note page-section">
    <div class="assistant-page-note__icon">🤖</div>
    <h3>AI 助手已升级为全局悬浮入口</h3>
    <p>当前所有角色页面右下角都提供 AI 机器人入口，点击即可打开问答弹窗。</p>
    <p>当前不展示历史记录，仅保留本次提问与即时回复。</p>
  </div>
</template>

<style scoped>
.assistant-page-note {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 240px;
  text-align: center;
}

.assistant-page-note__icon {
  width: 72px;
  height: 72px;
  display: grid;
  place-items: center;
  border-radius: 24px;
  font-size: 34px;
  background: linear-gradient(135deg, rgba(31, 93, 255, 0.08), rgba(85, 178, 255, 0.18));
}

.assistant-page-note h3,
.assistant-page-note p {
  margin: 0;
}

.assistant-page-note h3 {
  color: var(--hr-title);
}

.assistant-page-note p {
  color: var(--hr-info);
  line-height: 1.8;
}
</style>
