## Purpose

将每个窗口自动组织为树形知识结构，父子关系由划词创建行为绑定，侧边栏以树形展示所有节点的状态和层级关系。

## ADDED Requirements

### Requirement: 父子节点自动绑定

系统 SHALL 在窗口 A 中通过划词创建窗口 B 时，自动将窗口 B 记录为窗口 A 的子节点。

#### Scenario: 划词创建自动绑定父子关系

- **WHEN** 用户在窗口 A 中划词并创建了窗口 B
- **THEN** 系统 SHALL 自动记录窗口 B 的 parent_id 为窗口 A 的 id，并计算窗口 B 的 root_id

#### Scenario: 根节点创建

- **WHEN** 用户通过主界面创建了一个顶级话题（非划词创建）
- **THEN** 该窗口 SHALL 的 parent_id 为 null，root_id 指向自身

### Requirement: 树形侧边栏

系统 SHALL 在页面左侧常驻一个侧边栏，以树形缩进结构展示所有会话节点。

#### Scenario: 节点层级缩进

- **WHEN** 侧边栏渲染知识树
- **THEN** 子节点 SHALL 相对于父节点以缩进方式展示，清晰表达层级关系

#### Scenario: 节点状态视觉区分

- **WHEN** 侧边栏渲染节点
- **THEN** "打开中"的节点 SHALL 以亮色/高亮样式显示，"已关闭"的节点 SHALL 以灰色/半透明样式显示

#### Scenario: 点击已关闭节点恢复窗口

- **WHEN** 用户点击侧边栏中"已关闭"的节点
- **THEN** 系统 SHALL 从持久化存储中读取该节点的完整对话历史，在前端渲染恢复窗口

### Requirement: 面包屑路径导航

系统 SHALL 在每个窗口的顶部区域展示该窗口在知识树中的面包屑路径。

#### Scenario: 面包屑显示

- **WHEN** 窗口渲染
- **THEN** 窗口顶部 SHALL 显示从根节点到当前节点的完整路径，格式为"根 / 父 / 当前"

#### Scenario: 点击面包屑跳转

- **WHEN** 用户点击面包屑中的某个祖先节点
- **THEN** 对应窗口 SHALL 成为前台窗口

### Requirement: 节点删除与子节点提升

系统 SHALL 在删除节点时将其所有子节点的 parent_id 提升至被删除节点的父级。

#### Scenario: 删除中间节点

- **WHEN** 用户删除知识树中的某个中间节点
- **THEN** 该节点的所有直接子节点 SHALL 的 parent_id 更新为该节点的 parent_id

#### Scenario: 删除叶子节点

- **WHEN** 用户删除知识树中的叶子节点
- **THEN** 该节点 SHALL 直接移除，不影响其他节点

### Requirement: 伪关闭机制

系统 SHALL 在用户关闭窗口时仅销毁 DOM 元素，后台保留该窗口的全部对话记录和状态。

#### Scenario: 关闭窗口

- **WHEN** 用户点击窗口的关闭按钮
- **THEN** 窗口 DOM SHALL 从界面移除，但数据保留在 MySQL，节点状态更新为"已关闭"

#### Scenario: 恢复已关闭窗口

- **WHEN** 用户通过侧边栏恢复一个"已关闭"的窗口
- **THEN** 窗口 SHALL 完整恢复，对话历史与关闭前完全一致