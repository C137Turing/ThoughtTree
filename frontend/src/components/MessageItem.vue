<template>
  <div class="message-item" :class="[role, { streaming: isStreaming }]">
    <div class="message-avatar">{{ role === 'user' ? 'U' : 'AI' }}</div>
    <div class="message-body">
      <div class="message-content" ref="contentRef" v-html="renderedContent"></div>
      <div class="message-actions" v-if="role === 'assistant' && !isStreaming">
        <button class="action-btn" @click="$emit('copy')" title="copy">copy</button>
        <button class="action-btn" @click="$emit('regenerate')" title="regenerate">regenerate</button>
      </div>
      <div class="streaming-cursor" v-if="isStreaming">|</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const props = defineProps<{
  role: 'user' | 'assistant' | 'system'
  content: string
  isStreaming?: boolean
}>()

const emit = defineEmits<{
  copy: []
  regenerate: []
  'noun-click': [term: string]
  'text-select': [text: string, isLong: boolean]
}>()

const contentRef = ref<HTMLElement | null>(null)

// Tech dictionary for noun recognition
const TECH_DICT = new Set([
  'API', 'REST', 'GraphQL', 'SSE', 'WebSocket', 'HTTP', 'HTTPS', 'TCP', 'UDP', 'IP', 'DNS',
  'JSON', 'XML', 'YAML', 'CSV', 'SQL', 'NoSQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
  'Docker', 'Kubernetes', 'CI/CD', 'Git', 'GitHub', 'Jenkins',
  'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt',
  'TypeScript', 'JavaScript', 'Python', 'Rust', 'Go', 'Java', 'C#', 'C++', 'Kotlin', 'Swift',
  'Node.js', 'Deno', 'Bun', 'Express', 'FastAPI', 'Django', 'Flask', 'Spring',
  'OAuth', 'JWT', 'CORS', 'CSRF', 'XSS', 'SSL', 'TLS',
  'AWS', 'GCP', 'Azure', 'Vercel', 'Netlify', 'Cloudflare',
  'ORM', 'MVC', 'MVVM', 'Webpack', 'Vite', 'esbuild', 'Babel',
  'DevOps', 'Scrum', 'TDD', 'BDD', 'DDD', 'Nginx',
  'WebRTC', 'gRPC', 'MQTT', 'Kafka', 'RabbitMQ',
  'LLM', 'GPT', 'BERT', 'RAG', 'Embedding',
  'LangChain', 'LangGraph', 'Agent', 'Fine-tuning',
])

// Configure marked with highlight.js
marked.use(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code: string, lang: string) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value
      }
      return hljs.highlightAuto(code).value
    },
  })
)

marked.setOptions({
  breaks: true,
  gfm: true,
})

function wrapTerms(html: string): string {
  // Only wrap in text segments, not inside code/pre/spans/links
  const parts = html.split(/(<pre[^>]*>[\s\S]*?<\/pre>|<code[^>]*>[\s\S]*?<\/code>|<span[^>]*>[\s\S]*?<\/span>|<a[^>]*>[\s\S]*?<\/a>)/g)
  return parts.map((part, i) => {
    if (i % 2 !== 0 || part.startsWith('<')) return part
    let result = part
    for (const term of TECH_DICT) {
      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp('(?<![a-zA-Z0-9\\u4e00-\\u9fff/])(' + escaped + ')(?![a-zA-Z0-9\\u4e00-\\u9fff/])', 'g')
      result = result.replace(regex, '<span class="dashed-underline" data-term="$1">$1</span>')
    }
    return result
  }).join('')
}

const renderedContent = computed(() => {
  if (!props.content) return ''
  try {
    const html = marked.parse(props.content, { async: false })
    if (props.role === 'assistant') {
      return wrapTerms(html as string)
    }
    return html as string
  } catch {
    return props.content.replace(/\n/g, '<br>')
  }
})

function handleClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.classList.contains('dashed-underline')) {
    e.preventDefault()
    e.stopPropagation()
    const term = target.dataset.term || target.textContent || ''
    emit('noun-click', term)
  }
}

function handleMouseUp(_e: MouseEvent) {
  setTimeout(() => {
    const sel = window.getSelection()
    if (!sel || sel.isCollapsed || !sel.toString().trim()) return
    const text = sel.toString().trim()
    if (!text || text.length < 2) return
    const isLong = text.length > 50
    emit('text-select', text, isLong)
  }, 10)
}

onMounted(() => {
  contentRef.value?.addEventListener('click', handleClick)
  contentRef.value?.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  contentRef.value?.removeEventListener('click', handleClick)
  contentRef.value?.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.message-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  animation: fadeIn 0.3s ease;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.system {
  justify-content: center;
  font-size: 12px;
  color: #999;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.user .message-avatar {
  background: #4f46e5;
  color: #fff;
}

.assistant .message-avatar {
  background: #10b981;
  color: #fff;
}

.message-body {
  max-width: 75%;
  position: relative;
}

.user .message-body {
  text-align: right;
}

.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.user .message-content {
  background: #4f46e5;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.assistant .message-content {
  background: #f3f4f6;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.message-content :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-content :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}

.message-content :deep(p code) {
  background: rgba(0,0,0,0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

.message-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.message-content :deep(th),
.message-content :deep(td) {
  border: 1px solid #d1d5db;
  padding: 6px 10px;
  text-align: left;
}

.message-content :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}

.message-content :deep(blockquote) {
  border-left: 3px solid #4f46e5;
  padding-left: 12px;
  margin: 8px 0;
  color: #6b7280;
}

.message-content :deep(.dashed-underline) {
  text-decoration: underline dashed;
  text-decoration-color: #6366f1;
  text-underline-offset: 3px;
  cursor: pointer;
  color: #4f46e5;
  transition: background 0.15s;
}
.message-content :deep(.dashed-underline:hover) {
  background: rgba(99, 102, 241, 0.1);
  border-radius: 2px;
}

:global(.text-highlight-overlay) {
  position: fixed;
  background: rgba(0, 98, 255, 0.15);
  border-radius: 2px;
  pointer-events: auto;
  cursor: pointer;
  z-index: 9999;
  transition: background 0.15s;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-item:hover .message-actions {
  opacity: 1;
}

.action-btn {
  padding: 2px 8px;
  font-size: 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  color: #6b7280;
}

.action-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.streaming-cursor {
  display: inline;
  animation: blink 1s step-end infinite;
  color: #4f46e5;
  font-weight: bold;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
