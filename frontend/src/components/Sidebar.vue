<!-- Sidebar.vue — 侧边栏容器 -->
<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>知识树</h2>
    </div>
    <div class="sidebar-content">
      <p class="placeholder">知识树</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
</script>

<style scoped>
.sidebar {
  width: 280px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg, #f8f9fa);
  border-right: 1px solid var(--border-color, #e0e0e0);
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.sidebar-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.sidebar-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.placeholder {
  color: #999;
  font-size: 14px;
  text-align: center;
  margin-top: 40px;
}
</style>