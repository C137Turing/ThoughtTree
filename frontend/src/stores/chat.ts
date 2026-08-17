import { ref, computed } from 'vue'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  isStreaming?: boolean
  createdAt?: string
}

const chatCache = new Map<string, ReturnType<typeof _createChatState>>()

export function createChatState(sessionId: string, baseUrl = 'http://localhost:8000') {
  const existing = chatCache.get(sessionId)
  if (existing) return existing
  const state = _createChatState(sessionId, baseUrl)
  chatCache.set(sessionId, state)
  return state
}

function _createChatState(sessionId: string, baseUrl: string) {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  const lastUserMessage = computed(() => {
    const userMsgs = messages.value.filter((m) => m.role === 'user')
    return userMsgs[userMsgs.length - 1] ?? null
  })

  async function sendMessage(content: string): Promise<void> {
    error.value = null
    isStreaming.value = true
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', content, createdAt: new Date().toISOString() }
    messages.value.push(userMsg)
    const aiMsg: ChatMessage = { id: crypto.randomUUID(), role: 'assistant', content: '', isStreaming: true, createdAt: new Date().toISOString() }
    messages.value.push(aiMsg)
    await streamChat(content, aiMsg)
    isStreaming.value = false
  }

  async function streamChat(content: string, aiMsg: ChatMessage): Promise<void> {
    try {
      const res = await fetch(`${baseUrl}/api/sessions/${sessionId}/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      if (!reader) throw new Error('No response body')
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        let event = '', data = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) event = line.slice(7).trim()
          else if (line.startsWith('data: ')) data = line.slice(6).trim()
          else if (!line.trim()) continue
          else continue
          if (!event || !data) continue
          try {
            const parsed = JSON.parse(data)
            if (event === 'token') aiMsg.content += parsed.delta
            else if (event === 'done') { aiMsg.id = parsed.message_id; aiMsg.isStreaming = false }
            else if (event === 'error') { error.value = parsed.message; aiMsg.content = `[Error: ${parsed.message}]`; aiMsg.isStreaming = false }
          } catch { /* skip */ }
          event = ''; data = ''
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

  async function regenerateMessage(aiMessageId: string): Promise<void> {
    const aiIdx = messages.value.findIndex((m) => m.id === aiMessageId)
    if (aiIdx === -1) return
    let userContent = ''
    for (let i = aiIdx - 1; i >= 0; i--) {
      if (messages.value[i]!.role === 'user') { userContent = messages.value[i]!.content; break }
    }
    if (!userContent) return
    const aiMsg = messages.value[aiIdx]!
    aiMsg.content = ''; aiMsg.isStreaming = true
    error.value = null; isStreaming.value = true
    await streamChat(userContent, aiMsg)
    isStreaming.value = false
  }

  async function loadHistory(): Promise<void> {
    try {
      const res = await fetch(`${baseUrl}/api/sessions/${sessionId}/messages`)
      if (res.ok) {
        const msgs = await res.json()
        messages.value = msgs.map((m: any) => ({ id: m.id, role: m.role, content: m.content, isStreaming: false, createdAt: m.created_at }))
      }
    } catch { /* offline */ }
  }

  return { messages, isStreaming, error, lastUserMessage, sendMessage, clearMessages, regenerateMessage, loadHistory }
}
