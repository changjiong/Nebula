# Global Project Rules

These rules apply to all interactions within the **Talos** project.

## 1. Technology Stack & consistency
- **Backend**: 
  - Framework: **FastAPI** (Async default).
  - ORM: **SQLModel** (Combine Pydantic models & SQLAlchemy tables).
  - Package Manager: **uv**.
- **Frontend**: 
  - Framework: **React** + **Vite** + **TypeScript**.
  - State Management: **Zustand** or React Context (Avoid Redux).
  - Styling: **Tailwind CSS** + **shadcn/ui**.
  - Networking: **TanStack Query** (React Query) + Generated Client.
- **Constaint**: Do not introduce new heavy dependencies or alternative frameworks without explicit user approval.

## 2. Code Quality Standards
- **Type Safety**: strict type checking is enabled. Avoid `any` types in TypeScript and use Pydantic models for Python type validation.
- **Async/Await**: Ensure all I/O bound operations (DB, API calls) are asynchronous.
- **Error Handling**: Use structured exception handling. Backend should raise `HTTPException` with clear details. Frontend should handle errors gracefully (e.g., Toasts or Error Boundaries).
- **Comments**: Comment complex logic. For "Thinking Chain" or Agentic parts, document the reasoning process.

## 3. Agentic Workflows ("The Way We Work")
- **Bug Fixes**: 在执行修复 bug 之前，请从 `docs/issue-log.md` 文件查看之前的修复历史。修复完成后，**始终**检查是否应触发 `/log-fix` 工作流以记录解决方案。
- **New Capabilities**: When implementing a new complex business logic, consider if it should be encapsulated as a **Skill** (in `backend/app/api/routes/skills.py` ) for reusability.
- **Documentation**: If code changes affect the system architecture or API surface, check if `README.md` or `docs/` needs synchronization (Refer to `/sync-docs`).

## 4. Operational Safety
- **Destructive Actions**: Never delete data directories, drop tables, or perform `rm -rf` on non-temporary folders without explicit confirmation.
- **Secrets**: Never hardcode secrets. Use `.env` variables and `app/core/config.py`.
## 5. Data & API Integrity
- **No Mock Data**: 禁止在前端或后端使用模拟数据（Mock Data）。所有展示的数据必须源自真实的后端 API。
- **API-First Development**: 如果所需数据没有对应的 API，必须先设计并实现后端 API 及相应的数据库模型（SQLModel），严禁在前端硬编码临时数据。

## 6. Communication Style
- **Language**: 默认使用**中文**进行对话和解释。
- **Conciseness**: Give direct answers. When code is requested, provide the full runnable block or clear diffs.
