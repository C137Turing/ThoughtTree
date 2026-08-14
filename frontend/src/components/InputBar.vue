<!-- InputBar.vue — 底部输入框 -->
<template>
  <footer class="input-bar">
    <div class="input-wrapper">
      <input
        type="text"
        class="message-input"
        placeholder="选择或创建一个窗口开始对话..."
        disabled
      />
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.input-bar {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: var(--input-bar-bg, #f0f0f0);
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.input-wrapper {
  width: 100%;
}

.message-input {
  width: 100%;
  height: 40px;
  padding: 0 16px;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #999;
  outline: none;
}

.message-input:disabled {
  cursor: not-allowed;
  background: #f5f5f5;
}
</style>