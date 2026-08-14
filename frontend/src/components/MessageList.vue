<template>
  <div class="message-list" ref="listRef">
    <div v-if="messages.length === 0" class="empty-hint">
      Start a conversation by sending a message below.
    </div>
    <MessageItem
      v-for="msg in messages"
      :key="msg.id"
      :role="msg.role"
      :content="msg.content"
      :is-streaming="msg.isStreaming"
      @copy="handleCopy(msg)"
      @regenerate="handleRegenerate(msg)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import MessageItem from './MessageItem.vue'
import type { ChatMessage } from '../stores/chat'

const props = defineProps<{
  messages: ChatMessage[]
}>()

const emit = defineEmits<{
  copy: [content: string]
  regenerate: []
}>()

const listRef = ref<HTMLElement | null>(null)

// Auto-scroll to bottom
watch(
  () => props.messages.length,
  async () => {
    await nextTick()
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  }
)

async function handleCopy(msg: ChatMessage) {
  try {
    await navigator.clipboard.writeText(msg.content)
  } catch {
    // Fallback
    const textarea = document.createElement('textarea')
    textarea.value = msg.content
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
  }
}

function handleRegenerate(_msg: ChatMessage) {
  emit('regenerate')
}
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.empty-hint {
  text-align: center;
  color: #9ca3af;
  margin-top: 60px;
  font-size: 14px;
}
</style>
