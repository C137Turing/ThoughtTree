<template>
  <div>
    <div
      class="tree-node"
      :class="{ active: node.session.status === 'open', closed: node.session.status === 'closed', minimized: node.session.status === 'minimized' }"
      :style="{ paddingLeft: (node.depth * 16 + 12) + 'px' }"
      @click="$emit('click')"
      @contextmenu.prevent="$emit('delete', $event)"
    >
      <span class="node-status" :title="node.session.status">
        {{ node.session.status === 'open' ? '\u25CF' : node.session.status === 'minimized' ? '\u2014' : '\u25CB' }}
      </span>
      <span class="node-title">{{ node.session.title }}</span>
    </div>
    <TreeNode
      v-for="child in node.children"
      :key="child.session.id"
      :node="child"
      @click="(s: any) => $emit('click', s)"
      @delete="(e: any) => $emit('delete', e)"
    />
  </div>
</template>

<script setup lang="ts">
import type { SessionInfo } from '../stores/sessions'

interface TreeNode { session: SessionInfo; children: TreeNode[]; depth: number }

defineProps<{ node: TreeNode }>()

defineEmits<{
  click: [session?: SessionInfo]
  delete: [event: Event]
}>()
</script>

<style scoped>
.tree-node {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; border-radius: 6px; cursor: pointer;
  font-size: 13px; transition: background 0.15s;
  color: #cdd6f4;
}
.tree-node:hover { background: #313244; }
.tree-node.active { background: #45475a; color: #fff; }
.tree-node.closed { opacity: 0.5; }
.tree-node.minimized { opacity: 0.7; font-style: italic; }
.node-status { font-size: 10px; width: 16px; text-align: center; flex-shrink: 0; }
.tree-node.active .node-status { color: #a6e3a1; }
.tree-node.closed .node-status { color: #6c7086; }
.tree-node.minimized .node-status { color: #f9e2af; }
.node-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
