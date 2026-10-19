# 代码 AST 处理

`CodeAstProcessor` 使用可选依赖 `tree-sitter` 及对应的语法包解析源代码，例如 `tree-sitter-python`、`tree-sitter-javascript`。

在已完成配置初始化的处理器上调用 `process_docs`，并在文档元数据中提供语法包对应的语言名称：

```python
documents = processor.process_docs([
    Document(text=source_code, metadata={"language": "python"})
])
```

第一份输出文档包含 AST 表示和完整特征统计。满足现有分块条件时，还会输出声明块或按行划分的窗口块。

特征统计与声明收集使用原生游标遍历完整语法子树。节点较多的模块和嵌套较深的表达式不会再为每个节点累积一个 Python 调用帧，也不会修改解释器的递归上限。

已识别的函数和方法节点均计入 `function_count`，并生成 `chunk_type: "function"`；已识别的类节点生成 `chunk_type: "class"`。声明名称取自语法树的 `name` 字段，并按 UTF-8 源码偏移读取。JavaScript 计算属性方法名保留源码表达式，例如 `["method"]`，不会执行该表达式。

`max_depth` 仍限制输出 AST JSON 的深度，默认值为 8；它不会截断特征统计或声明发现。输出文档与声明边界仍保存在内存中。将 `max_depth` 设置得很大时，AST JSON 转换或 JSON 序列化仍可能达到递归上限。
