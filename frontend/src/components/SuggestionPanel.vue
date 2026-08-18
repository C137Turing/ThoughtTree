<template>
  <div class="suggestion-panel" :class="{ collapsed: !expanded }">
    <div class="sp-header" @click="expanded = !expanded">
      <span class="sp-title">AI Suggestions</span>
      <span class="sp-toggle">{{ expanded ? 'collapse' : 'expand' }}</span>
    </div>
    <div class="sp-body" v-if="expanded">
      <div class="sp-stats" v-if="stats">
        <span class="stat">{{ stats.total_nodes }} nodes</span>
        <span class="stat">{{ stats.answered }} answered</span>
        <span class="stat" v-if="stats.dangling">{{ stats.dangling }} dangling</span>
      </div>
      <div class="sp-stagnation" v-if="stagnant">
        No activity for {{ idleMinutes }} min. Keep exploring?
      </div>
      <div class="sp-suggestions" v-if="suggestions.length">
        <div v-for="(s, i) in suggestions" :key="i" class="sp-item">
          <span class="sp-icon">{{ s.type === 'missing_dimension' ? '?' : '!' }}</span>
          <span class="sp-text">{{ s.message }}</span>
          <button class="sp-action" @click="adoptSuggestion(s)">Analyze</button>
        </div>
      </div>
      <div class="sp-empty" v-if="!suggestions.length && !stagnant && stats">
        All clear!
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useWindowManager } from '../stores/windowManager'
import { useSessionsStore } from '../stores/sessions'

const wm = useWindowManager()
const sessions = useSessionsStore()

const expanded = ref(true)
const suggestions = ref<any[]>([])
const stats = ref<any>(null)
const idleMinutes = ref(0)
const stagnant = ref(false)
let idleTimer: ReturnType<typeof setInterval> | null = null
let lastActivity = Date.now()

function resetActivity() { lastActivity = Date.now(); stagnant.value = false }
onMounted(() => {
  document.addEventListener('keydown', resetActivity)
  document.addEventListener('click', resetActivity)
  idleTimer = setInterval(() => {
    idleMinutes.value = Math.floor((Date.now() - lastActivity) / 60000)
    if (idleMinutes.value >= 5) stagnant.value = true
  }, 30000)
  fetchSuggestions()
})
onUnmounted(() => {
  document.removeEventListener('keydown', resetActivity)
  document.removeEventListener('click', resetActivity)
  if (idleTimer) clearInterval(idleTimer)
})

async function fetchSuggestions() {
  const topWindow = wm.topWindow
  if (!topWindow) return
  try {
    const res = await fetch('http://localhost:8000/api/suggestions?root_id=' + topWindow.id)
    const data = await res.json()
    suggestions.value = data.suggestions || []
    stats.value = data.stats || null
  } catch { /* offline */ }
}

async function adoptSuggestion(suggestion: any) {
  const topWindow = wm.topWindow
  if (!topWindow) return
  const s = await sessions.createSession(
    suggestion.dimension || 'New Analysis', topWindow.id, topWindow.rootId
  )
  if (s) {
    wm.addWindow(s.id, s.title, topWindow.id, s.root_id)
    const { createChatState } = await import('../stores/chat')
    const chat = createChatState(s.id)
    chat.sendMessage('Please analyze: ' + (suggestion.dimension || suggestion.message))
  }
}
</script>

<style scoped>
.suggestion-panel { border-top: 1px solid #313244; background: #181825; flex-shrink: 0; }
.sp-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; cursor: pointer; user-select: none; }
.sp-title { font-size: 13px; font-weight: 600; color: #cdd6f4; }
.sp-toggle { font-size: 11px; color: #6c7086; }
.sp-body { padding: 0 16px 12px; max-height: 300px; overflow-y: auto; }
.sp-stats { display: flex; gap: 12px; margin-bottom: 8px; }
.stat { font-size: 11px; color: #6c7086; }
.sp-stagnation { font-size: 12px; color: #f9e2af; padding: 6px 0; }
.sp-suggestions { display: flex; flex-direction: column; gap: 6px; }
.sp-item { display: flex; align-items: flex-start; gap: 6px; padding: 6px 8px; background: #1e1e2e; border-radius: 6px; }
.sp-icon { font-size: 12px; flex-shrink: 0; width: 18px; text-align: center; }
.sp-text { font-size: 12px; color: #cdd6f4; flex: 1; line-height: 1.4; }
.sp-action { padding: 2px 8px; border: 1px solid #45475a; border-radius: 4px; background: #313244; color: #cdd6f4; font-size: 11px; cursor: pointer; flex-shrink: 0; }
.sp-action:hover { background: #45475a; }
.sp-empty { font-size: 12px; color: #6c7086; text-align: center; padding: 8px; }
</style>
