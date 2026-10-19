# Code AST processing

`CodeAstProcessor` parses source code with the optional `tree-sitter` package and the matching grammar package, such as `tree-sitter-python` or `tree-sitter-javascript`.

On a configured processor, call `process_docs` with code documents whose metadata contains the grammar's language name:

```python
documents = processor.process_docs([
    Document(text=source_code, metadata={"language": "python"})
])
```

The first output document contains the AST representation and complete feature counts. Additional documents contain declaration or line-window chunks when the existing chunking conditions apply.

Feature counting and declaration collection traverse the entire syntax subtree with a native cursor. Wide modules and deep expressions therefore do not consume one Python call frame per node. Processing keeps the interpreter's recursion limit unchanged.

Recognized function and method nodes both contribute to `function_count` and produce `chunk_type: "function"`; recognized class nodes produce `chunk_type: "class"`. Declaration names use the grammar's `name` field and UTF-8 source offsets. Computed JavaScript method names remain their source expressions, such as `["method"]`; they are not evaluated.

`max_depth` still limits the returned AST JSON, with a default of 8; it does not truncate feature counts or declaration discovery. Output documents and declaration boundaries are still accumulated in memory. Very large `max_depth` settings can still reach the recursion limits of AST JSON conversion or JSON serialization.
