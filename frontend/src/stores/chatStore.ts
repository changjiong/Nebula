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

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
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

  // Conversation management
  conversations: Conversation[]
  currentConversationId: string | null

  // Actions
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, content: string) => void

  setAgents: (agents: Agent[]) => void

  addThinkingStep: (step: ThinkingStep) => void
  updateThinkingStep: (id: string, updates: Partial<ThinkingStep>) => void

  setIsConnecting: (status: boolean) => void
  setCurrentAgentId: (id: string | null) => void

  // Thinking steps actions
  clearThinkingSteps: () => void

  // Conversation actions
  createNewConversation: () => void
  switchConversation: (id: string) => void
  deleteConversation: (id: string) => void
  updateConversationTitle: (id: string, title: string) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  agents: [],
  thinkingSteps: [],
  isConnecting: false,
  currentAgentId: null,
  conversations: [],
  currentConversationId: null,

  setMessages: (messages) => set({ messages }),
  addMessage: (message) => {
    set((state) => {
      // Clear thinking steps when user sends a new message
      const shouldClearThinking = message.role === "user"
      return {
        messages: [...state.messages, message],
        thinkingSteps: shouldClearThinking ? [] : state.thinkingSteps,
      }
    })
    // Update current conversation
    const { currentConversationId, conversations } = get()
    if (currentConversationId) {
      const updatedConversations = conversations.map((conv) =>
        conv.id === currentConversationId
          ? {
            ...conv,
            messages: [...conv.messages, message],
            updatedAt: new Date(),
          }
          : conv,
      )
      set({ conversations: updatedConversations })
    }
  },
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

  clearThinkingSteps: () => set({ thinkingSteps: [] }),

  createNewConversation: () => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: "新对话",
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    set((state) => ({
      conversations: [newConv, ...state.conversations],
      currentConversationId: newConv.id,
      messages: [],
      thinkingSteps: [],
    }))
  },

  switchConversation: (id) => {
    const conv = get().conversations.find((c) => c.id === id)
    if (conv) {
      set({
        currentConversationId: id,
        messages: conv.messages,
        thinkingSteps: [],
      })
    }
  },

  deleteConversation: (id) => {
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      ...(state.currentConversationId === id
        ? { currentConversationId: null, messages: [], thinkingSteps: [] }
        : {}),
    }))
  },

  updateConversationTitle: (id, title) => {
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === id ? { ...c, title, updatedAt: new Date() } : c,
      ),
    }))
  },
}))
