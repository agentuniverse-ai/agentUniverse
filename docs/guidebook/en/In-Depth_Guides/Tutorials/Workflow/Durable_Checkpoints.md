# Durable Workflow Checkpoints

Long-running workflows can persist progress after every successful node and
resume later without repeating completed work.

```python
from pathlib import Path


def save_checkpoint(snapshot):
    Path("workflow-checkpoint.json").write_text(
        snapshot.to_checkpoint_json(),
        encoding="utf-8",
    )


result = workflow.run(
    {"input": "prepare the report"},
    checkpoint_callback=save_checkpoint,
)
```

If the process is interrupted, restore the last snapshot:

```python
checkpoint = Path("workflow-checkpoint.json").read_text(encoding="utf-8")
result = workflow.resume(checkpoint, checkpoint_callback=save_checkpoint)
```

`resume()` accepts a `WorkflowOutput`, dictionary, JSON string, or JSON bytes.
The workflow id is checked before execution, and a resumed run skips every node
already present in `workflow_node_results`. Callbacks receive deep copies so a
storage adapter cannot accidentally mutate the live execution state.
