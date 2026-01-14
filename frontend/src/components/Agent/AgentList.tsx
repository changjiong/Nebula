import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import type { AgentPublic, AgentsPublic } from "@/client"
import { AgentsService } from "@/client"
import { Button } from "@/components/ui/button"
import { AgentForm } from "./AgentForm"

export function AgentList(): React.JSX.Element {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<AgentPublic | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery<AgentsPublic>({
    queryKey: ["agents"],
    queryFn: () => AgentsService.readAgents({ skip: 0, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => AgentsService.deleteAgent({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    },
  })

  function handleEdit(agent: AgentPublic): void {
    setEditingAgent(agent)
    setIsFormOpen(true)
  }

  function handleDelete(id: string): void {
    if (confirm("Are you sure you want to delete this agent?")) {
      deleteMutation.mutate(id)
    }
  }

  function handleClose(): void {
    setIsFormOpen(false)
    setEditingAgent(null)
  }

  if (isLoading) {
    return <div>Loading agents...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => setIsFormOpen(true)}>Create Agent</Button>
      </div>

      <div className="rounded-md border">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="p-4 text-left font-medium">Name</th>
              <th className="p-4 text-left font-medium">Description</th>
              <th className="p-4 text-left font-medium">Model</th>
              <th className="p-4 text-left font-medium">Temperature</th>
              <th className="p-4 text-left font-medium">Status</th>
              <th className="p-4 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data?.data.map((agent) => (
              <tr key={agent.id} className="border-b">
                <td className="p-4 font-medium">{agent.name}</td>
                <td className="p-4 text-sm text-muted-foreground">
                  {agent.description || "—"}
                </td>
                <td className="p-4 text-sm">{agent.model_name}</td>
                <td className="p-4 text-sm">{agent.temperature}</td>
                <td className="p-4">
                  <span
                    className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                      agent.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {agent.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(agent)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(agent.id)}
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isFormOpen && (
        <AgentForm
          agent={editingAgent}
          onClose={handleClose}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ["agents"] })
            handleClose()
          }}
        />
      )}
    </div>
  )
}
