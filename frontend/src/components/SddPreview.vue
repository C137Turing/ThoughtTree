<template>
  <div class="sdd-preview">
    <div class="sdd-toolbar">
      <h3>SDD Preview</h3>
      <div class="toolbar-actions">
        <button class="tb-btn" @click="generate" :disabled="loading">
          {{ loading ? 'Generating...' : 'Generate SDD' }}
        </button>
        <button class="tb-btn" @click="exportMarkdown" :disabled="!sddContent">
          Export .md
        </button>
        <button class="tb-btn" @click="$emit('close')">Close</button>
      </div>
    </div>
    <div class="sdd-body" v-if="sddContent">
      <div class="sdd-sidebar">
        <div v-for="section in navSections" :key="section.title" class="nav-item" @click="scrollTo(section.title)">
          {{ section.title }}
        </div>
      </div>
      <div class="sdd-content" ref="contentRef" v-html="renderedSdd"></div>
    </div>
    <div class="sdd-empty" v-else-if="!loading">
      <p>Select a root session and click "Generate SDD".</p>
      <div class="root-select">
        <input v-model="rootId" placeholder="Root session ID" />
      </div>
    </div>
    <div class="sdd-loading" v-if="loading"><p>Generating...</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useWindowManager } from '../stores/windowManager'

defineEmits<{ close: [] }>()

const wm = useWindowManager()
const rootId = ref(wm.topWindow?.id || '')
const sddContent = ref<string | null>(null)
const loading = ref(false)
const contentRef = ref<HTMLElement | null>(null)

const navSections = computed(() => {
  if (!sddContent.value) return []
  const sections: { key: string; title: string }[] = []
  for (const line of sddContent.value.split('\n')) {
    if (line.startsWith('## ')) sections.push({ key: line, title: line.replace('## ', '') })
  }
  return sections
})

const renderedSdd = computed(() => {
  if (!sddContent.value) return ''
  return marked.parse(sddContent.value, { async: false }) as string
})

async function generate() {
  if (!rootId.value) return
  loading.value = true
  try {
    const res = await fetch('http://localhost:8000/api/sdd/generate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ root_id: rootId.value }),
    })
    const { task_id } = await res.json()
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 500))
      const taskRes = await fetch('http://localhost:8000/api/sdd/task/' + task_id)
      const task = await taskRes.json()
      if (task.status === 'done') { sddContent.value = task.sdd; break }
      if (task.status === 'error') { sddContent.value = '# Error\n\n' + task.sdd; break }
    }
  } catch (e: unknown) {
    sddContent.value = '# Error\n\n' + (e instanceof Error ? e.message : 'Unknown error')
  } finally { loading.value = false }
}

function scrollTo(_key: string) {
  contentRef.value?.querySelector('h2')?.scrollIntoView({ behavior: 'smooth' })
}

function exportMarkdown() {
  if (!sddContent.value) return
  const blob = new Blob([sddContent.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'SDD_' + new Date().toISOString().slice(0, 10) + '.md'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.sdd-preview { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10000; background: #fff; display: flex; flex-direction: column; }
.sdd-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
.sdd-toolbar h3 { font-size: 16px; color: #1e293b; }
.toolbar-actions { display: flex; gap: 8px; }
.tb-btn { padding: 6px 16px; border: 1px solid #cbd5e1; border-radius: 6px; background: #fff; font-size: 13px; cursor: pointer; color: #334155; }
.tb-btn:hover:not(:disabled) { background: #f1f5f9; }
.tb-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.sdd-body { display: flex; flex: 1; overflow: hidden; }
.sdd-sidebar { width: 220px; border-right: 1px solid #e2e8f0; padding: 16px; overflow-y: auto; background: #f8fafc; }
.nav-item { padding: 6px 10px; font-size: 13px; cursor: pointer; color: #475569; border-radius: 4px; margin-bottom: 2px; }
.nav-item:hover { background: #e2e8f0; color: #1e293b; }
.sdd-content { flex: 1; padding: 24px 32px; overflow-y: auto; font-size: 14px; line-height: 1.7; color: #1e293b; }
.sdd-content :deep(h1) { font-size: 24px; margin-bottom: 16px; }
.sdd-content :deep(h2) { font-size: 18px; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #e2e8f0; }
.sdd-content :deep(h3) { font-size: 15px; margin: 16px 0 8px; }
.sdd-content :deep(blockquote) { border-left: 3px solid #6366f1; padding-left: 12px; margin: 8px 0; color: #64748b; }
.sdd-empty, .sdd-loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; gap: 16px; }
.root-select input { padding: 6px 12px; border: 1px solid #cbd5e1; border-radius: 6px; width: 300px; }
</style>
