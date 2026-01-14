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
  isPinned?: boolean
}

// 子项类型：搜索结果、文件操作、API调用等
export interface StepSubItem {
  id: string
  type: "search-result" | "file-operation" | "api-call" | "text"
  title: string
  icon?: string // 图标URL或icon名称
  source?: string // 来源域名（搜索结果用）
  content?: string // 可在画布中展示的详细内容
  previewable: boolean // 是否可点击查看详情
}

export interface ThinkingStep {
  id: string
  title: string
  status: "pending" | "in-progress" | "completed" | "failed"
  content: string
  timestamp: number
  // Timeline UI 扩展字段
  group?: string // 所属分组名称（如"开始研究"）
  subItems?: StepSubItem[] // 子项列表
  isCollapsible?: boolean // 是否可折叠
  defaultExpanded?: number // 默认展开的子项数量
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

  // Canvas state (right-side detail panel)
  canvasContent: StepSubItem | null
  isCanvasOpen: boolean

  // Actions
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  updateMessage: (id: string, content: string) => void
  updateMessageTransient: (id: string, content: string) => void
  syncMessageToConversation: (id: string) => void

  setAgents: (agents: Agent[]) => void

  addThinkingStep: (step: ThinkingStep) => void
  updateThinkingStep: (id: string, updates: Partial<ThinkingStep>) => void

  setIsConnecting: (status: boolean) => void
  setCurrentAgentId: (id: string | null) => void

  // Thinking steps actions
  clearThinkingSteps: () => void

  // Conversation actions
  createNewConversation: () => void
  resetToHome: () => void // Go back to "What can I help you with?" without creating a conversation
  switchConversation: (id: string) => void
  deleteConversation: (id: string) => void
  updateConversationTitle: (id: string, title: string) => void
  toggleConversationPin: (id: string) => void

  // Canvas actions
  openCanvas: (item: StepSubItem) => void
  closeCanvas: () => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      agents: [],
      thinkingSteps: [],
      isConnecting: false,
      currentAgentId: null,
      conversations: [],
      currentConversationId: null,
      canvasContent: null,
      isCanvasOpen: false,

      setMessages: (messages) => set({ messages }),
      addMessage: (message) => {
        const { currentConversationId } = get()

        set((state) => {
          // Clear thinking steps when user sends a new message
          const shouldClearThinking = message.role === "user"

          // Lazy creation: If no current conversation, create one now
          let targetConversationId = currentConversationId
          let updatedConversations = state.conversations

          if (!targetConversationId) {
            // Create new conversation on the fly
            const newConv: Conversation = {
              id: crypto.randomUUID(),
              title: "Temp Title", // Will be auto-updated below
              messages: [],
              createdAt: new Date(),
              updatedAt: new Date(),
            }
            targetConversationId = newConv.id
            updatedConversations = [newConv, ...state.conversations]

            // We also need to update the state immediately so the view switches
            // NOTE: We return the partial state update at the end, which handles this.
          }

          // Update conversations with new message
          if (targetConversationId) {
            updatedConversations = updatedConversations.map((conv) => {
              if (conv.id === targetConversationId) {
                // Auto-name: if this is user's first message and title is default
                let newTitle = conv.title
                if (
                  message.role === "user" &&
                  conv.messages.filter((m) => m.role === "user").length === 0 &&
                  (conv.title === "Temp Title" ||
                    conv.title === "新对话" ||
                    conv.title === "New Conversation" ||
                    !conv.title)
                ) {
                  // Use first 50 chars of message as title
                  newTitle = message.content.slice(0, 50).trim()
                  if (message.content.length > 50) {
                    newTitle += "..."
                  }
                }

                return {
                  ...conv,
                  title: newTitle,
                  messages: [...conv.messages, message],
                  updatedAt: new Date(),
                }
              }
              return conv
            })
          }

          return {
            currentConversationId: targetConversationId, // Ensure we switch to it
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
            msg.id === id ? { ...msg, content } : msg,
          )

          // Also update in conversations
          let updatedConversations = state.conversations
          if (currentConversationId) {
            updatedConversations = conversations.map((conv) =>
              conv.id === currentConversationId
                ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === id ? { ...msg, content } : msg,
                  ),
                  updatedAt: new Date(),
                }
                : conv,
            )
          }

          return {
            messages: updatedMessages,
            conversations: updatedConversations,
          }
        })
      },

      updateMessageTransient: (id, content) => {
        // Only update the 'messages' array (view state), NOT 'conversations' (persisted state)
        // This avoids triggering localStorage write on every keystroke/token
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, content } : msg,
          ),
        }))
      },

      syncMessageToConversation: (id) => {
        // Sync a specific message from view state to persisted conversations
        const { currentConversationId, messages } = get()
        const messageToSync = messages.find((m) => m.id === id)

        if (!currentConversationId || !messageToSync) return

        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === currentConversationId
              ? {
                ...conv,
                messages: conv.messages.map((msg) =>
                  msg.id === id
                    ? { ...msg, content: messageToSync.content }
                    : msg,
                ),
                updatedAt: new Date(),
              }
              : conv,
          ),
        }))
      },

      setAgents: (agents) => set({ agents }),

      addThinkingStep: (step) =>
        set((state) => {
          const existingIndex = state.thinkingSteps.findIndex(
            (s) => s.id === step.id,
          )
          if (existingIndex !== -1) {
            const updated = [...state.thinkingSteps]
            updated[existingIndex] = step
            return { thinkingSteps: updated }
          }
          return { thinkingSteps: [...state.thinkingSteps, step] }
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

      resetToHome: () => {
        set({
          currentConversationId: null,
          messages: [],
          thinkingSteps: [],
        })
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

      toggleConversationPin: (id) => {
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, isPinned: !c.isPinned } : c,
          ),
        }))
      },

      // Canvas actions
      openCanvas: (item) => set({ canvasContent: item, isCanvasOpen: true }),
      closeCanvas: () => set({ canvasContent: null, isCanvasOpen: false }),
    }),
    {
      name: "chat-storage",
      partialize: (state) => ({
        conversations: state.conversations,
        currentConversationId: state.currentConversationId,
      }),
      onRehydrateStorage: () => {
        return (state, error) => {
          if (error) {
            console.error("Hydration error:", error)
            return
          }

          // After loading from localStorage, restore current conversation messages
          if (state?.currentConversationId && state?.conversations) {
            const currentConv = state.conversations.find(
              (c) => c.id === state.currentConversationId,
            )
            if (currentConv?.messages) {
              // Properly update state using Zustand's pattern
              state.messages = currentConv.messages
              console.log(
                `✅ Restored ${currentConv.messages.length} messages from conversation: ${currentConv.title}`,
              )
            }
          }
        }
      },
    },
  ),
)
