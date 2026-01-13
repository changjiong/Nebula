import { create } from "zustand"
import { persist } from "zustand/middleware"

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

export const useChatStore = create<ChatState>()(persist((set, get) => ({
  messages: [],
  agents: [],
  thinkingSteps: [],
  isConnecting: false,
  currentAgentId: null,
  conversations: [],
  currentConversationId: null,

  setMessages: (messages) => set({ messages }),
  addMessage: (message) => {
    const { currentConversationId, conversations } = get()

    set((state) => {
      // Clear thinking steps when user sends a new message
      const shouldClearThinking = message.role === "user"

      // Update conversations with new message
      let updatedConversations = state.conversations
      if (currentConversationId) {
        updatedConversations = conversations.map((conv) =>
          conv.id === currentConversationId
            ? {
              ...conv,
              messages: [...conv.messages, message],
              updatedAt: new Date(),
            }
            : conv,
        )
      }

      return {
        messages: [...state.messages, message],
        thinkingSteps: shouldClearThinking ? [] : state.thinkingSteps,
        conversations: updatedConversations,
      }
    })
  },
  updateMessage: (id, content) => {
    const { currentConversationId, conversations } = get()

    set((state) => {
      // Update in state.messages
      const updatedMessages = state.messages.map((msg) =>
        msg.id === id ? { ...msg, content } : msg
      )

      // Also update in conversations
      let updatedConversations = state.conversations
      if (currentConversationId) {
        updatedConversations = conversations.map((conv) =>
          conv.id === currentConversationId
            ? {
              ...conv,
              messages: conv.messages.map((msg) =>
                msg.id === id ? { ...msg, content } : msg
              ),
              updatedAt: new Date(),
            }
            : conv
        )
      }

      return {
        messages: updatedMessages,
        conversations: updatedConversations,
      }
    })
  },

  setAgents: (agents) => set({ agents }),

  addThinkingStep: (step) =>
    set((state) => {
      const existingIndex = state.thinkingSteps.findIndex((s) => s.id === step.id)
      if (existingIndex !== -1) {
        const updated = [...state.thinkingSteps]
        updated[existingIndex] = step
        return { thinkingSteps: updated }
      } else {
        return { thinkingSteps: [...state.thinkingSteps, step] }
      }
    }),
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
}), {
  name: "chat-storage",
  partialize: (state) => ({
    conversations: state.conversations,
    currentConversationId: state.currentConversationId,
  }),
  onRehydrateStorage: () => {
    return (state, error) => {
      if (error) {
        console.error('Hydration error:', error)
        return
      }

      // After loading from localStorage, restore current conversation messages
      if (state?.currentConversationId && state?.conversations) {
        const currentConv = state.conversations.find(
          (c) => c.id === state.currentConversationId
        )
        if (currentConv && currentConv.messages) {
          // Properly update state using Zustand's pattern
          state.messages = currentConv.messages
          console.log(`✅ Restored ${currentConv.messages.length} messages from conversation: ${currentConv.title}`)
        }
      }
    }
  },
}))
