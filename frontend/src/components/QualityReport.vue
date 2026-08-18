<template>
  <div class="qr-overlay" @click.self="$emit('close')">
    <div class="qr-panel">
      <h2>Quality Check Report</h2>
      <div class="qr-section" v-for="check in checks" :key="check.key">
        <div class="qr-header" :class="check.passed ? 'pass' : 'fail'">
          {{ check.passed ? 'PASS' : 'FAIL' }} {{ check.label }}
        </div>
        <div class="qr-summary">{{ check.summary }}</div>
        <div v-if="check.issues.length" class="qr-issues">
          <div v-for="(issue, i) in check.issues" :key="i" class="qr-issue">
            <span class="qr-severity" :class="issue.severity">{{ issue.severity === 'warning' ? '!' : 'i' }}</span>
            {{ issue.message }}
            <button class="qr-fix-btn" @click="$emit('fix', issue)">Fix</button>
          </div>
        </div>
      </div>
      <div class="qr-actions">
        <button class="qr-btn primary" @click="$emit('continue')">Continue generating SDD</button>
        <button class="qr-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ report: any }>()

defineEmits<{ close: []; continue: []; fix: [issue: any] }>()

const checks = computed(() => [
  {
    key: 'completeness', label: 'Completeness',
    passed: props.report?.completeness?.passed ?? false,
    summary: props.report?.completeness?.summary ?? '',
    issues: props.report?.completeness?.issues ?? [],
  },
  {
    key: 'consistency', label: 'Consistency',
    passed: props.report?.consistency?.passed ?? false,
    summary: props.report?.consistency?.summary ?? '',
    issues: props.report?.consistency?.issues ?? [],
  },
  {
    key: 'testability', label: 'Testability',
    passed: props.report?.testability?.passed ?? false,
    summary: props.report?.testability?.summary ?? '',
    issues: props.report?.testability?.issues ?? [],
  },
  {
    key: 'ears', label: 'EARS Compliance',
    passed: props.report?.ears?.passed ?? false,
    summary: props.report?.ears?.summary ?? '',
    issues: [],
  },
])
</script>

<style scoped>
.qr-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10001; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; }
.qr-panel { background: #fff; border-radius: 12px; padding: 24px; width: 520px; max-height: 80vh; overflow-y: auto; }
.qr-panel h2 { margin-bottom: 16px; color: #1e293b; font-size: 18px; }
.qr-section { margin-bottom: 14px; padding: 12px; border-radius: 8px; background: #f8fafc; }
.qr-header { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.qr-header.pass { color: #16a34a; }
.qr-header.fail { color: #dc2626; }
.qr-summary { font-size: 13px; color: #475569; margin-bottom: 6px; }
.qr-issues { margin-top: 6px; }
.qr-issue { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #64748b; padding: 4px 0; }
.qr-severity { width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0; }
.qr-severity.warning { background: #fef3c7; color: #d97706; }
.qr-severity.info { background: #dbeafe; color: #2563eb; }
.qr-fix-btn { margin-left: auto; padding: 2px 10px; border: 1px solid #cbd5e1; border-radius: 4px; background: #fff; font-size: 11px; cursor: pointer; }
.qr-fix-btn:hover { background: #f1f5f9; }
.qr-actions { display: flex; gap: 8px; margin-top: 16px; justify-content: flex-end; }
.qr-btn { padding: 8px 20px; border: 1px solid #cbd5e1; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; }
.qr-btn.primary { background: #4f46e5; color: #fff; border-color: #4f46e5; }
</style>