<!-- Workspace.vue — 工作区容器 -->
<template>
  <main class="workspace">
    <div class="workspace-placeholder">
      <p>工作区</p>
    </div>
  </main>
</template>

<script setup lang="ts">
</script>

<style scoped>
.workspace {
  flex: 1;
  height: 100%;
  position: relative;
  overflow: hidden;
  background: var(--workspace-bg, #ffffff);
}

.workspace-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #ccc;
  font-size: 24px;
  user-select: none;
}
</style>