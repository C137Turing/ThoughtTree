<template>
  <div class="app-layout">
    <Sidebar />
    <div class="main-area">
      <Workspace />
      <InputBar />
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './components/Sidebar.vue'
import Workspace from './components/Workspace.vue'
import InputBar from './components/InputBar.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app-layout { display: flex; height: 100vh; }
.main-area { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
</style>
