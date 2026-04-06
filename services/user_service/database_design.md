# U分U享 - 数据库设计文档

## 📊 设计理念

本项目采用**微服务架构**，数据库设计遵循**敏捷开发**和**迭代交付**原则，按功能模块分阶段实施。

## 🎯 分阶段实施策略

### 阶段一：用户认证系统（✅ 已完成）
**时间**：Week 1-2  
**目标**：建立完整的用户体系和 JWT 认证机制

### 阶段二：垃圾分类识别（🔄 进行中）
**时间**：Week 3-4（当前阶段）  
**目标**：实现核心业务功能，记录用户分类行为数据

### 阶段三：积分与激励系统（📅 计划中）
**时间**：Week 5-6  
**目标**：提升用户活跃度和粘性

---

## 📋 数据表设计清单

| 表名 | 状态 | 用途 |
|------|------|------|
| users | ✅ 已创建 | 用户基本信息和认证 |
| user_profiles | 🔄 设计完成 | 用户详细资料扩展 |
| classification_records | 🔄 设计完成 | 垃圾分类识别记录 |
| user_points | 📅 设计完成 | 用户积分变动历史 |
| ai_chat_history | 📅 设计完成 | AI助手对话记录 |

**说明**：站点信息（垃圾投放点）采用文件存储方式（Excel/CSV），不纳入数据库管理。

---

## 📋 详细表结构设计

### ✅ 已实施的表

#### 1. users（用户表）

**功能**：存储用户基本信息和认证凭证

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, IDENTITY | 用户唯一标识 |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | 用户名 |
| hashed_password | VARCHAR(255) | NOT NULL | 密码哈希值（bcrypt加密） |

**索引**：
- PRIMARY KEY: `id`
- UNIQUE INDEX: `username`

**安全设计**：
- 密码使用 bcrypt 哈希加密
- 用户名建立唯一索引，防止重复注册
- 使用 JWT Token 进行身份认证

**状态**：✅ 已创建并投入使用

---

### 🔄 待实施的表（已完成设计）

#### 2. classification_records（分类记录表）

**功能**：记录用户每次垃圾分类识别的详细信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, IDENTITY | 记录唯一标识 |
| user_id | INT | NOT NULL, FOREIGN KEY | 关联用户ID |
| garbage_name | NVARCHAR(100) | NOT NULL | 垃圾名称 |
| garbage_category | VARCHAR(50) | NOT NULL | 垃圾分类（recyclable/harmful/kitchen/other） |
| classification_method | VARCHAR(20) | NOT NULL | 识别方式（text/voice/image） |
| confidence | FLOAT | NULL | AI识别置信度（0-1） |
| image_url | VARCHAR(500) | NULL | 图片存储路径（仅图像识别） |
| recognition_result | NVARCHAR(MAX) | NULL | 完整识别结果（JSON格式） |
| created_at | DATETIME | DEFAULT GETDATE() | 记录创建时间 |

**索引设计**：
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` REFERENCES users(id)
- INDEX: `user_id, created_at` （用于查询用户历史记录）
- INDEX: `garbage_category` （用于统计分析）

**实施时机**：垃圾分类识别功能上线时创建

---

#### 3. user_points（用户积分表）

**功能**：记录用户积分变动历史，实现激励机制

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, IDENTITY | 记录唯一标识 |
| user_id | INT | NOT NULL, FOREIGN KEY | 关联用户ID |
| points_change | INT | NOT NULL | 积分变动值（正数为增加，负数为减少） |
| current_points | INT | NOT NULL | 变动后的总积分 |
| reason | NVARCHAR(200) | NOT NULL | 积分变动原因 |
| reference_type | VARCHAR(50) | NULL | 关联类型（classification/daily_login/activity） |
| reference_id | BIGINT | NULL | 关联记录ID |
| created_at | DATETIME | DEFAULT GETDATE() | 记录创建时间 |

**索引设计**：
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` REFERENCES users(id)
- INDEX: `user_id, created_at` （用于查询积分历史）

**业务规则**：
- 每次正确分类：+5 积分
- 连续登录 7 天：+20 积分
- 每日首次使用：+2 积分

**实施时机**：积分系统功能开发时创建

---

#### 4. ai_chat_history（AI对话历史表）

**功能**：存储用户与AI助手的对话记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, IDENTITY | 记录唯一标识 |
| user_id | INT | NOT NULL, FOREIGN KEY | 关联用户ID |
| conversation_id | VARCHAR(100) | NOT NULL | 会话ID（同一次对话共享） |
| role | VARCHAR(20) | NOT NULL | 角色（user/assistant/system） |
| content | NVARCHAR(MAX) | NOT NULL | 消息内容 |
| created_at | DATETIME | DEFAULT GETDATE() | 消息发送时间 |

**索引设计**：
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` REFERENCES users(id)
- INDEX: `conversation_id, created_at` （用于加载对话上下文）
- INDEX: `user_id, created_at` （用于查询用户对话历史）

**实施时机**：AI对话功能需要持久化存储时创建

---

#### 5. recycling_stations（回收站点表）

**功能**：存储校园内垃圾回收站点信息（可选功能）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, IDENTITY | 站点唯一标识 |
| name | NVARCHAR(100) | NOT NULL | 站点名称 |
| location | NVARCHAR(200) | NOT NULL | 位置描述 |
| latitude | DECIMAL(10,6) | NULL | 纬度 |
| longitude | DECIMAL(10,6) | NULL | 经度 |
| available_categories | VARCHAR(200) | NOT NULL | 支持的垃圾类别（JSON数组） |
| opening_hours | NVARCHAR(100) | NULL | 开放时间 |
| created_at | DATETIME | DEFAULT GETDATE() | 创建时间 |
| updated_at | DATETIME | DEFAULT GETDATE() | 更新时间 |

**实施时机**：地图导航功能开发时创建（可选）

---

#### 6. user_profiles（用户扩展信息表）

**功能**：存储用户详细资料和偏好设置

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | INT | PRIMARY KEY, FOREIGN KEY | 关联用户ID |
| nickname | NVARCHAR(50) | NULL | 昵称 |
| avatar_url | VARCHAR(500) | NULL | 头像URL |
| email | VARCHAR(100) | NULL | 邮箱 |
| phone | VARCHAR(20) | NULL | 手机号 |
| campus | NVARCHAR(50) | NULL | 所在校区 |
| total_points | INT | DEFAULT 0 | 总积分 |
| classification_count | INT | DEFAULT 0 | 累计分类次数 |
| is_active | BIT | DEFAULT 1 | 账户状态 |
| last_login_at | DATETIME | NULL | 最后登录时间 |
| created_at | DATETIME | DEFAULT GETDATE() | 创建时间 |
| updated_at | DATETIME | DEFAULT GETDATE() | 更新时间 |

**索引设计**：
- PRIMARY KEY: `user_id`
- FOREIGN KEY: `user_id` REFERENCES users(id)
- UNIQUE INDEX: `email` （如果启用邮箱登录）

**实施时机**：用户信息完善功能开发时创建

---

## 🔗 表关系图

```
users (1) ──────< (N) classification_records
  │
  ├───────────< (N) user_points
  │
  ├───────────< (N) ai_chat_history
  │
  └───────────< (1) user_profiles
```

**说明**：
- 一个用户可以有多条分类记录
- 一个用户可以有多条积分变动记录
- 一个用户可以有多条AI对话记录
- 一个用户对应一条扩展信息

---

## 📈 数据库扩展性设计

### 1. 统一字段规范
所有表都包含以下标准字段（部分表已包含）：
- `created_at`: 记录创建时间
- `updated_at`: 记录更新时间（如需要）
- `deleted_at`: 软删除标记（如需要）

### 2. 外键约束
所有关联关系都建立外键约束，保证数据完整性

### 3. 索引优化
- 主键自动建立索引
- 外键字段建立索引
- 经常查询的字段建立索引
- 组合查询建立复合索引

### 4. JSON 字段应用
部分复杂数据使用 JSON 格式存储（如识别结果详情），便于扩展

---

## 🛠️ 数据库迁移策略

### 迁移工具
使用 Alembic（SQLAlchemy 配套）或手动 SQL 脚本管理数据库版本

### 迁移记录
每次表结构变更都记录在 `migrations/` 目录：
```
migrations/
├── 001_create_users_table.sql          ✅ 已执行
├── 002_create_classification_records.sql  📅 待执行
├── 003_create_user_points.sql          📅 待执行
└── ...
```

### 版本控制
- 所有 DDL 语句纳入版本控制
- 变更前先在测试环境验证
- 重要变更保留回滚脚本

---

## 🔒 安全性设计

### 1. 密码安全
- 使用 bcrypt 算法加密
- 密码强度验证
- 防止暴力破解（登录限流）

### 2. SQL 注入防护
- 使用 ORM（SQLAlchemy）参数化查询
- 避免字符串拼接 SQL

### 3. 数据隔离
- 用户数据通过 user_id 隔离
- API 层面验证用户权限

### 4. 数据备份
- 定期自动备份（Docker Volume）
- 重要数据变更前手动备份

---

## 📊 性能优化策略

### 1. 查询优化
- 避免 SELECT *
- 合理使用索引
- 分页查询大数据量

### 2. 连接池
- SQLAlchemy 配置连接池
- 合理设置池大小

### 3. 缓存机制
- 热点数据使用 Redis 缓存（计划中）
- 用户 Token 缓存

---

## 📝 实施计划

| 阶段 | 表名 | 状态 | 计划时间 |
|------|------|------|----------|
| 阶段一 | users | ✅ 已完成 | Week 1-2 |
| 阶段二 | classification_records | 🔄 设计完成 | Week 3-4 |
| 阶段二 | user_profiles | 🔄 设计完成 | Week 3-4 |
| 阶段三 | user_points | 📅 设计完成 | Week 5-6 |
| 阶段三 | ai_chat_history | 📅 设计完成 | Week 5-6 |
| 阶段四 | recycling_stations | 📅 设计完成 | Week 7-8（可选） |

---

## 🎯 设计优势

1. **分阶段实施**：降低风险，快速迭代
2. **整体规划**：保证系统扩展性和一致性
3. **关注分离**：每个表职责单一清晰
4. **灵活扩展**：预留 JSON 字段和扩展表
5. **性能优化**：合理的索引和查询策略

---

**文档版本**：v1.0  
**最后更新**：2025-11-06  
**维护人员**：项目组  
**审核状态**：待审核

