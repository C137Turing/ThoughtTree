<template>
  <div class="canvas-container">
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :default-viewport="{ x: 0, y: 0, zoom: 1 }"
      :min-zoom="0.1"
      :max-zoom="2"
      @connect="onConnect"
      @edge-dbl-click="onEdgeDoubleClick"
      @pane-click="closeContextMenu"
      @node-drag-stop="onNodeDragStop"
    >
      <Background />
      <Controls />
      <template #node-custom="nodeProps">
        <div
          class="canvas-node"
          :class="{
            'node-dangling': nodeProps.data.isDangling,
          }"
          :style="{ opacity: nodeProps.data.status === 'closed' ? 0.5 : 1 }"
          @dblclick="openNode(nodeProps.data.sessionId)"
          @contextmenu.prevent="showContextMenu($event, nodeProps.data)"
        >
          <div class="cn-header">
            <span class="cn-status" :class="nodeProps.data.status"></span>
            <span class="cn-title">{{ nodeProps.data.label }}</span>
          </div>
        </div>
      </template>
    </VueFlow>

    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <div class="ctx-item" @click="createChildNode">Create child node</div>
      <div class="ctx-item" @click="deleteNode">Delete node</div>
      <div class="ctx-item" @click="focusNode">Open in window</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import { useSessionsStore } from '../stores/sessions'
import { useWindowManager } from '../stores/windowManager'

const emit = defineEmits<{ 'node-double-click': [sessionId: string] }>()

const sessions = useSessionsStore()
const wm = useWindowManager()
const { fitView } = useVueFlow()

const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const contextMenu = ref({ visible: false, x: 0, y: 0, sessionId: '' })

function buildCanvas() {
  const list = sessions.sessions.value
  const cols = Math.ceil(Math.sqrt(list.length || 1))
  const newNodes = list.map((s, i) => {
    const col = i % cols
    const row = Math.floor(i / cols)
    const isDangling = s.status === 'open' && !list.some((x) => x.parent_id === s.id)
    return {
      id: s.id, type: 'custom',
      position: s.position_x && s.position_y ? { x: s.position_x, y: s.position_y } : { x: col * 250 + 50, y: row * 120 + 50 },
      data: { label: s.title, status: s.status, sessionId: s.id, isDangling },
    }
  })
  const newEdges = list.filter((s) => s.parent_id).map((s) => ({
    id: 'e-' + s.parent_id + '-' + s.id,
    source: s.parent_id!, target: s.id, type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  }))
  nodes.value = newNodes
  edges.value = newEdges
}

onMounted(() => { sessions.fetchSessions().then(buildCanvas) })
watch(() => sessions.sessions.value.length, buildCanvas)

function onConnect(connection: any) {
  edges.value.push({
    id: 'manual-' + connection.source + '-' + connection.target + '-' + Date.now(),
    source: connection.source, target: connection.target, type: 'smoothstep',
    style: { stroke: '#f59e0b', strokeWidth: 1.5, strokeDasharray: '6 3' }, animated: true,
  })
}

function onEdgeDoubleClick(event: any) {
  edges.value = edges.value.filter((e: any) => e.id !== event.edge.id)
}

function showContextMenu(event: MouseEvent, data: any) {
  contextMenu.value = { visible: true, x: event.clientX, y: event.clientY, sessionId: data.sessionId }
}

function closeContextMenu() { contextMenu.value.visible = false }

function onNodeDragStop(event: any) {
  const node = event.node
  if (node) {
    fetch('http://localhost:8000/api/sessions/' + node.id, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ position_x: node.position.x, position_y: node.position.y }),
    }).catch(() => {})
  }
}

function openNode(sessionId: string) {
  closeContextMenu()
  emit('node-double-click', sessionId)
}

async function createChildNode() {
  const s = await sessions.createSession('New Node', contextMenu.value.sessionId)
  closeContextMenu()
  if (s) buildCanvas()
}

async function deleteNode() {
  if (!confirm('Delete this node?')) return
  await fetch('http://localhost:8000/api/sessions/' + contextMenu.value.sessionId, { method: 'DELETE' })
  wm.removeWindow(contextMenu.value.sessionId)
  closeContextMenu()
  sessions.fetchSessions().then(buildCanvas)
}

function focusNode() {
  const sid = contextMenu.value.sessionId
  closeContextMenu()
  emit('node-double-click', sid)
}

onMounted(() => {
  window.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'f' && e.ctrlKey) { e.preventDefault(); fitView() }
  })
})
</script>

<style scoped>
.canvas-container { width: 100%; height: 100%; }
.canvas-node {
  background: #fff; border: 2px solid #e2e8f0; border-radius: 10px;
  padding: 10px 14px; min-width: 160px; cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: box-shadow 0.2s, border-color 0.2s;
}
.canvas-node:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.15); border-color: #6366f1; }
.canvas-node.node-dangling { border-color: #ef4444; animation: danglingPulse 2s ease-in-out infinite; }
.cn-header { display: flex; align-items: center; gap: 8px; }
.cn-status { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.cn-status.open { background: #22c55e; }
.cn-status.closed { background: #94a3b8; }
.cn-status.minimized { background: #eab308; }
.cn-title { font-size: 13px; font-weight: 500; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.context-menu { position: fixed; z-index: 10000; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); padding: 4px 0; min-width: 160px; }
.ctx-item { padding: 8px 16px; font-size: 13px; cursor: pointer; color: #334155; }
.ctx-item:hover { background: #f1f5f9; }
@keyframes danglingPulse { 0%, 100% { border-color: #ef4444; } 50% { border-color: #fca5a5; } }
</style>
