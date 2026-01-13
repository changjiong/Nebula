import { createFileRoute } from "@tanstack/react-router"
import { TaskList } from "@/components/Task/TaskList"

export const Route = createFileRoute("/_layout/tasks")({
    component: TasksPage,
})

function TasksPage(): React.JSX.Element {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Task Monitor</h1>
                <p className="text-muted-foreground mt-2">
                    View and manage background tasks
                </p>
            </div>
            <TaskList />
        </div>
    )
}
