<script setup lang="ts">
import Sidebar from './components/Sidebar.vue'
import Workspace from './components/Workspace.vue'
import InputBar from './components/InputBar.vue'
</script>

<template>
  <div class="app-layout">
    <Sidebar />
    <Workspace />
    <InputBar />
  </div>
</template>

<style>
:root {
  --border-color: #e0e0e0;
  --sidebar-bg: #f8f9fa;
  --workspace-bg: #ffffff;
  --input-bar-bg: #f0f0f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.app-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 1fr 60px;
  height: 100%;
  width: 100%;
}

.app-layout > :nth-child(1) {
  grid-row: 1;
  grid-column: 1;
}

.app-layout > :nth-child(2) {
  grid-row: 1;
  grid-column: 2;
}

.app-layout > :nth-child(3) {
  grid-row: 2;
  grid-column: 1 / -1;
}
</style>
