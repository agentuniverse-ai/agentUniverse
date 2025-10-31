# 文档分类器应用示例

本示例展示了如何使用agentUniverse框架的文档分类器功能，支持多种分类策略和中文文档处理。

## 功能特性

### 基础文档分类器 (DocumentClassifier)
- **多种分类策略**：关键词匹配、正则表达式、LLM分类、混合策略
- **灵活配置**：支持自定义分类规则和类别
- **批量处理**：高效处理大量文档
- **分类统计**：提供详细的分类结果统计

### 中文文档分类器 (ChineseDocumentClassifier)
- **中文优化**：专门针对中文文档优化
- **jieba分词**：支持中文分词和关键词提取
- **停用词过滤**：自动过滤中文停用词
- **模糊匹配**：支持中文关键词模糊匹配
- **内容类型识别**：自动识别文档内容类型

## 安装依赖

```bash
pip install agentuniverse jieba
```

## 快速开始

### 1. 运行演示程序

```bash
python document_classifier_demo.py
```

### 2. 运行测试

```bash
python test_classifier.py
```

## 使用示例

### 基础分类器使用

```python
from agentuniverse.agent.action.knowledge.store.document import Document
from examples.third_party_examples.tools.document_classifier_tool.document_classifier import DocumentClassifier

# 创建分类器
classifier = DocumentClassifier()

# 设置分类类别
classifier.set_categories(['技术文档', '学术论文', '新闻资讯', '其他'])

# 添加关键词规则
classifier.add_keyword_rule('技术文档', ['代码', '编程', 'API', '函数'])
classifier.add_keyword_rule('学术论文', ['研究', '实验', '分析', '论文'])

# 创建文档
doc = Document(text="这是一个Python编程教程，介绍了如何使用API和函数。")

# 分类文档
classified_doc = classifier._classify_document(doc)
print(f"分类结果: {classified_doc.metadata['classification']}")
print(f"置信度: {classified_doc.metadata['classification_confidence']}")
```

### 中文分类器使用

```python
from examples.third_party_examples.tools.document_classifier_tool.chinese_document_classifier import
    ChineseDocumentClassifier

# 创建中文分类器
classifier = ChineseDocumentClassifier()

# 设置分类类别
classifier.set_categories(['技术文档', '学术论文', '新闻资讯', '其他'])

# 添加中文关键词规则
classifier.add_chinese_keyword_rule('技术文档', ['代码', '编程', 'API', '函数', '技术'])

# 分类中文文档
doc = Document(text="这是一个Python编程教程，介绍了如何使用API和函数进行技术开发。")
classified_doc = classifier._classify_document(doc)
print(f"分类结果: {classified_doc.metadata['classification']}")
```

### 批量文档处理

```python
# 处理多个文档
documents = [
    Document(text="Python编程教程"),
    Document(text="机器学习研究论文"),
    Document(text="科技新闻资讯")
]

classified_docs = classifier.process_docs(documents)

# 获取分类统计
summary = classifier.get_classification_summary(classified_docs)
print(f"总文档数: {summary['total_documents']}")
print(f"分类统计: {summary['category_counts']}")
```

## 配置说明

### 基础分类器配置 (document_classifier.yaml)

```yaml
name: 'document_classifier'
description: '智能文档分类器，支持多种分类策略'
strategy: 'keyword_matching'  # 分类策略
confidence_threshold: 0.7     # 置信度阈值
default_category: '未分类'     # 默认分类
categories:                   # 分类类别列表
  - '技术文档'
  - '学术论文'
  - '新闻资讯'
  - '其他'
keyword_rules:               # 关键词规则
  技术文档:
    - '代码'
    - '编程'
    - 'API'
    - '函数'
```

### 中文分类器配置 (chinese_document_classifier.yaml)

```yaml
name: 'chinese_document_classifier'
description: '中文文档智能分类器'
use_jieba: true              # 使用jieba分词
min_word_length: 2           # 最小词长度
similarity_threshold: 0.6    # 相似度阈值
stop_words:                  # 停用词列表
  - '的'
  - '了'
  - '在'
  - '是'
```

## 分类策略

### 1. 关键词匹配 (keyword_matching)
- 基于预定义关键词进行匹配
- 支持模糊匹配和权重计算
- 适合规则明确的分类场景

### 2. 正则表达式 (regex_pattern)
- 使用正则表达式进行模式匹配
- 支持复杂的文本模式识别
- 适合结构化文档分类

### 3. LLM分类 (llm_classification)
- 使用大语言模型进行智能分类
- 支持自然语言理解
- 适合复杂语义分类场景

### 4. 混合策略 (hybrid)
- 结合多种分类策略
- 提高分类准确性和鲁棒性
- 适合复杂分类需求

## 高级功能

### 文本统计
```python
# 获取文本统计信息
stats = classifier.get_text_statistics(text)
print(f"总字符数: {stats['total_chars']}")
print(f"总词数: {stats['total_words']}")
print(f"高频词: {stats['most_common_words']}")
```

### 内容类型识别
```python
# 自动识别内容类型
content_type = classifier.classify_by_content_type(text)
print(f"内容类型: {content_type}")
```

### 自定义停用词
```python
# 添加自定义停用词
classifier.stop_words.extend(['自定义', '停用词'])
```

## 性能优化

1. **批量处理**：使用`process_docs`方法批量处理文档
2. **缓存结果**：分类结果会存储在文档metadata中
3. **分词优化**：中文分类器使用jieba分词提高效率
4. **规则优化**：合理设置关键词规则和正则表达式

## 扩展开发

### 自定义分类器
```python
class CustomClassifier(DocumentClassifier):
    def _classify_document(self, document: Document) -> Document:
        # 实现自定义分类逻辑
        pass
```

### 添加新的分类策略
```python
class CustomStrategy(ClassificationStrategy):
    CUSTOM_STRATEGY = "custom_strategy"
```

## 常见问题

### Q: 如何提高分类准确性？
A: 
1. 优化关键词规则
2. 调整置信度阈值
3. 使用混合策略
4. 增加训练数据

### Q: 如何处理新领域文档？
A: 
1. 添加领域特定关键词
2. 训练领域特定模型
3. 使用LLM分类策略

### Q: 分类速度慢怎么办？
A: 
1. 减少关键词数量
2. 使用更简单的策略
3. 批量处理文档
4. 优化正则表达式

## 贡献指南

欢迎提交Issue和Pull Request来改进文档分类器功能！

## 许可证

本项目采用Apache 2.0许可证。
