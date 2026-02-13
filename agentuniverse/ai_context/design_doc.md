# AgentContext 设计文档

## 1. 定位

AgentContext 是**单次 Agent Run 的完整运行时状态容器**。

- **生命周期**：从 `agent.run()` 开始到返回结果结束。即使同一个 session、同一个 trace，每次 run 都是独立的 AgentContext 实例。
- **核心职责**：持有本次 run 所需的全部状态，agent 内部各函数通过 context 读取配置和消息、写入中间结果。
- **设计倾向**：务实优先。context 就是"当前这次 run 的快照"，agent 可以自由修改其中的字段（切换 LLM、更新工具集等），下一次 LLM 调用自然生效。单次 run 内只有一个协程在跑，不存在并发竞争，不需要过度防御。

## 2. 结构总览

```
AgentContext
│
├── 身份标识
│   ├── agent_id: str
│   └── session_id: str
│
├── Agent 配置
│   └── profile: AgentProfile
│       ├── introduction   (system prompt 模板)
│       ├── target         (目标描述模板)
│       ├── instruction    (用户指令模板)
│       ├── few_shot       (少样本示例)
│       └── tool_execute_config
│
├── LLM 配置（run 期间可修改）
│   └── llm_config: LLMConfig
│       ├── model_name: str
│       ├── temperature: float
│       ├── max_tokens: int
│       └── ...其他参数
│
├── 工具配置（run 期间可修改）
│   ├── tool_names: List[str]
│   └── tools_schema: List[Dict]
│
├── 消息（分层管理，组装时按序拼接）
│   ├── system_message: Message          ← 从 profile 模板生成
│   ├── few_shot_messages: List[Message]  ← 从 profile.few_shot 生成
│   ├── chat_history: List[Message]       ← 初始化时从 memory 加载，只读
│   └── current_messages: List[Message]   ← 本次 run 产生的所有消息，只 append
│
├── 运行时引用
│   ├── memory: Memory           ← memory 读写入口
│   ├── output_stream: Any       ← 流式输出通道
│   └── tool_output_stream: Any  ← 工具输出通道
│
└── 扩展
    └── extra: Dict[str, Any]    ← 业务侧自由扩展
```

## 3. 消息管理

### 3.1 分层的理由

消息不是一个无差别的扁平 list，而是分为四层，各自有不同的语义：

| 层 | 字段 | 来源 | 可变性 | Token 裁剪 |
|----|------|------|--------|-----------|
| system_message | 单条 Message | 从 profile 模板 + input_dict 生成 | 一般不变 | 不可裁剪 |
| few_shot_messages | List[Message] | 从 profile.few_shot 生成 | 一般不变 | 不可裁剪 |
| chat_history | List[Message] | 初始化时从 memory 加载 | 只读 | **可裁剪**（最早的先删） |
| current_messages | List[Message] | 本次 run 中产生 | 只 append | 一般不裁剪 |

分层的核心价值：
- **Token 预算管理**：当上下文超限时，知道哪些能删（chat_history 的旧消息）、哪些不能动（system、few_shot）。
- **持久化边界**：run 结束后需要写回 memory 的只有 current_messages，不用遍历整个 list 判断"哪些是新的"。
- **调试清晰**：一眼能看出哪些是背景历史、哪些是当前轮次产生的。

### 3.2 current_messages 内部是扁平的

current_messages 就是一个普通的 `List[Message]`，按时间顺序 append。不需要 ToolCallRound 之类的嵌套结构，因为项目已有的 Message 类已经能完整表达 tool calling 的语义：

```
current_messages 中的典型序列：

  Message(type=human,     content="分析 AAPL")
  Message(type=ai,        content="我来查一下", tool_calls=[ToolCall(...)])
  Message(type=tool,      tool_call_id="call_1", content='{"price": 185.2}')
  Message(type=ai,        content="还需要算市盈率", tool_calls=[ToolCall(...)])
  Message(type=tool,      tool_call_id="call_2", content="28.85")
  Message(type=ai,        content="AAPL 当前股价 185.2，市盈率 28.85")
```

多轮 tool calling 自然体现在消息顺序中，不需要额外的结构来管理"轮次"。

### 3.3 消息组装

`build_messages()` 是将消息提交给 LLM 的唯一出口：

```python
def build_messages(self) -> List[Dict[str, Any]]:
    result = []
    if self.system_message:
        result.append(self.system_message.to_dict())
    for msg in self.few_shot_messages:
        result.append(msg.to_dict())
    for msg in self.chat_history:
        result.append(msg.to_dict())
    for msg in self.current_messages:
        result.append(msg.to_dict())
    return result
```

用显式方法而非 property，表明这是一个"构建"动作。

## 4. LLM 配置

### 4.1 为什么 LLM 配置在 context 里

同一个 agent 在一次 run 中可能动态切换 LLM：
- Planning 阶段用轻量模型降成本
- Generation 阶段用强模型保质量
- Fallback 场景切换到备用模型

因此 LLM 配置是可变状态，不是静态配置。存在 context 里，agent 随时改，下一次 `llm_call` 自然用新值。

### 4.2 LLMConfig 结构

```python
class LLMConfig(BaseModel):
    model_name: str = ""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    # 扩展参数（top_p、stop 等）
    extra: Dict[str, Any] = Field(default_factory=dict)
```

只存参数，不存 LLM 客户端实例。实际调用时由 LLM 层根据 model_name 路由到对应的 client。

### 4.3 使用方式

```python
# Agent 在 run 过程中切换模型
ctx.llm_config.model_name = "qwen-turbo"
plan = await self.llm_call(ctx)

ctx.llm_config.model_name = "qwen-max"
ctx.llm_config.temperature = 0.2
result = await self.llm_call(ctx)
```

## 5. 工具配置

### 5.1 为什么工具配置也是可变的

Agent 在不同执行阶段可能需要不同的工具子集：
- Planning 阶段只暴露搜索工具
- Execution 阶段切换为代码执行工具
- 某些 tool 调用失败后 fallback 到替代工具

### 5.2 使用方式

```python
def set_tools(self, tool_names: List[str]):
    """更新工具集，自动重建 schema"""
    self.tool_names = tool_names
    self.tools_schema = build_tools_schema(tool_names)
```

tools_schema 跟随 tool_names 联动更新，调用方不需要手动维护一致性。

## 6. 创建方式

### 6.1 工厂方法（正常使用）

```python
ctx = AgentContext.create(
    agent_id="analyst",
    session_id="session_abc",
    profile={"introduction": "你是金融分析师", "instruction": "分析 {query}"},
    input_dict={"query": "AAPL"},
    tool_names=["stock_search"],
    llm_config={"model_name": "qwen-max"},
    memory=memory_instance,
)
```

工厂方法内部完成：
- AgentProfile 解析
- 通过 MessageBuilder 构建 system_message、few_shot_messages、user_message
- 从 memory 加载 chat_history
- 通过 ToolManager 构建 tools_schema

### 6.2 直接构造（单测用）

```python
ctx = AgentContext(
    agent_id="test",
    session_id="test",
    profile=AgentProfile(introduction="test"),
    llm_config=LLMConfig(model_name="mock"),
    system_message=Message(type="system", content="you are a test agent"),
    current_messages=[Message(type="human", content="hello")],
)
```

构造函数无副作用，不依赖 ToolManager 或 memory，直接创建即可。

## 7. 核心方法列表

| 方法 | 说明 |
|------|------|
| `AgentContext.create(...)` | 工厂方法，完成全部初始化 |
| `ctx.build_messages() -> List[Dict]` | 组装完整消息列表，提交给 LLM 的唯一出口 |
| `ctx.append_message(msg)` | 向 current_messages 追加消息 |
| `ctx.set_tools(tool_names)` | 更新工具集 + 自动重建 schema |
| `ctx.set_llm(**kwargs)` | 更新 LLM 配置 |
| `ctx.update_user_message(input_dict)` | 重建用户消息（重试场景） |

## 8. 不在 AgentContext 中的东西

| 排除项 | 理由 | 放在哪 |
|--------|------|--------|
| Trace / Span | 有独立的 tracing 系统 | 框架的 tracing 层 |
| Tool 实例 | 工具实例的获取和缓存是 ToolManager 的事 | ToolManager |
| LLM 客户端实例 | context 只存参数，不存连接 | LLM 层根据 model_name 路由 |
| Token 计算工具函数 | 不是 context 的职责 | 独立的 token_utils 模块 |
| 消息构建逻辑 | 不是 context 的职责 | 独立的 MessageBuilder |

## 9. 与现有 Message 类的关系

AgentContext 不定义自己的 Message，完全复用项目已有的 `agentuniverse.agent.memory.message.Message`：

- 消息角色用 `type` 字段（ChatMessageEnum: human / ai / system / tool）
- Tool calling 用 `tool_calls: List[ToolCall]`（typed model，非 Dict）
- 序列化用 `msg.to_dict()`，反序列化用 `Message.from_dict(dict)`