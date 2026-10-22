# Structured Agent Output

An agent normally validates only the keys returned by `output_keys()`. When a
downstream API or workflow needs a typed contract, override `output_model()`
and return a Pydantic model.

```python
from pydantic import BaseModel, Field

from agentuniverse.agent.template.agent_template import AgentTemplate


class ResearchResult(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    sources: list[str] = []


class ResearchAgentTemplate(AgentTemplate):
    def output_keys(self) -> list[str]:
        return ["answer", "confidence", "sources"]

    def output_model(self) -> type[BaseModel]:
        return ResearchResult
```

Validation runs after `parse_result()` and before `OutputObject` is created in
both `run()` and `async_run()`. Pydantic coercion and defaults are included in
the returned dictionary. Invalid nested values raise `ValidationError` before
they can reach another agent or service.

The hook is optional. Agents that do not override `output_model()` keep the
existing dictionary and `output_keys()` behavior unchanged.
