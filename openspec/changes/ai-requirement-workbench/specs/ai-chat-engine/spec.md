## Purpose

基于 LangGraph 提供多轮对话引擎，每个窗口拥有独立的对话上下文，支持流式响应、Markdown 渲染和代码语法高亮。

## ADDED Requirements

### Requirement: 独立窗口对话上下文

系统 SHALL 为每个窗口维护独立的 LangGraph 对话实例，各窗口的对话历史互不干扰。

#### Scenario: 多窗口独立对话

- **WHEN** 用户在窗口 A 和窗口 B 中分别发送消息
- **THEN** 每个窗口的 AI 回复 SHALL 仅基于该窗口的历史上下文

#### Scenario: 上下文继承

- **WHEN** 窗口 B 是通过窗口 A 划词创建的
- **THEN** 窗口 B 的初始上下文 SHALL 包含划词选中的文本

### Requirement: 流式响应

系统 SHALL 以流式方式逐字/逐句渲染 AI 回复。

#### Scenario: 流式渲染

- **WHEN** AI 开始生成回复
- **THEN** 回复内容 SHALL 以逐 token 方式在前端渲染

#### Scenario: 流式中断

- **WHEN** 流式响应过程中用户关闭了窗口
- **THEN** 后端 SHALL 继续完成请求并保存到数据库，但前端不再渲染

### Requirement: Markdown 渲染与代码高亮

系统 SHALL 完整支持 Markdown 语法渲染，代码块须具备语法高亮。

#### Scenario: Markdown 渲染

- **WHEN** AI 回复包含 Markdown 格式内容
- **THEN** 前端 SHALL 正确渲染为对应 HTML 格式

#### Scenario: 代码块语法高亮

- **WHEN** AI 回复包含代码块
- **THEN** 代码块 SHALL 以语法高亮方式渲染

### Requirement: 消息操作

系统 SHALL 支持用户复制 AI 回复和重新生成回答。

#### Scenario: 复制 AI 回复

- **WHEN** 用户对某条 AI 回复执行复制操作
- **THEN** 该回复的纯文本内容 SHALL 被复制到剪贴板

#### Scenario: 重新生成回答

- **WHEN** 用户对某条 AI 回复点击"重新生成"
- **THEN** 系统 SHALL 重新发起请求，生成新回复替换当前回复

### Requirement: 多模型接入

系统 SHALL 支持用户配置并切换不同的 AI 大模型 API。

#### Scenario: 切换模型

- **WHEN** 用户在设置中选择不同的 AI 模型
- **THEN** 后续所有对话请求 SHALL 使用所选模型