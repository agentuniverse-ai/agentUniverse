# Typed tool inputs

Tools can attach a Pydantic model to `args_model` when key-presence checks are
not enough. The model is applied by both `run()` and `async_run()` before the
tool implementation is called.

```python
from pydantic import BaseModel, Field

from agentuniverse.agent.action.tool.tool import Tool


class SearchArgs(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=20)


class SearchTool(Tool):
    name: str = "search"
    input_keys: list[str] = ["query"]
    args_model: object = SearchArgs

    def execute(self, query: str, limit: int):
        return search(query, limit=limit)
```

Pydantic coercions and defaults are passed to `execute`. Invalid input raises
the normal Pydantic `ValidationError`. Existing tools that leave `args_model`
unset keep their current behavior, including tools that still receive a
`ToolInput` object.
