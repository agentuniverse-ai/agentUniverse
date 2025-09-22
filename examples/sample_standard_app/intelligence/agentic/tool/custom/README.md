# 搜索工具使用说明

本目录包含了增强的Google搜索和Google学术搜索工具，按照AgentUniverse标准项目架构组织。

## 工具列表

### 1. GoogleSearchTool (google_search_tool.py)
增强的Google搜索工具，支持多种搜索类型和参数配置。

**主要特性:**
- 支持普通搜索、图片搜索、新闻搜索、地点搜索
- 可配置返回结果数量、地理位置、语言等参数
- 提供格式化的搜索结果输出
- 支持同步和异步执行
- 完善的错误处理和模拟模式支持

**使用示例:**
```python
from sample_standard_app.intelligence.agentic.tool.custom.google_search_tool import GoogleSearchTool

# 创建工具实例
search_tool = GoogleSearchTool()

# 普通搜索
result = search_tool.execute(input="人工智能最新发展")

# 图片搜索
result = search_tool.execute(input="美丽的风景", search_type="images", k=5)

# 新闻搜索
result = search_tool.execute(input="科技新闻", search_type="news", gl="cn", hl="zh")
```

### 2. GoogleScholarSearchTool (google_search_tool.py)
Google学术搜索工具，专门用于搜索学术论文和研究资料。

**主要特性:**
- 专门针对学术内容搜索
- 支持按年份、作者、期刊等条件筛选
- 自动构建优化的学术搜索查询
- 提供论文引用相关信息
- 支持同步和异步执行

**使用示例:**
```python
from sample_standard_app.intelligence.agentic.tool.custom.google_search_tool import GoogleScholarSearchTool

# 创建工具实例
scholar_tool = GoogleScholarSearchTool()

# 基础学术搜索
result = scholar_tool.execute(input="机器学习算法")

# 按年份筛选
result = scholar_tool.execute(input="深度学习", year="2020..2024")

# 按作者筛选
result = scholar_tool.execute(input="神经网络", author="Geoffrey Hinton")

# 综合搜索
result = scholar_tool.execute(
    input="自然语言处理",
    author="Yoshua Bengio",
    year="2020..2024",
    k=5
)
```

## 配置文件

### google_search_tool.yaml
Google搜索工具的配置文件，包含工具的描述、参数说明和使用示例。

### google_scholar_search_tool.yaml
Google学术搜索工具的配置文件，包含工具的描述、参数说明和使用示例。

## 智能体集成

### search_agent.yaml
搜索智能体配置文件，集成了Google搜索和Google学术搜索工具。

### search_agent.py
搜索智能体实现类，继承自AgentTemplate。

## 测试

### test_google_search_tool.py
完整的单元测试，测试工具的各种功能和边界情况。

### test_search_tools_demo.py
演示脚本，展示如何使用这些搜索工具。

## 环境配置

### API密钥配置
在环境变量中配置Google Serper API密钥：

```bash
export SERPER_API_KEY='your_serper_api_key_here'
```

或者在 `config/custom_key.toml` 文件中配置：

```toml
[KEY_LIST]
SERPER_API_KEY='your_serper_api_key_here'
```

### 获取API密钥
1. 访问 [Serper.dev](https://serper.dev)
2. 注册免费账户
3. 获取API密钥（每月2500次免费查询）

## 运行测试

```bash
# 运行单元测试
cd examples/sample_standard_app/intelligence/test
python test_google_search_tool.py

# 运行演示脚本
python test_search_tools_demo.py
```

## 在智能体中使用

在智能体配置文件中添加工具：

```yaml
tool_list: ['google_search_tool', 'google_scholar_search_tool']
```

## 注意事项

1. **API限制**: Serper API每月有2500次免费查询限制
2. **网络连接**: 需要稳定的网络连接来访问Google搜索服务
3. **模拟模式**: 当API密钥不可用时，工具会返回模拟结果
4. **错误处理**: 工具包含完善的错误处理机制

## 扩展功能

### 自定义搜索工具
可以基于现有工具创建自定义搜索工具：

```python
from agentuniverse.agent.action.tool.tool import Tool

class CustomSearchTool(Tool):
    def execute(self, input: str, **kwargs):
        # 自定义搜索逻辑
        pass
```

### 集成其他搜索服务
可以集成其他搜索服务，如Bing搜索、DuckDuckGo等。

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查密钥是否正确配置
   - 确认密钥是否有效且未过期

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

3. **搜索结果为空**
   - 尝试调整搜索词
   - 检查搜索参数设置

4. **导入错误**
   - 确认AgentUniverse框架已正确安装
   - 检查Python路径设置

## 贡献

欢迎提交Issue和Pull Request来改进这些搜索工具！
