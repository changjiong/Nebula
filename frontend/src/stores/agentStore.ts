import { create } from "zustand"

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
    // TODO: Replace with actual API call
    // const agents = await fetchUserAgents()

    // Mock data for now
    const mockAgents: Agent[] = [
      {
        id: "enterprise_resolver",
        name: "企业主体识别",
        description: "快速识别企业主体",
        icon: "🏢",
        category: "拓客营销",
      },
      {
        id: "kechuang_evaluator",
        name: "科创评价",
        description: "五维评分精准定位",
        icon: "📊",
        category: "风险评估",
      },
      {
        id: "customer_value",
        name: "客户价值评估",
        description: "价值评估精准营销",
        icon: "💰",
        category: "拓客营销",
      },
      {
        id: "counterparty_mining",
        name: "交易对手挖掘",
        description: "挖掘上下游高潜客户",
        icon: "🔗",
        category: "拓客营销",
      },
    ]

    set({ userAgents: mockAgents })
  },

  selectAgent: (agent) => {
    // Trigger conversation with agent
    // For now, we'll just log it
    console.log("Selected agent:", agent)

    // In the future, this should:
    // 1. Insert a system message or user message with agent context
    // 2. Trigger SSE connection with agent context
  },
}))
