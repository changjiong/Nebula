import { create } from "zustand"

export interface Agent {
  id: string
  name: string
  avatar: string
  description: string
  capabilities: string[]
}

export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: number
  agentId?: string
}

export interface ThinkingStep {
  id: string
  title: string
  status: "pending" | "in-progress" | "completed" | "failed"
  content: string
  timestamp: number
}

interface ChatState {
  messages: Message[]
  agents: Agent[]
  thinkingSteps: ThinkingStep[]
  isConnecting: boolean
  currentAgentId: string | null

  // Actions
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, content: string) => void

  setAgents: (agents: Agent[]) => void

  addThinkingStep: (step: ThinkingStep) => void
  updateThinkingStep: (id: string, updates: Partial<ThinkingStep>) => void

  setIsConnecting: (status: boolean) => void
  setCurrentAgentId: (id: string | null) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  agents: [],
  thinkingSteps: [],
  isConnecting: false,
  currentAgentId: null,

  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  updateMessage: (id, content) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, content } : msg,
      ),
    })),

  setAgents: (agents) => set({ agents }),

  addThinkingStep: (step) =>
    set((state) => ({ thinkingSteps: [...state.thinkingSteps, step] })),
  updateThinkingStep: (id, updates) =>
    set((state) => ({
      thinkingSteps: state.thinkingSteps.map((step) =>
        step.id === id ? { ...step, ...updates } : step,
      ),
    })),

  setIsConnecting: (isConnecting) => set({ isConnecting }),
  setCurrentAgentId: (currentAgentId) => set({ currentAgentId }),
}))
