# DocumentClassifier 文档分类器

DocumentClassifier是agentUniverse框架中的文档分类组件，提供智能文档分类功能，支持多种分类策略和中文文档处理。

## 功能特性

### 基础功能
- **多种分类策略**：关键词匹配、正则表达式、LLM分类、混合策略
- **灵活配置**：支持自定义分类规则和类别
- **批量处理**：高效处理大量文档
- **分类统计**：提供详细的分类结果统计

### 中文优化
- **jieba分词**：支持中文分词和关键词提取
- **停用词过滤**：自动过滤中文停用词
- **模糊匹配**：支持中文关键词模糊匹配
- **内容类型识别**：自动识别文档内容类型

## 使用方法

### 基础分类器

```python
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.doc_processor.document_classifier import DocumentClassifier

# 创建分类器
classifier = DocumentClassifier()

# 设置分类类别
classifier.set_categories(['技术文档', '学术论文', '新闻资讯', '其他'])

# 添加关键词规则
classifier.add_keyword_rule('技术文档', ['代码', '编程', 'API', '函数'])

# 分类文档
doc = Document(text="这是一个Python编程教程")
classified_doc = classifier._classify_document(doc)
```

### 中文分类器

```python
from agentuniverse.agent.action.knowledge.doc_processor.chinese_document_classifier import ChineseDocumentClassifier

# 创建中文分类器
classifier = ChineseDocumentClassifier()

# 添加中文关键词规则
classifier.add_chinese_keyword_rule('技术文档', ['代码', '编程', 'API', '函数', '技术'])
```

## 配置说明

### 基础配置

```yaml
name: 'document_classifier'
strategy: 'keyword_matching'
confidence_threshold: 0.7
default_category: '未分类'
categories:
  - '技术文档'
  - '学术论文'
  - '新闻资讯'
keyword_rules:
  技术文档:
    - '代码'
    - '编程'
    - 'API'
```

### 中文配置

```yaml
name: 'chinese_document_classifier'
use_jieba: true
min_word_length: 2
similarity_threshold: 0.6
```

## 分类策略

1. **关键词匹配**：基于预定义关键词进行匹配
2. **正则表达式**：使用正则表达式进行模式匹配
3. **LLM分类**：使用大语言模型进行智能分类
4. **混合策略**：结合多种分类策略

## 高级功能

- 文本统计信息获取
- 内容类型自动识别
- 分类结果统计摘要
- 自定义停用词配置

更多详细信息请参考示例应用：`examples/sample_apps/document_classifier_app/`
