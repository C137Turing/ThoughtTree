## Context

全新项目，无现有代码库约束。技术栈：Vue 3 + FastAPI + LangGraph + MySQL + Redis。单用户自部署模式。详见 proposal.md - Why。

## Goals / Non-Goals

**Goals:**
- 定义前后端分层架构，明确各层职责边界
- 确定数据模型（MySQL 表结构、Redis 缓存策略）
- 确定 API 通信协议（REST + SSE 流式）
- 确定前端组件树和状态管理架构
- 确定 LangGraph 图结构（对话管理、SDD 生成、质检、建议）

**Non-Goals:**
- 多用户认证与权限系统
- 云端部署与 SaaS 化
- 浏览器扩展形态
- 移动端适配
- CI/CD 流水线

## Decisions

### D-01: 前端架构 — Vue 3 + Pinia + Vue Flow

**决策**: 使用 Vue 3 Composition API + Pinia 状态管理 + Vue Flow 画布库。

**理由**:
- Vue 3 的 `Teleport` + `createApp` API 天然适合动态创建独立窗口实例
- Pinia 的 `setup stores` 模式与 Composition API 风格一致，且支持 `createPinia()` 多次实例化，为每个窗口创建独立 store
- Vue Flow 提供开箱即用的无限画布、节点拖拽、连线功能，避免从零实现画布

**备选方案**:
- React + Zustand：React Portal 共享根上下文，多窗口隔离不如 Vue 的独立 app 实例干净
- 自研画布：开发成本高，Vue Flow 已满足需求

### D-02: 窗口架构 — 每个窗口 = 独立 Vue App 实例

**决策**: 每个浮窗通过 `createApp()` 创建独立的 Vue 应用实例，挂载到动态创建的 DOM 容器上。

**理由**:
- 每个窗口获得完全独立的响应式上下文，避免状态污染
- 窗口销毁时调用 `app.unmount()` 即可完整清理
- 窗口状态（位置、大小、z-index）由全局 `WindowManager`（Pinia store）统一管理

```
WindowManager (全局单例)
├── windows: Map<windowId, WindowState>
│   ├── windowId: string
│   ├── position: {x, y}
│   ├── size: {width, height}
│   ├── zIndex: number
│   ├── rotation: number  // 倾斜角度
│   ├── opacity: number   // 透明度
│   └── status: 'active' | 'minimized' | 'closed'

每个窗口实例内:
├── sessionStore (独立 Pinia) → 会话数据 + 消息列表
├── chatStore (独立 Pinia) → 输入状态 + 流式状态
└── Vue App (独立实例) → 组件树
```

### D-03: 后端架构 — FastAPI + LangGraph 分层

**决策**: 分层架构，API 层负责 CRUD，LangGraph 层负责 AI 逻辑。

```
FastAPI 应用
├── api/
│   ├── sessions.py     → 会话 CRUD + 树结构操作
│   ├── messages.py     → 消息 CRUD + 流式 SSE
│   ├── sdd.py          → SDD 生成触发 + 质检触发
│   └── config.py       → 用户配置（API Key、模型、映射规则）
├── graphs/
│   ├── chat_graph.py   → 对话管理图（每个窗口一个实例）
│   ├── sdd_graph.py    → SDD 生成图（遍历树 + 映射 + 生成）
│   ├── quality_graph.py → 质检图（完整性/一致性/可测试性/EARS）
│   └── suggest_graph.py → 建议生成图（分析树状态）
├── db/
│   ├── mysql.py        → SQLAlchemy + MySQL 连接
│   └── redis.py        → Redis 连接池
└── models/
    ├── session.py      → Session ORM 模型
    ├── message.py      → Message ORM 模型
    └── schemas.py      → Pydantic 请求/响应模型
```

### D-04: 数据模型 — 邻接表 + 闭包表

**决策**: 使用 Adjacency List（parent_id）存储树结构，辅以 Closure Table 支持高效子树查询。

**MySQL 核心表**:

```sql
-- sessions 表
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    parent_id VARCHAR(36) NULL,
    root_id VARCHAR(36) NOT NULL,
    status ENUM('open', 'closed', 'minimized') DEFAULT 'open',
    position_x FLOAT DEFAULT 0,
    position_y FLOAT DEFAULT 0,
    width FLOAT DEFAULT 600,
    height FLOAT DEFAULT 400,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES sessions(id) ON DELETE SET NULL,
    FOREIGN KEY (root_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- messages 表
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    is_quote BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- session_tree 闭包表
CREATE TABLE session_tree (
    ancestor_id VARCHAR(36) NOT NULL,
    descendant_id VARCHAR(36) NOT NULL,
    depth INT NOT NULL DEFAULT 0,
    PRIMARY KEY (ancestor_id, descendant_id),
    FOREIGN KEY (ancestor_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (descendant_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- user_config 表
CREATE TABLE user_config (
    id INT PRIMARY KEY DEFAULT 1,
    api_key_encrypted TEXT,
    active_model VARCHAR(50) DEFAULT 'deepseek',
    ears_enabled BOOLEAN DEFAULT FALSE,
    numbering_style ENUM('standard', 'chinese') DEFAULT 'standard',
    sdd_mapping_rules JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Redis 缓存结构**:

```
window_stack → JSON array [window_id, ...]  // 从底到顶的堆叠顺序
active_windows → Set {window_id, ...}       // 当前活跃窗口 ID 集合
streaming:{window_id} → "1" (TTL 300s)     // 流式请求锁
session:{window_id} → JSON {最近 20 条消息}  // 消息缓存 (TTL 3600s)
```

### D-05: 通信协议 — REST + SSE

**决策**: 常规 CRUD 使用 REST API，AI 流式响应使用 SSE（Server-Sent Events）。

- `POST /api/sessions/{id}/chat` → SSE 流式响应（Content-Type: text/event-stream）
- `GET/POST/PUT/DELETE /api/sessions` → REST CRUD
- `POST /api/sdd/generate` → 触发 SDD 生成（异步，返回 task_id）
- `GET /api/sdd/task/{task_id}` → 轮询 SDD 生成状态
- `POST /api/quality/check` → 触发质检（同步返回报告）

**备选方案**: WebSocket — 更重，对单用户场景过度设计；SSE 足够用且实现更简单。

### D-06: LangGraph 图结构设计

**对话管理图 (chat_graph)**:
```
START → load_history → call_llm → save_message → END
                            ↑          │
                            └──────────┘ (流式循环)
```

**SDD 生成图 (sdd_graph)**:
```
START → traverse_tree → classify_nodes → map_to_ieee830 → generate_sections → assemble_sdd → END
```

**质检图 (quality_graph)**:
```
START → check_completeness ─┐
       → check_consistency ─┼→ aggregate_report → END
       → check_testability ─┤
       → check_ears ────────┘
```

**建议图 (suggest_graph)**:
```
START → analyze_tree_state → detect_gaps → generate_suggestions → END
```

### D-07: 前端组件树

```
App.vue
├── Sidebar.vue
│   ├── TreePanel.vue          → 知识树渲染
│   │   └── TreeNode.vue       → 单节点组件（递归）
│   └── SuggestionPanel.vue    → AI 建议面板
├── Workspace.vue
│   ├── StackArea.vue          → 窗口堆叠区
│   │   └── WindowCard.vue     → 单个窗口卡片（v-for 动态渲染）
│   │       ├── WindowHeader.vue    → 标题栏 + 面包屑 + 操作按钮
│   │       ├── MessageList.vue     → 消息列表
│   │       │   └── MessageItem.vue → 单条消息（Markdown 渲染）
│   │       └── QuoteBlock.vue      → 引用块（长文本划选产物）
│   └── InputBar.vue           → 固定底部输入框
├── CanvasView.vue             → 画布视图（v-if 切换）
│   └── VueFlow 实例
└── SettingsModal.vue          → 设置面板
```

### D-08: 超文本交互实现方案

**名词自动识别**: 后端在 AI 流式响应中返回标记后的文本，标记格式为 `__underline__术语__/underline__`，前端解析为带虚下划线的 `<span>`。

**划选高亮**: `mouseup` 事件 → `window.getSelection()` → 获取选中文本和位置 → 创建高亮覆盖层（绝对定位的 `<div>`，半透明蓝色背景）。

**短/长文本判断**: 选中文本长度 ≤ 50 字符 → 点击创建新窗口；> 50 字符 → 点击插入引用块。

**点击高亮触发**: 在高亮覆盖层上绑定 `click` 事件。点击外部区域通过 `document.addEventListener('click', ...)` 捕获，取消高亮。

## Risks / Trade-offs

- **[风险] 多独立 Vue App 实例内存开销**: 每个窗口一个 Vue 实例，窗口过多时内存压力大 → 缓解：限制同时渲染的窗口实例数（≤ 5），其余通过侧边栏恢复时再创建实例
- **[风险] LangGraph 实例管理**: 每个窗口一个 graph 实例，长时间运行可能积累 → 缓解：实现 graph 实例 LRU 淘汰，非活跃窗口（> 30 分钟无交互）的 graph 实例序列化后释放
- **[风险] 闭包表维护复杂度**: 树结构变更时需同步更新闭包表 → 缓解：封装为数据库触发器或 ORM 事件钩子，应用层透明
- **[取舍] 单用户模式牺牲了协作能力**: 当前版本不支持多人协作 → 可在 MySQL schema 中预留 `user_id` 字段，未来扩展

## Open Questions

- 画布视图中"关联线"是否需要持久化到 MySQL，还是仅作为临时视觉标注？建议 MVP 先做临时标注
- 建议 Agent 的分析频率：实时（每次树变更）还是定时（每 30 秒）？实时分析更灵敏但消耗更多 AI token
- SDD 导出是否需要支持 PDF 格式？Markdown 先行，PDF 可通过浏览器打印或后续引入 Puppeteer 实现
- 用户自建反向代理的部署文档需单独编写，不属于代码实现范围