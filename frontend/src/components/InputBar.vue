<template>
  <footer class="input-bar">
    <div class="input-wrapper">
      <span class="current-window-badge" v-if="wm.topWindow" :title="wm.topWindow.title">
        {{ wm.topWindow.title }}
      </span>
      <input
        type="text"
        class="message-input"
        v-model="inputText"
        placeholder="Type a message..."
        :disabled="!wm.topWindow"
        @keydown.enter="sendMessage"
      />
      <button class="send-btn" :disabled="!inputText.trim() || !wm.topWindow" @click="sendMessage">
        Send
      </button>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useWindowManager } from '../stores/windowManager'
import { createChatState } from '../stores/chat'

const wm = useWindowManager()
const inputText = ref('')

function handleInsertQuote(e: Event) {
  const detail = (e as CustomEvent).detail
  if (detail && detail.text) {
    inputText.value = '> ' + detail.text + '\n\n' + inputText.value
  }
}

onMounted(() => { window.addEventListener('insert-quote', handleInsertQuote) })
onUnmounted(() => { window.removeEventListener('insert-quote', handleInsertQuote) })

function sendMessage() {
  const content = inputText.value.trim()
  if (!content || !wm.topWindow) return
  const chat = createChatState(wm.topWindow.id)
  chat.sendMessage(content)
  inputText.value = ''
}
</script>

<style scoped>
.input-bar {
  height: 60px; display: flex; align-items: center;
  padding: 0 16px; background: #f0f0f0; border-top: 1px solid #e0e0e0;
}
.input-wrapper {
  width: 100%; display: flex; align-items: center; gap: 8px;
}
.current-window-badge {
  padding: 4px 10px; background: #4f46e5; color: #fff;
  border-radius: 6px; font-size: 12px; white-space: nowrap;
  max-width: 160px; overflow: hidden; text-overflow: ellipsis;
}
.message-input {
  flex: 1; height: 40px; padding: 0 14px;
  border: 1px solid #e0e0e0; border-radius: 8px;
  font-size: 14px; background: #fff; color: #1f2937; outline: none;
}
.message-input:disabled { background: #f5f5f5; color: #999; cursor: not-allowed; }
.send-btn {
  padding: 8px 20px; border: none; border-radius: 8px;
  background: #4f46e5; color: #fff; font-size: 14px; cursor: pointer;
}
.send-btn:disabled { background: #c7d2fe; cursor: not-allowed; }
</style>