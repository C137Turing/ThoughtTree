<template>
  <div class="stack-area">
    <WindowCard
      v-for="win in wm.activeWindows"
      :key="win.id"
      :win="win"
    />
    <div class="stack-empty" v-if="wm.activeWindows.length === 0">
      No active windows. Click "+ New" in the sidebar to begin.
    </div>
  </div>
</template>

<script setup lang="ts">
import WindowCard from './WindowCard.vue'
import { useWindowManager } from '../stores/windowManager'

const wm = useWindowManager()
</script>

<style scoped>
.stack-area {
  position: relative;
  flex: 1;
  overflow: hidden;
  background: #e8ecf1;
}
.stack-empty {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  color: #9ca3af;
  font-size: 14px;
}
</style>
