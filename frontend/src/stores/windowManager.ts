import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** 窗口状态 */
export interface WindowState {
  id: string
  title: string
  position: { x: number; y: number }
  size: { width: number; height: number }
  zIndex: number
  rotation: number    // 倾斜角度，默认 0
  opacity: number     // 透明度，默认 1
  grayscale: number   // 灰度，默认 0
  scale: number       // 缩放，默认 1
  status: 'active' | 'minimized' | 'closed'
}

export const useWindowManager = defineStore('windowManager', () => {
  // --- State ---
  const windows = ref<Map<string, WindowState>>(new Map())
  const nextZIndex = ref(1)

  // --- Getters ---
  const activeWindows = computed(() =>
    Array.from(windows.value.values()).filter(
      (w) => w.status === 'active'
    )
  )

  const minimizedWindows = computed(() =>
    Array.from(windows.value.values()).filter(
      (w) => w.status === 'minimized'
    )
  )

  const windowsByZIndex = computed(() =>
    [...activeWindows.value].sort((a, b) => a.zIndex - b.zIndex)
  )

  const topWindow = computed(() =>
    activeWindows.value.reduce(
      (top, w) => (w.zIndex > (top?.zIndex ?? -1) ? w : top),
      null as WindowState | null
    )
  )

  function getWindow(id: string): WindowState | undefined {
    return windows.value.get(id)
  }

  // --- Actions ---

  /**
   * 创建并激活窗口。
   * 新窗口获得最高 zIndex，旧窗口倾斜变灰退后。
   */
  function addWindow(id: string, title: string): WindowState {
    // 将当前所有活跃窗口倾斜退后
    for (const w of windows.value.values()) {
      if (w.status === 'active') {
        w.rotation = -3
        w.grayscale = 0.6
        w.scale = 0.95
        w.opacity = 0.6
      }
    }

    const win: WindowState = {
      id,
      title,
      position: { x: 100, y: 80 },
      size: { width: 600, height: 400 },
      zIndex: nextZIndex.value++,
      rotation: 0,
      opacity: 1,
      grayscale: 0,
      scale: 1,
      status: 'active',
    }

    windows.value.set(id, win)
    return win
  }

  /**
   * 移除窗口（关闭）。
   * 状态标记为 closed，数据保留在 MySQL 中。
   */
  function removeWindow(id: string): void {
    const win = windows.value.get(id)
    if (win) {
      win.status = 'closed'
      windows.value.delete(id)
    }
  }

  /**
   * 将窗口置顶。
   * 目标窗口飞回正位，当前前台窗口倾斜退后。
   */
  function focusWindow(id: string): void {
    const target = windows.value.get(id)
    if (!target || target.status !== 'active') return

    // 当前前台窗口倾斜退后
    for (const w of windows.value.values()) {
      if (w.status === 'active' && w.id !== id) {
        w.rotation = -3
        w.grayscale = 0.6
        w.scale = 0.95
        w.opacity = 0.6
      }
    }

    // 目标窗口飞回正位
    target.zIndex = nextZIndex.value++
    target.rotation = 0
    target.grayscale = 0
    target.scale = 1
    target.opacity = 1
  }

  /**
   * 最小化窗口。
   * 窗口从堆叠区消失，侧边栏标记为"已折叠"。
   */
  function minimizeWindow(id: string): void {
    const win = windows.value.get(id)
    if (win) {
      win.status = 'minimized'
    }
  }

  /**
   * 更新窗口位置。
   */
  function updateWindowPosition(id: string, x: number, y: number): void {
    const win = windows.value.get(id)
    if (win) {
      win.position = { x, y }
    }
  }

  /**
   * 更新窗口尺寸。
   */
  function updateWindowSize(id: string, width: number, height: number): void {
    const win = windows.value.get(id)
    if (win) {
      win.size = { width, height }
    }
  }

  return {
    // State
    windows,
    nextZIndex,
    // Getters
    activeWindows,
    minimizedWindows,
    windowsByZIndex,
    topWindow,
    getWindow,
    // Actions
    addWindow,
    removeWindow,
    focusWindow,
    minimizeWindow,
    updateWindowPosition,
    updateWindowSize,
  }
})
