import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  isStreaming?: boolean
  createdAt?: string
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  const lastUserMessage = computed(() => {
    const userMsgs = messages.value.filter((m) => m.role === 'user')
    return userMsgs[userMsgs.length - 1] ?? null
  })

  async function sendMessage(
    sessionId: string,
    content: string,
    baseUrl = 'http://localhost:8000'
  ): Promise<void> {
    error.value = null
    isStreaming.value = true

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    const aiMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      isStreaming: true,
      createdAt: new Date().toISOString(),
    }
    messages.value.push(aiMsg)

    await streamChat(sessionId, content, aiMsg, baseUrl)
    isStreaming.value = false
  }

  async function streamChat(
    sessionId: string,
    content: string,
    aiMsg: ChatMessage,
    baseUrl: string
  ): Promise<void> {
    try {
      const response = await fetch(
        `${baseUrl}/api/sessions/${sessionId}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content }),
        }
      )
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (!line.trim()) continue
          let event = '', data = ''
          if (line.startsWith('event: ')) event = line.slice(7).trim()
          else if (line.startsWith('data: ')) data = line.slice(6).trim()
          else continue
          if (!event || !data) continue
          try {
            const parsed = JSON.parse(data)
            if (event === 'token') aiMsg.content += parsed.delta
            else if (event === 'done') { aiMsg.id = parsed.message_id; aiMsg.isStreaming = false }
            else if (event === 'error') { error.value = parsed.message; aiMsg.content = `[Error: ${parsed.message}]`; aiMsg.isStreaming = false }
          } catch { /* skip */ }
        }
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Unknown error'
      error.value = msg
      aiMsg.content = `[Connection error: ${msg}]`
      aiMsg.isStreaming = false
    }
  }

  function clearMessages(): void { messages.value = [] }

  function removeMessage(id: string): void {
    const idx = messages.value.findIndex((m) => m.id === id)
    if (idx !== -1) messages.value.splice(idx, 1)
  }

  async function regenerateMessage(
    aiMessageId: string,
    sessionId: string,
    baseUrl = 'http://localhost:8000'
  ): Promise<void> {
    const aiIdx = messages.value.findIndex((m) => m.id === aiMessageId)
    if (aiIdx === -1) return
    let userContent = ''
    for (let i = aiIdx - 1; i >= 0; i--) {
      if (messages.value[i]!.role === 'user') {
        userContent = messages.value[i]!.content
        break
      }
    }
    if (!userContent) return
    const aiMsg = messages.value[aiIdx]!
    aiMsg.content = ''
    aiMsg.isStreaming = true
    error.value = null
    isStreaming.value = true
    await streamChat(sessionId, userContent, aiMsg, baseUrl)
    isStreaming.value = false
  }

  return {
    messages, isStreaming, error, lastUserMessage,
    sendMessage, clearMessages, removeMessage, regenerateMessage,
  }
})
