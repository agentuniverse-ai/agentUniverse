# Changelog

All notable changes to the GRR (Generate-Review-Rewrite) pattern will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-12-01

### Added

#### Core Framework
- **GRRWorkPattern** (`agentuniverse/agent/work_pattern/grr_work_pattern.py`)
  - Implemented Generate-Review-Rewrite three-stage workflow
  - Support for synchronous and asynchronous execution
  - Configurable iteration count and quality threshold
  - Intelligent iterative optimization mechanism
  - Full integration with AgentUniverse component system

#### Agent Templates
- **GeneratingAgentTemplate** (`agentuniverse/agent/template/generating_agent_template.py`)
  - Content generation based on user requirements
  - Support for expert framework guidance
  - Stream output support for real-time feedback
  - Input/output key validation

- **RewritingAgentTemplate** (`agentuniverse/agent/template/rewriting_agent_template.py`)
  - Content rewriting based on review feedback
  - Context-aware improvement suggestions
  - Integration with review scores and suggestions
  - Expert framework support

- **GRRAgentTemplate** (`agentuniverse/agent/template/grr_agent_template.py`)
  - Coordinator for three sub-agents
  - Memory management across iterations
  - Expert framework building and injection
  - Result parsing with preference for rewritten content

#### Configuration
- **Work Pattern Config** (`agentuniverse/agent/work_pattern/grr_work_pattern.yaml`)
  - Work pattern metadata and type definitions

#### Example Application
- **Complete GRR Agent App** (`examples/sample_apps/grr_agent_app/`)
  - Full directory structure following PEER pattern conventions
  - Four agent configurations (main GRR agent + 3 sub-agents)
  - Three Chinese prompt templates (generating, reviewing, rewriting)
  - LLM and memory configurations
  - Application configuration (config.toml)
  - Unit tests with three test scenarios

#### Documentation
- **README.md** - Comprehensive usage documentation
  - Architecture overview
  - Quick start guide
  - Configuration parameters
  - Use cases and examples
  - Comparison with PEER pattern

- **CONTRIBUTING.md** - Contribution guidelines
  - Development environment setup
  - Code style guidelines
  - Testing requirements
  - PR submission process

- **CHANGELOG.md** - Version history and changes

- **quick_start.py** - Quick start demo script with three examples

#### Testing
- **test_grr_agent.py** - Unit tests
  - Basic functionality test
  - Content generation test
  - Creative writing test

### Features

#### Iterative Content Optimization
- Automatic quality-based iteration decision
- Configurable quality score threshold (default: 60/100)
- Configurable maximum iteration count (default: 2)
- Smart result selection (prioritizes rewritten content)

#### Flexible Configuration System
- YAML-based agent configuration
- Profile-level and planner-level configuration support
- Easy parameter override
- Expert framework support with context and tool selector

#### Expert Framework Support
- Static context configuration for domain-specific guidance
- Dynamic tool selector for runtime guidance generation
- Per-stage guidance (generating, reviewing, rewriting)

#### Memory Integration
- Complete iteration history recording
- Cross-iteration conversation memory
- Structured memory storage with role information
- Detailed turn-by-turn memory entries

#### Stream Output Support
- Real-time output for each stage
- Progress feedback for long-running tasks
- Type-specific output markers (generating, reviewing, rewriting)

### Technical Details

#### Architecture
- Follows PEER pattern design principles
- Component-based architecture with proper inheritance
- Singleton manager pattern for work pattern registration
- Dynamic agent assembly at runtime

#### Performance
- Support for both synchronous and asynchronous execution
- Efficient iteration with early termination on quality threshold
- Minimal overhead for single-iteration scenarios

#### Code Quality
- Full type hints throughout codebase
- Comprehensive docstrings
- Proper error handling and validation
- Consistent logging

### Use Cases
- Content creation (articles, reports, copywriting)
- Creative writing (stories, scripts)
- Technical documentation (API docs, user manuals)
- Marketing copy (product descriptions, advertisements)
- Academic writing (paper abstracts, research reports)

### Dependencies
- Inherits all dependencies from agentUniverse framework
- Compatible with existing PEER pattern infrastructure
- Reuses ReviewingAgentTemplate from PEER pattern

### Notes
- This is the initial release implementing GitHub Issue #257 (Part 1: GRR Mode)
- Part 2 (IS Mode: Implementation-Supervision) is planned for future release
- All documentation and prompts are in Chinese for better localization

### Breaking Changes
None - This is the initial release

### Deprecated
None

### Removed
None

### Fixed
None (initial release)

### Security
None (initial release)

## Future Plans

### Planned for Next Release (1.1.0)
- [ ] English prompt templates
- [ ] Additional domain-specific prompt templates
- [ ] Performance metrics and monitoring
- [ ] Streaming progress visualization
- [ ] More comprehensive test coverage

### Planned for Future Releases (2.0.0)
- [ ] IS Mode implementation (Implementation-Supervision pattern)
- [ ] GRR + PEER pattern combination examples
- [ ] Visual configuration and monitoring tools
- [ ] Parallel optimization for independent steps
- [ ] Enhanced expert framework with multi-tool support

## Related Issues
- [GitHub Issue #257](https://github.com/agentuniverse-ai/agentUniverse/issues/257) - Enhancement for agent work-patterns

## Contributors
- Claude Code - Initial implementation (2025-12-01)

---

For more information about the GRR pattern, see the [README](README.md).
