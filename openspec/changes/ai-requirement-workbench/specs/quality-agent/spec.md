## Purpose

在 SDD 生成前执行完整性、一致性、可测试性和 EARS 合规率检查，生成质检报告，帮助用户发现需求中的遗漏、冲突和模糊之处。

## ADDED Requirements

### Requirement: 完整性检查

系统 SHALL 在 SDD 生成前遍历知识树，检测所有叶子节点是否拥有明确的结论。

#### Scenario: 发现悬空节点

- **WHEN** 质检 Agent 检测到存在未解答或结论不明确的叶子节点
- **THEN** 质检报告 SHALL 列出所有悬空节点，在侧边栏对应节点上显示红色警告角标

#### Scenario: 无悬空节点

- **WHEN** 质检 Agent 遍历完成，所有叶子节点均有明确结论
- **THEN** 完整性检查 SHALL 标记为"通过"

### Requirement: 一致性检查

系统 SHALL 检测知识树中是否存在描述同一功能但方案冲突的节点。

#### Scenario: 发现方案冲突

- **WHEN** 质检 Agent 检测到两个节点描述了同一功能的冲突方案
- **THEN** 质检报告 SHALL 在"待确认问题"中生成条目，描述冲突内容

#### Scenario: 无冲突

- **WHEN** 质检 Agent 未发现方案冲突
- **THEN** 一致性检查 SHALL 标记为"通过"

### Requirement: 可测试性检查

系统 SHALL 扫描需求描述中的模糊词汇，提示用户量化。

#### Scenario: 发现模糊词汇

- **WHEN** 质检 Agent 检测到模糊词汇（如"快速"、"友好"、"高效"）
- **THEN** 质检报告 SHALL 列出所有模糊词汇，建议具体量化方案

#### Scenario: 高亮模糊词汇

- **WHEN** SDD 预览中显示质检报告
- **THEN** 模糊词汇 SHALL 在文本中以黄色下划线高亮，悬停显示量化建议

### Requirement: EARS 合规率评估

系统 SHALL 统计功能需求中符合 EARS 格式的条目比例。

#### Scenario: 计算 EARS 合规率

- **WHEN** 质检 Agent 完成分析
- **THEN** 质检报告头部 SHALL 显示 EARS 合规率评分

### Requirement: 质检报告交互

系统 SHALL 在质检报告中提供交互式修复入口。

#### Scenario: 用户选择修复问题

- **WHEN** 用户在质检报告中点击"去解决"
- **THEN** 系统 SHALL 自动创建子窗口，向 AI 发起追问

#### Scenario: 用户跳过问题

- **WHEN** 用户选择"继续生成 SDD"
- **THEN** 系统 SHALL 直接进入 SDD 生成流程，不强制修复

### Requirement: 质检触发时机

系统 SHALL 仅在用户点击"生成 SDD"按钮后、实际生成文档前执行质检。

#### Scenario: 生成前质检

- **WHEN** 用户点击"生成 SDD"按钮
- **THEN** 系统 SHALL 先执行质检 Agent 完成所有检查，展示质检报告，用户确认后再生成 SDD