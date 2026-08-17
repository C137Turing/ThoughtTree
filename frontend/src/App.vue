<template>
  <div class="app-layout" @keydown.tab.prevent="toggleMode">
    <Sidebar />
    <div class="main-area">
      <div class="mode-bar">
        <button class="mode-btn" @click="toggleMode" :title="canvasMode ? 'Switch to window mode (Tab)' : 'Switch to canvas mode (Tab)'">
          {{ canvasMode ? 'Window Mode' : 'Canvas Mode' }}
        </button>
        <span class="mode-hint">Tab</span>
      </div>
      <div class="view-container">
        <transition name="fade" mode="out-in">
          <Workspace v-if="!canvasMode" key="workspace" />
          <CanvasView v-else key="canvas" @node-double-click="switchToWindow" />
        </transition>
      </div>
      <InputBar />
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Workspace from './components/Workspace.vue'
import CanvasView from './components/CanvasView.vue'
import InputBar from './components/InputBar.vue'
import { useWindowManager } from './stores/windowManager'

const canvasMode = ref(false)
const wm = useWindowManager()

function toggleMode() { canvasMode.value = !canvasMode.value }

function switchToWindow(sessionId: string) {
  canvasMode.value = false
  wm.focusWindow(sessionId)
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app-layout { display: flex; height: 100vh; }
.main-area { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.mode-bar { display: flex; align-items: center; gap: 8px; padding: 4px 12px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.mode-btn { padding: 4px 12px; border: 1px solid #cbd5e1; border-radius: 4px; background: #fff; font-size: 12px; cursor: pointer; color: #334155; }
.mode-btn:hover { background: #f1f5f9; }
.mode-hint { font-size: 11px; color: #94a3b8; background: #f1f5f9; padding: 2px 6px; border-radius: 3px; }
.view-container { flex: 1; overflow: hidden; position: relative; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>