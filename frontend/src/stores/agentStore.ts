import { create } from "zustand"
import { AgentsService } from "@/client/sdk.gen"

export interface Agent {
  id: string
  name: string
  description: string
  icon?: string
  category: string
}

interface AgentStore {
  userAgents: Agent[]
  loadUserAgents: () => Promise<void>
  selectAgent: (agent: Agent) => void
}

export const useAgentStore = create<AgentStore>((set) => ({
  userAgents: [],

  loadUserAgents: async () => {
    try {
      const response = await AgentsService.readAgents({ limit: 100 })

      // Map to local Agent interface if needed, or cast if identical
      const agents: Agent[] = response.data.map((agent: any) => ({
        id: agent.id,
        name: agent.name,
        description: agent.description || "",
        icon: agent.icon,
        category: agent.category || "General",
      }))

      set({ userAgents: agents })
    } catch (error) {
      console.error("Error loading agents:", error)
      set({ userAgents: [] })
    }
  },

  selectAgent: (agent) => {
    // Trigger conversation with agent
    console.log("Selected agent:", agent)
    // Future: Connect to real agent endpoint
  },
}))
