<template>
  <div class="settings-overlay" @click.self="$emit('close')">
    <div class="settings-panel">
      <h3>Settings</h3>
      <div class="setting-group">
        <label>Model</label>
        <select v-model="config.active_model" @change="save">
          <option value="deepseek-v4-flash">DeepSeek v4 Flash</option>
          <option value="deepseek-v4-pro">DeepSeek v4 Pro</option>
          <option value="gpt-4o">GPT-4o</option>
          <option value="claude-sonnet-5">Claude Sonnet 5</option>
        </select>
      </div>
      <div class="setting-group">
        <label>API Key</label>
        <input type="password" v-model="config.api_key_encrypted" placeholder="Enter API key" @blur="save" />
      </div>
      <div class="setting-group">
        <label>Numbering Style</label>
        <select v-model="config.numbering_style" @change="save">
          <option value="standard">Standard (1, 1.1, 1.1.1)</option>
          <option value="chinese">Chinese</option>
        </select>
      </div>
      <div class="setting-group">
        <label>EARS Format</label>
        <input type="checkbox" v-model="config.ears_enabled" @change="save" />
      </div>
      <button class="close-btn" @click="$emit('close')">Close</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineEmits<{ close: [] }>()

const config = ref({
  active_model: 'deepseek-v4-flash',
  api_key_encrypted: '',
  numbering_style: 'standard',
  ears_enabled: false,
})

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/config/')
    const data = await res.json()
    config.value = { ...config.value, ...data }
  } catch { }
})

async function save() {
  await fetch('http://localhost:8000/api/config/', {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config.value),
  })
}
</script>

<style scoped>
.settings-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 10001; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }
.settings-panel { background: #fff; border-radius: 12px; padding: 24px; width: 400px; max-height: 80vh; overflow-y: auto; }
.settings-panel h3 { margin-bottom: 16px; color: #1e293b; }
.setting-group { margin-bottom: 14px; }
.setting-group label { display: block; font-size: 13px; color: #64748b; margin-bottom: 4px; }
.setting-group select, .setting-group input[type="password"] { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; }
.setting-group input[type="checkbox"] { width: 18px; height: 18px; }
.close-btn { margin-top: 12px; padding: 8px 20px; border: 1px solid #cbd5e1; border-radius: 6px; background: #fff; cursor: pointer; }
</style>