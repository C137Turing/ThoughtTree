<template>
  <div
    class="window-card"
    :class="[win.status]"
    :style="cardStyle"
    ref="cardRef"
    @mousedown="focusWindow"
  >
    <WindowHeader
      :title="win.title"
      :breadcrumb="breadcrumb"
      @minimize="minimizeWindow"
      @close="closeWindow"
      @breadcrumb-click="handleBreadcrumbClick"
    />
    <div class="window-body">
      <MessageList
        :messages="chat.messages.value"
        @regenerate="handleRegenerate"
      />
    </div>
    <div class="resize-handle resize-n" @mousedown.stop="startResize($event, 'n')"></div>
    <div class="resize-handle resize-s" @mousedown.stop="startResize($event, 's')"></div>
    <div class="resize-handle resize-e" @mousedown.stop="startResize($event, 'e')"></div>
    <div class="resize-handle resize-w" @mousedown.stop="startResize($event, 'w')"></div>
    <div class="resize-handle resize-ne" @mousedown.stop="startResize($event, 'ne')"></div>
    <div class="resize-handle resize-nw" @mousedown.stop="startResize($event, 'nw')"></div>
    <div class="resize-handle resize-se" @mousedown.stop="startResize($event, 'se')"></div>
    <div class="resize-handle resize-sw" @mousedown.stop="startResize($event, 'sw')"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDraggable } from '@vueuse/core'
import WindowHeader from './WindowHeader.vue'
import MessageList from './MessageList.vue'
import { useWindowManager } from '../stores/windowManager'
import { createChatState } from '../stores/chat'
import type { WindowState } from '../stores/windowManager'

const props = defineProps<{ win: WindowState }>()
const wm = useWindowManager()
const chat = createChatState(props.win.id)
const cardRef = ref<HTMLElement | null>(null)
const breadcrumb = ref<{ id: string; title: string }[]>([])

onMounted(() => { chat.loadHistory() })

// Dragging
useDraggable(cardRef, {
  initialValue: { x: props.win.position.x, y: props.win.position.y },
  onEnd: (pos) => { wm.updateWindowPosition(props.win.id, pos.x, pos.y) },
})

// Resize
const resizing = ref(false)
const resizeDir = ref('')
const resizeStart = ref({ x: 0, y: 0, w: 0, h: 0, l: 0, t: 0 })

function startResize(e: MouseEvent, dir: string) {
  resizing.value = true; resizeDir.value = dir
  resizeStart.value = { x: e.clientX, y: e.clientY, w: props.win.size.width, h: props.win.size.height, l: props.win.position.x, t: props.win.position.y }
  document.addEventListener('mousemove', onResizeMouseMove)
  document.addEventListener('mouseup', onResizeMouseUp)
}

function onResizeMouseMove(e: MouseEvent) {
  if (!resizing.value) return
  const dx = e.clientX - resizeStart.value.x
  const dy = e.clientY - resizeStart.value.y
  let { w, h, l, t } = resizeStart.value
  const dir = resizeDir.value
  if (dir.includes('e')) w = Math.max(300, w + dx)
  if (dir.includes('w')) { w = Math.max(300, w - dx); l = l + dx }
  if (dir.includes('s')) h = Math.max(200, h + dy)
  if (dir.includes('n')) { h = Math.max(200, h - dy); t = t + dy }
  wm.updateWindowPosition(props.win.id, l, t)
  wm.updateWindowSize(props.win.id, w, h)
}

function onResizeMouseUp() {
  resizing.value = false
  document.removeEventListener('mousemove', onResizeMouseMove)
  document.removeEventListener('mouseup', onResizeMouseUp)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onResizeMouseMove)
  document.removeEventListener('mouseup', onResizeMouseUp)
})

const cardStyle = computed(() => ({
  left: `${props.win.position.x}px`,
  top: `${props.win.position.y}px`,
  width: `${props.win.size.width}px`,
  height: `${props.win.size.height}px`,
  zIndex: props.win.zIndex,
  transform: `rotate(${props.win.rotation}deg) scale(${props.win.scale})`,
  opacity: props.win.opacity,
  filter: `grayscale(${props.win.grayscale})`,
  transition: 'transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1), opacity 400ms ease, filter 400ms ease',
}))

function focusWindow() {
  if (wm.topWindow?.id !== props.win.id) wm.focusWindow(props.win.id)
}

function minimizeWindow() { wm.minimizeWindow(props.win.id) }

function closeWindow() {
  fetch(`http://localhost:8000/api/sessions/${props.win.id}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'closed' }),
  }).catch(() => {})
  wm.removeWindow(props.win.id)
}

function handleRegenerate(messageId: string) { chat.regenerateMessage(messageId) }
function handleBreadcrumbClick(nodeId: string) { wm.focusWindow(nodeId) }
</script>

<style scoped>
.window-card {
  position: absolute;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  display: flex; flex-direction: column; overflow: hidden;
}
.window-card.minimized { display: none; }
.window-body { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.resize-handle { position: absolute; z-index: 10; }
.resize-n { top: 0; left: 8px; right: 8px; height: 4px; cursor: n-resize; }
.resize-s { bottom: 0; left: 8px; right: 8px; height: 4px; cursor: s-resize; }
.resize-e { top: 8px; right: 0; bottom: 8px; width: 4px; cursor: e-resize; }
.resize-w { top: 8px; left: 0; bottom: 8px; width: 4px; cursor: w-resize; }
.resize-ne { top: 0; right: 0; width: 8px; height: 8px; cursor: ne-resize; }
.resize-nw { top: 0; left: 0; width: 8px; height: 8px; cursor: nw-resize; }
.resize-se { bottom: 0; right: 0; width: 8px; height: 8px; cursor: se-resize; }
.resize-sw { bottom: 0; left: 0; width: 8px; height: 8px; cursor: sw-resize; }
</style>
