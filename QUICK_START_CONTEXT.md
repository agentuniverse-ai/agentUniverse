# 上下文工程系统 - 快速开始指南
## Context Engineering System - Quick Start Guide

**5 分钟上手 agentUniverse 上下文管理系统**

---

## 📦 什么是上下文工程系统？

上下文工程系统为 agentUniverse Agent 提供：
- ✅ 智能上下文管理（自动压缩、多层存储）
- ✅ 长对话记忆（跨会话保持连贯性）
- ✅ 知识库同步（自动更新、冲突解决）
- ✅ 性能监控（延迟、内存、质量指标）

**对标**: Cursor、Claude 等行业领先产品

---

## 🚀 快速开始

### 步骤 1: 基本使用（2 分钟）

```python
# 1. 导入必要的类
from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
from agentuniverse.agent.context.context_model import ContextType, ContextPriority

# 2. 获取上下文管理器实例
context_manager = ContextManagerManager().get_instance_obj("default_context_manager")

# 3. 创建上下文窗口（每个会话一个）
window = context_manager.create_context_window(
    session_id="user_123",
    task_type="dialogue"  # 可选: code_generation, data_analysis
)

# 4. 添加用户输入
context_manager.add_context(
    session_id="user_123",
    content="今天天气怎么样？",
    context_type=ContextType.CONVERSATION,
    priority=ContextPriority.HIGH
)

# 5. 添加 Agent 回复
context_manager.add_context(
    session_id="user_123",
    content="今天天气晴朗，温度 20°C。",
    context_type=ContextType.CONVERSATION,
    priority=ContextPriority.HIGH
)

# 6. 下一轮对话，搜索相关上下文
results = context_manager.search_context(
    session_id="user_123",
    query="天气",
    top_k=5
)

for segment in results:
    print(f"[{segment.priority}] {segment.content}")

# 7. 查看 token 使用情况
metrics = context_manager.get_budget_utilization("user_123")
print(f"Token 使用率: {metrics['utilization']:.1%}")
print(f"总 tokens: {metrics['total_tokens']}")
```

**就是这么简单！** 系统会自动处理压缩、存储和检索。

---

### 步骤 2: 知识同步（可选，3 分钟）

如果你的 Agent 使用知识库，可以自动同步知识到上下文：

```python
from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
    ConflictResolutionStrategy
)

# 1. 创建同步器
synchronizer = KnowledgeContextSynchronizer(
    context_manager=context_manager,
    conflict_strategy=ConflictResolutionStrategy.NEWEST_WINS
)

# 2. 同步知识文档到上下文
result = synchronizer.sync_knowledge_to_context(
    knowledge_id="user_manual",
    documents=[
        "产品特性：支持多种文件格式...",
        "安装步骤：1. 下载安装包 2. 运行安装..."
    ],
    session_id="user_123",
    priority=ContextPriority.HIGH
)

print(f"✅ 添加了 {result.segments_added} 个知识片段")

# 3. 更新知识（内容变化时自动检测）
result = synchronizer.sync_knowledge_to_context(
    knowledge_id="user_manual",
    documents=["产品特性：新增 PDF 导出功能..."],  # 更新后的内容
    session_id="user_123"
)

print(f"✅ 更新了知识，失效了 {result.segments_invalidated} 个旧片段")
```

---

### 步骤 3: 运行基准测试（可选，1 分钟）

验证系统性能：

```python
from agentuniverse.agent.context.benchmark.benchmark_suite import (
    ContextBenchmarkSuite
)

# 1. 创建基准测试套件
suite = ContextBenchmarkSuite(context_manager)

# 2. 运行测试（100 轮对话模拟）
result = suite.run_full_suite(num_turns=100)

# 3. 查看结果
print(f"📊 整体评分: {result.metrics.get_score():.1f}/100")
print(f"✅ 通过所有目标: {result.metrics.passes_targets()}")
print(f"   - 多轮连贯性: {result.metrics.multi_turn_coherence:.3f}")
print(f"   - 压缩率: {result.metrics.compression_ratio:.1%}")
print(f"   - 检索精确度: {result.metrics.retrieval_precision:.3f}")
```

**目标**: 评分 >85/100，所有指标达到行业标准。

---

## 🎯 三种使用场景

### 场景 1: 简单对话机器人

**需求**: 记住最近的对话，提供连贯的回复

**配置**: 默认配置即可

**代码**:
```python
# 每次用户输入
context_manager.add_context(session_id, user_input, ContextType.CONVERSATION, ContextPriority.HIGH)

# 每次 Agent 回复
context_manager.add_context(session_id, agent_output, ContextType.CONVERSATION, ContextPriority.HIGH)

# 系统自动处理上下文压缩和检索
```

---

### 场景 2: 知识问答系统

**需求**: 基于知识库回答问题，知识更新时自动同步

**配置**: 启用知识同步

**代码**:
```python
# 初始化同步器
synchronizer = KnowledgeContextSynchronizer(context_manager)

# 每次查询前同步相关知识
documents = knowledge_base.query(user_question, top_k=5)
synchronizer.sync_knowledge_to_context(
    knowledge_id="kb_v1",
    documents=[doc.text for doc in documents],
    session_id=session_id
)

# 使用上下文生成回答
context = context_manager.get_context(session_id)
agent_answer = llm.generate(context + user_question)
```

---

### 场景 3: 多 Agent 协作系统

**需求**: 多个 Agent 共享上下文，协同完成任务

**配置**: 使用 AgentContextCoordinator

**代码**:
```python
from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    AgentContextCoordinator  # 见 PHASE3_4_INTEGRATION_GUIDE.md
)

# 创建协调器
coordinator = AgentContextCoordinator()

# 创建共享会话
session_id = coordinator.create_shared_session("research_team")

# Agent 1 分享发现
coordinator.share_context(
    agent_group_id="research_team",
    content="找到相关论文: ...",
    source_agent="research_agent"
)

# Agent 2 获取共享上下文
shared_context = coordinator.get_shared_context("research_team")
```

---

## 📋 配置说明

### 最小配置（使用默认）

系统开箱即用，默认配置已优化：
- 热存储: RAM (快速访问)
- 压缩策略: Adaptive (自适应选择)
- Token 预算: 8000 (对话), 10000 (代码), 12000 (分析)

### 自定义配置（可选）

创建 `config/context_manager/my_context_manager.yaml`:

```yaml
name: 'my_context_manager'
hot_store_name: 'ram_context_store'
warm_store_name: 'redis_context_store'  # 可选: 持久化
cold_store_name: 'chroma_context_store'  # 可选: 长期存储
llm_name: 'gpt-4'
default_max_tokens: 10000
enable_compression: true

metadata:
  type: 'CONTEXT_MANAGER'
  module: 'agentuniverse.agent.context.context_manager'
  class: 'ContextManager'
```

---

## 🎓 进阶主题

### 压缩策略选择

系统提供 5 种压缩策略：

| 策略 | 速度 | 质量 | 适用场景 |
|------|------|------|----------|
| Truncate | 最快 | 一般 | 实时对话 |
| Selective | 快 | 好 | 一般应用 ⭐ |
| Summarize | 慢 | 最好 | 高质量要求 |
| Hybrid | 中等 | 好 | 平衡场景 |
| Adaptive | 自动 | 自动 | 推荐默认 ⭐ |

**推荐**: 使用 `Adaptive`（默认），系统自动选择最优策略。

### 优先级管理

5 种优先级：

| 优先级 | 说明 | 何时使用 |
|--------|------|----------|
| CRITICAL | 永不压缩 | 系统提示、核心指令 |
| HIGH | 优先保留 | 重要对话、关键知识 |
| MEDIUM | 按需保留 | 一般内容 |
| LOW | 容易压缩 | 背景信息 |
| EPHEMERAL | 立即丢弃 | 临时数据 |

**最佳实践**:
- 系统提示 → CRITICAL
- 用户输入 → HIGH
- Agent 回复 → HIGH
- 背景知识 → MEDIUM
- 临时计算 → EPHEMERAL

### 任务类型配置

系统支持 3 种预配置任务类型：

**1. dialogue (对话)**
- Token 预算: 8000
- 侧重: 对话历史 (50%)

**2. code_generation (代码生成)**
- Token 预算: 10000
- 侧重: 代码文件 (50%)

**3. data_analysis (数据分析)**
- Token 预算: 12000
- 侧重: 数据上下文 (40%)

创建上下文窗口时指定：
```python
window = context_manager.create_context_window(
    session_id="session_123",
    task_type="code_generation"  # 自动使用代码生成配置
)
```

---

## 🐛 常见问题

### Q1: 上下文太长，压缩不够？

**解决**: 调整压缩率或使用更激进的策略

```python
# 手动触发压缩
from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor

compressor = AdaptiveCompressor(
    name="aggressive_compressor",
    llm_name="gpt-4",
    compression_ratio=0.4,  # 60% 压缩
    enable_hybrid=True
)

# 或者降低 token 预算
window = context_manager.create_context_window(
    session_id="session_123",
    max_tokens=6000  # 从 8000 降到 6000
)
```

### Q2: 检索不准确？

**解决**: 使用更具体的查询词，或增加 top_k

```python
# 更具体的查询
results = context_manager.search_context(
    session_id="session_123",
    query="用户关于产品价格的问题",  # 而不是 "价格"
    top_k=10  # 增加返回数量
)

# 按类型过滤
conversation_context = context_manager.get_context(
    session_id="session_123",
    context_type=ContextType.CONVERSATION  # 只获取对话
)
```

### Q3: 内存占用太高？

**解决**: 启用多层存储，将旧上下文移到 Redis/Chroma

```yaml
# config/context_manager/my_context_manager.yaml
warm_store_name: 'redis_context_store'  # 启用 Redis
cold_store_name: 'chroma_context_store'  # 启用向量数据库
```

系统会自动将不常用的上下文移到暖/冷存储。

### Q4: 需要更详细的监控？

**解决**: 使用 ContextMonitor

```python
from agentuniverse.agent.context.benchmark.benchmark_suite import (
    ContextMonitor  # 见 PHASE3_4_INTEGRATION_GUIDE.md
)

monitor = ContextMonitor(context_manager_name="default_context_manager")

# 收集指标
metrics = monitor.collect_metrics()
print(f"活跃会话: {metrics.active_sessions}")
print(f"平均延迟: {metrics.average_add_latency_ms:.1f}ms")
print(f"内存使用: {metrics.total_memory_mb:.1f}MB")

# 健康检查
health = monitor.get_health_status()
print(f"系统健康: {health}")  # HEALTHY, WARNING, CRITICAL
```

---

## 📚 完整文档

- **集成指南**: `PHASE3_4_INTEGRATION_GUIDE.md` (850+ 行)
  - 5 种 Agent 集成模式详解
  - 完整代码示例
  - 生产部署指南

- **测试报告**: `PHASE2_最终测试报告.md`
  - 30 个单元测试详解
  - 性能验证结果

- **项目总结**: `阶段总结.md`
  - 完整项目概览
  - 所有组件说明

---

## 🎯 下一步

1. ✅ **试用基本功能**: 运行上面的快速开始代码
2. ✅ **运行基准测试**: 验证系统性能
3. ✅ **查看集成指南**: 选择适合的集成模式
4. ⏳ **集成到你的 Agent**: 按照指南集成
5. ⏳ **部署到生产**: 使用监控系统跟踪性能

---

## 💡 最佳实践

1. **永远使用 CRITICAL 优先级存储系统提示**
2. **为不同任务使用不同的 task_type**
3. **定期运行基准测试验证性能**
4. **启用监控跟踪生产环境指标**
5. **使用知识同步保持知识库最新**

---

## 🚀 开始使用

```python
# 最简单的完整示例
from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
from agentuniverse.agent.context.context_model import ContextType, ContextPriority

# 1. 获取管理器
cm = ContextManagerManager().get_instance_obj("default_context_manager")

# 2. 创建会话
cm.create_context_window(session_id="user_123", task_type="dialogue")

# 3. 添加对话
cm.add_context("user_123", "你好！", ContextType.CONVERSATION, ContextPriority.HIGH)
cm.add_context("user_123", "你好！有什么可以帮助你的吗？", ContextType.CONVERSATION, ContextPriority.HIGH)

# 4. 查询上下文
results = cm.search_context("user_123", "帮助", top_k=5)
for r in results:
    print(r.content)

# 5. 查看使用情况
metrics = cm.get_budget_utilization("user_123")
print(f"使用率: {metrics['utilization']:.1%}")
```

**就这么简单！开始构建你的上下文感知 Agent 吧！** 🎉

---

**需要帮助？** 查看完整文档：
- `PHASE3_4_INTEGRATION_GUIDE.md` - 详细集成指南
- `阶段总结.md` - 完整项目说明
- `PHASE2_最终测试报告.md` - 性能验证报告
