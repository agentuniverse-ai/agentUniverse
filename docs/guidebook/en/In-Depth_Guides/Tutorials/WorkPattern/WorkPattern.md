# Work Pattern

The work pattern encompasses typical paradigms for the collaboration and coordination among single-agent and multi-agent systems. Representative work patterns include PEER and DOE, among others.

## How to Define a Work Pattern

### [Basic Class Definition of Work Pattern](../../../../../../agentuniverse/agent/work_pattern/work_pattern.py)

The configuration information includes:

- `name`: The name of the work pattern.
- `description`: A description of the work pattern.

The methods included are:

- invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
  : The synchronous execution method of the work pattern (an abstract method).

- async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
  : The asynchronous execution method of the work pattern (an abstract method).

### Definition of a Specific Work Pattern Implementation Class

Taking the built-in [PEER Work Pattern](../../../../../../agentuniverse/agent/work_pattern/peer_work_pattern.py) in agentUniverse as an example, it defines four attributes:

- `planning`: The planning node.
- `executing`: The execution node.
- `expressing`: The expression node.
- `reviewing`: The reviewing node.

The `invoke` and `async_invoke` methods are the synchronous and asynchronous execution methods of the work pattern, respectively. The execution logic of the work pattern **only includes the transition logic between nodes and can be understood as a higher-level system abstraction compared to the agent template**.

## How to Use the Work Pattern

Taking the PEER work pattern mentioned above as an example, its invocation relationship exists within the [PEER Agent Template](../../../../../../agentuniverse/agent/template/peer_agent_template.py).
In the execution logic of the agent template, a specified work pattern instance is obtained, its attributes are assembled, and then it is executed.

The flowchart is as follows:
![PEER Work Pattern](../../../../_picture/peer_work_pattern.png)

By invoking the agent instance corresponding to the PEER agent template, the entire process is initiated. After performing the necessary pre-checks, the PEER agent template calls the work pattern. The work pattern executes the transition logic between the node members and ultimately returns the result to the PEER agent template.
The PEER agent template then performs specific assembly and post-processing before concluding the entire process.

When `jump_step` is `planning`, a review score below `eval_threshold` starts a new PEER round,
subject to `retry_count`. In the next round, the built-in planning agent receives the previous
framework, review score, and review suggestion and uses this feedback to revise the plan. These
optional feedback values are empty in the first round; custom planning prompts can choose whether
to consume the optional `previous_planning_result`, `review_score`, and `review_suggestion`
variables.

## Using the WorkPattern Work Mode Manager

The `get_instance_obj(xx_work_pattern)` method in WorkPatternManager can be used to obtain the instance of the work pattern with the corresponding name.

```python
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager

work_pattern_name = 'xxx_work_pattern'
work_pattern = WorkPatternManager().get_instance_obj(component_instance_name=work_pattern_name)
```

## The built-in work pattern in agentUniverse:

### [PeerWorkPattern](../../../../../../agentuniverse/agent/work_pattern/peer_work_pattern.py)

The built-in system configuration is as follows:

```yaml
name: 'peer_work_pattern'
description: 'peer work pattern'
metadata:
  type: 'WORK_PATTERN'
  module: 'agentuniverse.agent.work_pattern.peer_work_pattern'
  class: 'PeerWorkPattern'
```
Users can obtain the instance of the Peer work pattern through the work pattern manager.

## Work Pattern vs Agent Template vs Agent Planner
- The agent template encapsulates the specific orchestration logic within the execute method, which can be compared to the execution logic of the previous agent plan (planner).
- The agent template abstracts the execution logic of an agent. Users can assemble different agent instances from the template based on various configuration information, allowing for reuse.
- The work pattern is a higher-level abstraction above the agent template. It includes typical paradigms for collaboration and coordination among single-agent and multi-agent systems. The invoke method only contains the transition logic between nodes and does not include specific business processing logic.

# Summary
You have now understood the purpose of work patterns, their specific definitions, and how to use them.
