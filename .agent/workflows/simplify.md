---
description: Simplify and refine code for clarity using code-simplifier agent. Preserves functionality while improving readability.
---

# /simplify Workflow

Simplify and refine code using the `code-simplifier` agent principles.

## Steps

1. **Load Agent Rules**
   - Read `.agent/agents/code-simplifier.md` to understand the simplification principles
   - Focus on: preserving functionality, project standards, clarity enhancement, balance

2. **Identify Target Code**
   - If user specifies a file/function: analyze that specific code
   - If no file specified: check recently modified files using `git diff --name-only HEAD~1`
   - Ask user to confirm the scope before proceeding

3. **Analyze Code for Improvements**
   Apply the 5 core principles:
   - [ ] **Preserve Functionality**: Verify no behavioral changes
   - [ ] **Apply Project Standards**: ES modules, function keyword, explicit types
   - [ ] **Enhance Clarity**: Reduce nesting, avoid nested ternaries, clear naming
   - [ ] **Maintain Balance**: Don't over-simplify, keep helpful abstractions
   - [ ] **Focus Scope**: Only touch relevant code sections

4. **Apply Refinements**
   - Simplify code structure
   - Eliminate redundant code and abstractions
   - Improve variable and function names
   - Remove unnecessary comments
   - Consolidate related logic

5. **Verify Changes**
   - Confirm all original features remain intact
   - Run existing tests if available: `npm test` or `pytest`
   - Show diff of changes for user review

6. **Document Significant Changes**
   - Summarize what was simplified and why
   - Note any patterns that could be applied elsewhere

## Usage Examples

```
/simplify src/utils/helper.ts
/simplify backend/app/services/
/simplify  # (will check recently modified files)
```

## Anti-Patterns to Avoid

- ❌ Nested ternary operators → Use switch/if-else
- ❌ Overly compact one-liners → Prefer clarity over brevity
- ❌ Removing helpful abstractions → Keep code organized
- ❌ Combining too many concerns → Single responsibility
