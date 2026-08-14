## Purpose

使用 MySQL 存储所有永久数据（会话、消息、树结构），Redis 缓存活跃窗口状态和堆叠顺序，确保数据安全且可快速恢复。

## ADDED Requirements

### Requirement: MySQL 永久存储

系统 SHALL 使用 MySQL 存储所有永久数据，包括会话、消息和树结构。

#### Scenario: 会话持久化

- **WHEN** 用户创建新窗口或发送消息
- **THEN** 对应的会话和消息 SHALL 立即写入 MySQL

#### Scenario: 树结构持久化

- **WHEN** 窗口的父级关系建立或变更
- **THEN** 树结构变化 SHALL 立即写入 MySQL

#### Scenario: 数据恢复

- **WHEN** 用户关闭浏览器后重新打开应用
- **THEN** 系统 SHALL 从 MySQL 读取所有数据，恢复侧边栏树结构

### Requirement: Redis 活跃状态缓存

系统 SHALL 使用 Redis 缓存当前活跃窗口的状态信息。

#### Scenario: 窗口堆叠顺序缓存

- **WHEN** 窗口的堆叠顺序发生变化
- **THEN** 变更 SHALL 立即写入 Redis

#### Scenario: 活跃窗口列表缓存

- **WHEN** 窗口打开或关闭
- **THEN** 活跃窗口 ID 列表 SHALL 更新到 Redis

#### Scenario: 流式请求状态缓存

- **WHEN** 某个窗口正在进行 AI 流式请求
- **THEN** Redis SHALL 记录该窗口的流式状态，防止重复请求，TTL 为 5 分钟

### Requirement: Redis 数据过期与重建

系统 SHALL 在 Redis 数据丢失时能自动从 MySQL 重建缓存。

#### Scenario: Redis 清空后重建

- **WHEN** Redis 服务重启导致缓存数据丢失
- **THEN** 系统 SHALL 从 MySQL 读取所有"打开中"的会话，重建活跃窗口缓存

### Requirement: 本地优先原则

系统 SHALL 将所有数据存储在用户本地环境，不上传任何数据到云端。

#### Scenario: API Key 本地存储

- **WHEN** 用户配置 API Key
- **THEN** API Key SHALL 仅存储在本地 MySQL 中

#### Scenario: 数据完全本地化

- **WHEN** 用户使用应用的所有功能
- **THEN** 所有数据 SHALL 仅存储在用户自部署的 MySQL 和 Redis 中

### Requirement: 单用户模式

系统 SHALL 当前仅支持单用户模式，不涉及多用户账户管理。

#### Scenario: 无用户认证

- **WHEN** 用户访问应用
- **THEN** 系统 SHALL 直接进入工作台界面，无需登录或注册