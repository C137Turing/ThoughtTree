import { ref } from 'vue'

export interface SessionInfo {
  id: string; title: string; parent_id: string | null; root_id: string
  status: string; created_at?: string
  position_x?: number; position_y?: number
}

const sessions = ref<SessionInfo[]>([])

export function useSessionsStore() {
  async function fetchSessions() {
    try {
      const res = await fetch('http://localhost:8000/api/sessions/')
      sessions.value = await res.json()
    } catch { /* offline */ }
  }

  async function createSession(title: string, parentId?: string, rootId?: string): Promise<SessionInfo | null> {
    try {
      const res = await fetch('http://localhost:8000/api/sessions/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, parent_id: parentId || null, root_id: rootId || null }),
      })
      const s = await res.json()
      sessions.value.push(s)
      return s
    } catch { return null }
  }

  return { sessions, fetchSessions, createSession }
}
