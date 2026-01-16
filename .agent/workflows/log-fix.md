---
description: Log a bug fix to docs/issue-log.md
---

1.  **Analyze Context**: Review the recent conversation history to identify:
    -   **Issue**: A brief title and description of the problem.
    -   **Cause**: The root cause of the issue (if known).
    -   **Fix**: The steps taken or code changes applied to resolve it.
    -   **Files**: A list of files that were modified during the fix.

2.  **Format Entry**: Generate a new log entry using the following Markdown format:
    ```markdown
    ### [YYYY-MM-DD] <Issue Title>
    - **Description**: <Brief description>
    - **Cause**: <Root cause>
    - **Fix**: <Summary of fix>
    - **Files Modified**:
      - `<file_path_1>`
      - `<file_path_2>`
    ```
    *Ensure you use the current date.*

3.  **Read Log File**: Read the content of `docs/issue-log.md`.

4.  **Append Entry**: Append the new entry to the end of `docs/issue-log.md`.
    -   Use `run_command` with `cat >>` if safe, or read the file and use `write_to_file` to overwrite with the appended content.
    -   Ensure there is a blank line before the new entry.
