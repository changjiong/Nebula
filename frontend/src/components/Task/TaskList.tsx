import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import type { TasksPublic } from "@/client"
import { TasksService } from "@/client"

export function TaskList(): React.JSX.Element {
    const queryClient = useQueryClient()

    const { data, isLoading } = useQuery<TasksPublic>({
        queryKey: ["tasks"],
        queryFn: () => TasksService.readTasks({ skip: 0, limit: 100 }),
    })

    const cancelMutation = useMutation({
        mutationFn: (id: string) => TasksService.cancelTask({ id }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tasks"] })
        },
    })

    function handleCancel(id: string): void {
        if (confirm("Are you sure you want to cancel this task?")) {
            cancelMutation.mutate(id)
        }
    }

    function getStatusColor(status: string): string {
        switch (status) {
            case "completed":
                return "bg-green-100 text-green-800"
            case "failed":
                return "bg-red-100 text-red-800"
            case "running":
                return "bg-blue-100 text-blue-800"
            case "pending":
                return "bg-yellow-100 text-yellow-800"
            case "cancelled":
                return "bg-gray-100 text-gray-800"
            default:
                return "bg-gray-100 text-gray-800"
        }
    }

    if (isLoading) {
        return <div>Loading tasks...</div>
    }

    return (
        <div className="rounded-md border">
            <table className="w-full">
                <thead>
                    <tr className="border-b bg-muted/50">
                        <th className="p-4 text-left font-medium">ID</th>
                        <th className="p-4 text-left font-medium">Status</th>
                        <th className="p-4 text-left font-medium">Created</th>
                        <th className="p-4 text-right font-medium">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {data?.data.map((task) => (
                        <tr key={task.id} className="border-b">
                            <td className="p-4 font-mono text-sm">
                                {task.id.slice(0, 8)}...
                            </td>
                            <td className="p-4">
                                <span
                                    className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${getStatusColor(task.status)}`}
                                >
                                    {task.status}
                                </span>
                            </td>
                            <td className="p-4 text-sm text-muted-foreground">
                                {new Date(task.created_at).toLocaleString()}
                            </td>
                            <td className="p-4 text-right">
                                {task.status !== "completed" &&
                                    task.status !== "failed" &&
                                    task.status !== "cancelled" && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleCancel(task.id)}
                                        >
                                            Cancel
                                        </Button>
                                    )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
