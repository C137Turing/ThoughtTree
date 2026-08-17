<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>Knowledge Tree</h3>
      <button class="new-btn" @click="createNewSession">+ New</button>
    </div>
    <div class="tree-list">
      <TreeNode
        v-for="node in treeNodes"
        :key="node.session.id"
        :node="node"
        @click="handleTreeNodeClick(node.session)"
        @delete="handleDelete(node.session, $event)"
      />
      <div class="tree-empty" v-if="treeNodes.length === 0">
        No sessions yet
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, computed } from "vue"
import { useSessionsStore, type SessionInfo } from "../stores/sessions"
import { useWindowManager } from "../stores/windowManager"
import TreeNode from "./TreeNode.vue"

const sessions = useSessionsStore()
const wm = useWindowManager()

onMounted(() => { sessions.fetchSessions() })

interface TreeNodeType { session: SessionInfo; children: TreeNodeType[]; depth: number }

const treeNodes = computed(() => {
  const list = sessions.sessions.value
  const map = new Map<string, TreeNodeType>()
  const roots: TreeNodeType[] = []
  for (const s of list) { map.set(s.id, { session: s, children: [], depth: 0 }) }
  for (const node of map.values()) {
    const parentId = node.session.parent_id
    if (parentId && map.has(parentId)) {
      const parent = map.get(parentId)!
      node.depth = parent.depth + 1
      parent.children.push(node)
    } else { roots.push(node) }
  }
  return roots
})

async function createNewSession() {
  const s = await sessions.createSession("New Window")
  if (s) { wm.addWindow(s.id, s.title, s.parent_id, s.root_id) }
}

function handleTreeNodeClick(s: SessionInfo) { handleNodeClick(s) }

async function handleNodeClick(s: SessionInfo) {
  if (s.status === "closed") {
    await fetch("http://localhost:8000/api/sessions/" + s.id, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "open" }),
    })
    s.status = "open"
    wm.addWindow(s.id, s.title, s.parent_id, s.root_id)
  } else if (s.status === "minimized") {
    wm.focusWindow(s.id)
  } else {
    if (wm.getWindow(s.id)) { wm.focusWindow(s.id) }
    else { wm.addWindow(s.id, s.title, s.parent_id, s.root_id) }
  }
}

async function handleDelete(s: SessionInfo, event: Event) {
  event.stopPropagation()
  if (!confirm("Delete this node?")) return
  await fetch("http://localhost:8000/api/sessions/" + s.id, { method: "DELETE" })
  wm.removeWindow(s.id)
  sessions.fetchSessions()
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
.tree-empty { padding: 24px; text-align: center; color: #6c7086; font-size: 13px; }
</style>