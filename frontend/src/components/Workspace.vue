<template>
  <div class="workspace">
    <StackArea />
  </div>
</template>

<script setup lang="ts">
import StackArea from './StackArea.vue'
</script>

<style scoped>
.workspace {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}
</style>
