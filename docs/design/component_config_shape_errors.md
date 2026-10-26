# Component configuration structure errors

`ComponentConfiger` expects one mapping at the configuration root. When supplied,
`metadata` must also be a mapping (or `null` for existing metadata-free formats).
Lists, strings, numbers and booleans are not component definitions.

For example, these YAML structures are invalid:

```yaml
# A list at the root cannot define a single component.
- name: example_tool
```

```yaml
# metadata cannot be a scalar.
name: example_tool
metadata: TOOL
```

Use a mapping instead:

```yaml
name: example_tool
metadata:
  type: TOOL
  module: your_package.example_tool
  class: ExampleTool
```

Invalid structures raise `ValueError` before component attributes are loaded. The
message names the configuration path, the root or `metadata` field, and the actual
value type, without including configuration values. Programmatically constructed
configurations without a path are identified as `<in-memory>`.

This check does not require metadata for formats that omit it. Empty metadata
mappings, `metadata: null`, prompt metadata inferred from its path, and the legacy
`meta_class` declaration continue to work. An explicitly empty list, string or
boolean for `metadata` now raises `ValueError` instead of being silently ignored.

Run the regression and existing configuration tests with:

```bash
python -m pytest -q tests/test_agentuniverse/unit/base/config
```

中文说明：组件配置顶层应使用键值映射；`metadata` 应为映射或 `null`。
配置结构错误时，异常会直接指出文件路径、错误字段和实际类型，方便定位；
没有文件路径的内存配置以 `<in-memory>` 标识。错误消息不输出配置值。
