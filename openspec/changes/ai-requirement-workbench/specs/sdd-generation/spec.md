## Purpose

遍历知识树，自动将节点内容映射到 IEEE 830 标准章节，生成结构化的软件设计文档（SDD），支持用户自定义映射规则和格式选项。

## ADDED Requirements

### Requirement: IEEE 830 默认映射

系统 SHALL 内置 IEEE 830 标准章节结构，并在生成 SDD 时自动将知识树节点映射到对应章节。

#### Scenario: 默认章节映射

- **WHEN** 用户点击"生成 SDD"且未设置自定义映射规则
- **THEN** 系统 SHALL 按默认规则映射：根节点 → 引言，功能拆解节点 → 具体需求，带特定标签的节点 → 非功能需求/外部接口，未解决节点 → 附录待确认项

#### Scenario: 节点层级对应章节编号

- **WHEN** 知识树节点层级为三层
- **THEN** 生成的 SDD 中对应章节编号 SHALL 按层级自动缩进编号

### Requirement: 自定义映射规则

系统 SHALL 提供界面让用户自定义节点到 SDD 章节的映射规则。

#### Scenario: 创建自定义标签映射

- **WHEN** 用户在设置中创建自定义标签并指定目标章节
- **THEN** 生成 SDD 时，所有带有该标签的节点 SHALL 归入指定章节

#### Scenario: 拖拽式映射配置

- **WHEN** 用户在映射配置界面通过拖拽方式关联标签和章节
- **THEN** 映射规则 SHALL 被保存并应用于后续 SDD 生成

### Requirement: 编号样式选择

系统 SHALL 支持用户选择章节编号样式。

#### Scenario: 标准数字编号

- **WHEN** 用户选择"标准"编号样式
- **THEN** 章节 SHALL 按"1, 1.1, 1.1.1"格式编号

#### Scenario: 中文编号

- **WHEN** 用户选择"中文"编号样式
- **THEN** 章节 SHALL 按"一、1.（1）"格式编号

### Requirement: EARS 格式开关

系统 SHALL 提供 EARS 语法开关，开启后 AI 将用 EARS 格式重写需求条目。

#### Scenario: EARS 模式开启

- **WHEN** 用户开启 EARS 语法开关
- **THEN** 生成的 SDD 中功能需求条目 SHALL 以 EARS 格式呈现

#### Scenario: EARS 模式关闭

- **WHEN** 用户关闭 EARS 语法开关
- **THEN** 功能需求 SHALL 以自然语言形式呈现

### Requirement: SDD 预览与导出

系统 SHALL 在生成 SDD 后提供预览界面，并支持导出为 Markdown 文件。

#### Scenario: SDD 预览

- **WHEN** SDD 生成完成
- **THEN** 系统 SHALL 渲染完整 SDD 文档，支持章节折叠和导航

#### Scenario: 导出 Markdown

- **WHEN** 用户点击"导出 SDD"
- **THEN** 系统 SHALL 将 SDD 保存为 Markdown 文件并触发浏览器下载