# Skill

Skill is a modular, reusable capability unit in agentUniverse. Each Skill bundles a set of instructions with allowed tools, enabling agents to load specialized capabilities on demand.

## Core Concepts

### Skill Components
A Skill consists of the following key elements:
- **Instructions**: Detailed instructions defined in SKILL.md file in Markdown format
- **Allowed Tools**: List of tools the Skill can use
- **Allowed Toolkits**: List of toolkits the Skill can use
- **Execution Mode (Context)**: `inline` or `fork`

### Execution Modes

#### Inline Mode (Default)
In inline mode, the Skill's instructions and tools are injected directly into the current agent's context. The agent gains access to the Skill's tools and can use them immediately.

#### Fork Mode
In fork mode, the system creates an isolated sub-agent to execute the Skill's task. The sub-agent has its own independent context and tool set. Only the final result is returned, without affecting the parent agent's state.

## SKILL.md File Format

Each Skill is defined by a `SKILL.md` file containing YAML frontmatter and Markdown body:

```markdown
---
name: my-skill
description: "A brief description of this skill"
version: "1.0"
allowed_tools:
  - tool_name_1
  - tool_name_2
allowed_toolkits:
  - toolkit_name_1
context: inline
max_iterations: 10
---

# Skill Instructions

Detailed skill instructions written in Markdown format...
```

### Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Skill name (matches directory name) |
| `description` | Yes | Skill description for LLM semantic matching |
| `allowed_tools` | No | List of allowed tools, supports wildcard syntax |
| `allowed_toolkits` | No | List of allowed toolkit names |
| `context` | No | Execution mode: `inline` (default) or `fork` |
| `sub_agent` | No | Custom agent for fork mode |
| `model` | No | Override the default LLM model |
| `max_iterations` | No | Maximum tool-calling rounds (default 10) |
| `version` | No | Skill version number |
| `user_invocable` | No | Whether visible in user menus |
| `disable_model_invocation` | No | Prevent auto-invocation by LLM |

## Using Skills in Agents

### Configuration

Add the `skill` field to your agent's YAML configuration:

```yaml
name: 'my_skill_agent'
description: 'An agent with skills'
profile:
  introduction: 'You are an intelligent assistant with multiple skills'
  target: 'Help users accomplish various tasks'
  llm_model:
    name: 'qwen_llm'
    model_name: 'qwen-max'
action:
  skill:
    - 'algorithmic-art'
    - 'mcp-builder'
metadata:
  type: 'AGENT'
  module: 'xxx.agent_instance.my_skill_agent'
  class: 'MySkillAgent'
```

### Package Path Configuration

Configure the Skill scan path in `config.toml`:

```toml
[CORE_PACKAGE]
skill = ['sample_standard_app.intelligence.agentic.skill']
```

## Directory Structure

A typical Skill directory structure:

```
my-skill/
├── SKILL.md              # Skill definition file (required)
├── templates/            # Template files (optional)
│   └── template.html
├── reference/            # Reference documents (optional)
│   └── best_practices.md
└── scripts/              # Script files (optional)
    └── helper.py
```

## Built-in Examples

The framework provides two Skill examples in `sample_standard_app`:

### algorithmic-art
A skill for generating algorithmic art, including p5.js generator templates and HTML viewer.

### mcp-builder
An MCP server development guide skill, containing best practice references for Python and Node.js MCP servers.

# Conclusion
The Skill system provides a modular capability extension mechanism for agentUniverse, allowing agents to load specialized tools and instructions on demand, supporting both inline and isolated execution modes.
