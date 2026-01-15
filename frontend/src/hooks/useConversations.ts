import { useCallback, useState } from "react"

import { ChatService } from "@/client"
import type {
    ConversationPublic,
    ConversationWithMessages,
    MessagePublic,
} from "@/client/types.gen"
import { useChatStore } from "@/stores/chatStore"

/**
 * Hook for managing conversations with backend API sync.
 * Handles loading, creating, updating, and deleting conversations.
 */
export function useConversations() {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const {
        conversations,
        currentConversationId,
        setConversations,
        setCurrentConversation,
        addConversationFromServer,
        updateConversationFromServer,
        removeConversation,
    } = useChatStore()

    /**
     * Load all conversations from the server
     */
    const loadConversations = useCallback(async () => {
        setIsLoading(true)
        setError(null)
        try {
            const response = await ChatService.readConversations({ limit: 100 })
            setConversations(
                response.data.map((conv) => ({
                    id: conv.id,
                    title: conv.title || "新对话",
                    messages: [],
                    createdAt: new Date(conv.created_at),
                    updatedAt: new Date(conv.updated_at),
                    isPinned: conv.is_pinned,
                })),
            )
        } catch (err) {
            console.error("Failed to load conversations:", err)
            setError("加载对话历史失败")
        } finally {
            setIsLoading(false)
        }
    }, [setConversations])

    /**
     * Load a specific conversation with all its messages
     */
    const loadConversation = useCallback(
        async (conversationId: string) => {
            setIsLoading(true)
            setError(null)
            try {
                const conv: ConversationWithMessages =
                    await ChatService.readConversation({ conversationId })
                setCurrentConversation(conversationId, conv.messages || [])
                return conv
            } catch (err) {
                console.error("Failed to load conversation:", err)
                setError("加载对话详情失败")
                return null
            } finally {
                setIsLoading(false)
            }
        },
        [setCurrentConversation],
    )

    /**
     * Create a new conversation on the server
     */
    const createConversation = useCallback(
        async (title?: string): Promise<ConversationPublic | null> => {
            try {
                const conv = await ChatService.createConversation({
                    requestBody: { title: title || null },
                })
                addConversationFromServer({
                    id: conv.id,
                    title: conv.title || "新对话",
                    messages: [],
                    createdAt: new Date(conv.created_at),
                    updatedAt: new Date(conv.updated_at),
                    isPinned: conv.is_pinned,
                })
                return conv
            } catch (err) {
                console.error("Failed to create conversation:", err)
                setError("创建对话失败")
                return null
            }
        },
        [addConversationFromServer],
    )

    /**
     * Update conversation (title, pinned status)
     */
    const updateConversation = useCallback(
        async (
            conversationId: string,
            updates: { title?: string; is_pinned?: boolean },
        ) => {
            try {
                const conv = await ChatService.updateConversation({
                    conversationId,
                    requestBody: {
                        title: updates.title,
                        is_pinned: updates.is_pinned,
                    },
                })
                updateConversationFromServer(conversationId, {
                    title: conv.title || "新对话",
                    isPinned: conv.is_pinned,
                })
                return conv
            } catch (err) {
                console.error("Failed to update conversation:", err)
                setError("更新对话失败")
                return null
            }
        },
        [updateConversationFromServer],
    )

    /**
     * Delete a conversation
     */
    const deleteConversation = useCallback(
        async (conversationId: string) => {
            try {
                await ChatService.deleteConversation({ conversationId })
                removeConversation(conversationId)
                return true
            } catch (err) {
                console.error("Failed to delete conversation:", err)
                setError("删除对话失败")
                return false
            }
        },
        [removeConversation],
    )

    /**
     * Send a message and save to server
     */
    const sendMessage = useCallback(
        async (
            conversationId: string,
            role: "user" | "assistant",
            content: string,
        ): Promise<MessagePublic | null> => {
            try {
                const message = await ChatService.sendMessage({
                    conversationId,
                    requestBody: { role, content },
                })
                return message
            } catch (err) {
                console.error("Failed to send message:", err)
                setError("发送消息失败")
                return null
            }
        },
        [],
    )

    return {
        // State
        conversations,
        currentConversationId,
        isLoading,
        error,

        // Actions
        loadConversations,
        loadConversation,
        createConversation,
        updateConversation,
        deleteConversation,
        sendMessage,
    }
}
