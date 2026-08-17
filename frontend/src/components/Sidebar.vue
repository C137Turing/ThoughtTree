<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>Knowledge Tree</h3>
      <button class="new-btn" @click="createNewSession">+ New</button>
    </div>
    <div class="tree-list">
      <div
        v-for="s in sessions.sessions.value"
        :key="s.id"
        class="tree-node"
        :class="{ active: s.status === 'open', closed: s.status === 'closed', minimized: s.status === 'minimized' }"
        @click="handleNodeClick(s)"
      >
        <span class="node-status" :title="s.status">
          {{ s.status === 'open' ? '\u25CF' : s.status === 'minimized' ? '\u2014' : '\u25CB' }}
        </span>
        <span class="node-title">{{ s.title }}</span>
      </div>
      <div class="tree-empty" v-if="sessions.sessions.value.length === 0">
        No sessions yet
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSessionsStore } from '../stores/sessions'
import { useWindowManager } from '../stores/windowManager'

const sessions = useSessionsStore()
const wm = useWindowManager()

onMounted(() => { sessions.fetchSessions() })

async function createNewSession() {
  const s = await sessions.createSession('New Window')
  if (s) { wm.addWindow(s.id, s.title) }
}

async function handleNodeClick(s: { id: string; title: string; status: string }) {
  if (s.status === 'closed') {
    await fetch(`http://localhost:8000/api/sessions/${s.id}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'open' }),
    })
    s.status = 'open'
    wm.addWindow(s.id, s.title)
  } else if (s.status === 'minimized') {
    wm.focusWindow(s.id)
  } else {
    wm.focusWindow(s.id)
  }
}
</script>

<style scoped>
.sidebar {
  width: 280px; background: #1e1e2e; color: #cdd6f4;
  display: flex; flex-direction: column; flex-shrink: 0;
  border-right: 1px solid #313244;
}
.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; border-bottom: 1px solid #313244;
}
.sidebar-header h3 { font-size: 14px; font-weight: 600; }
.new-btn {
  padding: 4px 12px; border: 1px solid #45475a; border-radius: 6px;
  background: #313244; color: #cdd6f4; font-size: 12px; cursor: pointer;
}
.new-btn:hover { background: #45475a; }
.tree-list { flex: 1; overflow-y: auto; padding: 8px; }
.tree-node {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; border-radius: 6px; cursor: pointer;
  font-size: 13px; transition: background 0.15s;
}
.tree-node:hover { background: #313244; }
.tree-node.active { background: #45475a; color: #fff; }
.tree-node.closed { opacity: 0.5; }
.tree-node.minimized { opacity: 0.7; font-style: italic; }
.node-status { font-size: 10px; width: 16px; text-align: center; }
.tree-node.active .node-status { color: #a6e3a1; }
.tree-node.closed .node-status { color: #6c7086; }
.tree-node.minimized .node-status { color: #f9e2af; }
.node-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tree-empty { padding: 24px; text-align: center; color: #6c7086; font-size: 13px; }
</style>
