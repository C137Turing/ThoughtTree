## Purpose

在侧边栏常驻 AI 建议面板，后台持续分析知识树状态，检测遗漏维度、冲突方案和悬空节点，主动向用户推荐探索方向。

## ADDED Requirements

### Requirement: 建议面板常驻

系统 SHALL 在侧边栏下部常驻一个 AI 建议面板。

#### Scenario: 建议面板位置

- **WHEN** 用户打开应用
- **THEN** 侧边栏 SHALL 包含两部分：上部为知识树，下部为 AI 建议面板

#### Scenario: 折叠建议面板

- **WHEN** 用户点击建议面板的折叠按钮
- **THEN** 建议面板 SHALL 折叠为仅显示标题栏，点击展开后恢复

### Requirement: 遗漏维度检测

系统 SHALL 分析知识树结构，检测可能遗漏的需求维度并主动建议。

#### Scenario: 检测遗漏维度

- **WHEN** AI 建议 Agent 分析后发现用户已探索了部分功能但未涉及相关维度
- **THEN** 建议面板 SHALL 显示建议内容并附带"帮我分析"按钮

#### Scenario: 用户采纳建议

- **WHEN** 用户点击建议面板中的"帮我分析"按钮
- **THEN** 系统 SHALL 自动创建新的子窗口，AI 开始分析该维度

### Requirement: 悬空节点提醒

系统 SHALL 持续检测知识树中的悬空节点并提醒。

#### Scenario: 悬空节点计数

- **WHEN** 知识树中存在悬空节点
- **THEN** 建议面板 SHALL 显示悬空节点数量和名称

### Requirement: 探索停滞检测

系统 SHALL 在用户长时间未活动时给出探索建议。

#### Scenario: 探索停滞提示

- **WHEN** 用户在过去 5 分钟内未创建新节点且未发送任何消息
- **THEN** 建议面板 SHALL 显示温和的探索建议

### Requirement: 建议面板不打断用户

系统 SHALL 确保建议面板的内容更新不打断用户当前操作。

#### Scenario: 用户专注时建议不弹窗

- **WHEN** 用户正在输入框中打字或正在阅读 AI 回复
- **THEN** 建议面板 SHALL 仅静默更新内容，不弹出模态框或打断性提示