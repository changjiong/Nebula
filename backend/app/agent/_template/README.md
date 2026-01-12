# Agent Development Template

This directory contains a template for creating new agents.

## Quick Start

1. **Copy this directory**:
   ```bash
   cp -r _template/ my_new_agent/
   ```

2. **Modify config.yaml**:
   - Set your agent `name`, `version`, `description`
   - Define input/output schema
   - Configure external services

3. **Modify prompts.py**:
   - Update system prompt
   - Add task-specific prompts

4. **Implement handler.py**:
   - Rename `TemplateAgent` class
   - Implement `execute()` method
   - Uncomment `@register_agent` decorator

5. **Update __init__.py**:
   - Export your agent class

## File Structure

```
my_new_agent/
├── __init__.py      # Package exports
├── config.yaml      # Agent configuration
├── prompts.py       # Prompt templates
└── handler.py       # Business logic
```

## Example Usage

```python
from app.agent import AgentRegistry

# Get agent instance
agent = AgentRegistry.get_instance("my_new_agent")

# Execute
result = await agent.execute(input_data)
```
