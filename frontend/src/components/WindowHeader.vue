<template>
  <div class="window-header" ref="headerRef">
    <div class="window-title-area">
      <span class="window-title">{{ title }}</span>
      <span class="breadcrumb" v-if="breadcrumb.length">
        <template v-for="(node, i) in breadcrumb" :key="node.id">
          <span v-if="i > 0" class="breadcrumb-sep">/</span>
          <span class="breadcrumb-node" @click="$emit('breadcrumb-click', node.id)">{{ node.title }}</span>
        </template>
      </span>
    </div>
    <div class="window-actions">
      <button class="win-btn" @click="$emit('minimize')" title="minimize">—</button>
      <button class="win-btn" @click="$emit('close')" title="close">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
  breadcrumb: { id: string; title: string }[]
}>()

defineEmits<{
  minimize: []
  close: []
  'breadcrumb-click': [id: string]
}>()

const headerRef = ref<HTMLElement | null>(null)
defineExpose({ headerRef })
</script>

<style scoped>
.window-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px 10px 0 0;
  cursor: grab;
  user-select: none;
  min-height: 36px;
}

.window-header:active {
  cursor: grabbing;
}

.window-title-area {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.window-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.breadcrumb {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.breadcrumb-sep {
  margin: 0 4px;
}

.breadcrumb-node {
  cursor: pointer;
  text-decoration: underline dotted;
}

.breadcrumb-node:hover {
  color: #fff;
}

.window-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.win-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: rgba(255,255,255,0.2);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.win-btn:hover {
  background: rgba(255,255,255,0.4);
}
</style>
