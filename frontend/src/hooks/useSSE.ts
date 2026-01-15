import { useRef, useState, useCallback } from "react"
import { useChatStore } from "@/stores/chatStore"

export function useSSE() {
  const [isStreaming, setIsStreaming] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)

  const {
    addMessage,
    updateMessageTransient,
    addThinkingStep,
    updateThinkingStep,
    syncMessageToConversation,
    setIsConnecting
  } = useChatStore()

  const streamMessage = useCallback(async (
    payload: {
      content: string;
      model: string;
      provider_id?: string | null;
      conversation_id: string
    }
  ) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    const abortController = new AbortController()
    abortControllerRef.current = abortController
    setIsStreaming(true)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"

      const response = await fetch(`${apiUrl}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          role: "user",
          content: payload.content,
          model: payload.model,
          provider_id: payload.provider_id || null,
        }),
        signal: abortController.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) return

      // Create initial assistant message placeholder
      const assistantMessageId = (Date.now() + 1).toString()
      addMessage({
        id: assistantMessageId,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ""

      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          if (!line.trim()) continue
          if (!line.startsWith("data: ")) continue

          const data = line.slice(6).trim()
          if (data === "[DONE]") break

          try {
            const payload = JSON.parse(data)
            // Backend sends { event: "...", data: "..." }
            // Where data might be a JSON string or object
            const eventType = payload.event || payload.type

            // Parse nested data if string
            let eventData = payload.data
            if (typeof eventData === 'string') {
              try {
                eventData = JSON.parse(eventData)
              } catch {
                // Keep as string if not JSON
              }
            }

            if (!eventType) continue

            switch (eventType) {
              case "tool_call":
                addThinkingStep({
                  id: eventData.id,
                  title: `调用工具: ${eventData.name}`,
                  status: "in-progress",
                  content: `参数:\n${JSON.stringify(eventData.arguments, null, 2)}`,
                  timestamp: Date.now(),
                  subItems: [{
                    id: `sub-${eventData.id}`,
                    type: "api-call",
                    title: eventData.name,
                    content: JSON.stringify(eventData.arguments, null, 2),
                    previewable: true
                  }]
                })
                break

              case "tool_result":
                updateThinkingStep(eventData.id, {
                  status: eventData.success ? "completed" : "failed",
                  content: eventData.error
                    ? `执行失败: ${eventData.error}`
                    : `执行完成\n\n结果:\n${eventData.result}`,
                  subItems: [{
                    id: `sub-${eventData.id}`,
                    type: "api-call",
                    title: eventData.name,
                    content: `参数:\n${JSON.stringify({} /* args unavailable */, null, 2)}\n\n结果:\n${eventData.result}`,
                    previewable: true
                  }]
                })
                break

              case "thinking":
                // 思考过程 (Chain of Thought)
                // thinking event data: { id, title, status, content, timestamp }
                if (eventData.status === "in-progress" && !eventData.content) {
                  addThinkingStep({
                    id: eventData.id || `think-${Date.now()}`,
                    title: eventData.title || "Thinking...",
                    status: "in-progress",
                    content: "",
                    timestamp: Date.now()
                  })
                } else {
                  updateThinkingStep(eventData.id, {
                    status: eventData.status,
                    content: eventData.content,
                    title: eventData.title
                  })
                }
                break

              case "message":
                if (eventData.content) {
                  assistantMessage += eventData.content
                  updateMessageTransient(assistantMessageId, assistantMessage)
                }
                break

              case "error":
                console.error("Stream error event:", eventData)
                assistantMessage += `\n[系统错误: ${eventData.message || '未知错误'}]`
                updateMessageTransient(assistantMessageId, assistantMessage)
                break
            }
          } catch (e) {
            console.error("Failed to parse chunk:", e)
          }
        }
      }

      // Final sync to server
      // Note: We need to update the conversation on server
      // Ideally use a hook or service. existing InputBox logic used sendMessage provided by useConversations
      // Here we rely on store sync, but we might need to explicitly call API to save assistant msg if backend doesn't save stream.
      // *Backend chat/stream endpoint usually doesn't save the assistant response automatically unless configured.*
      // Actually `chat.py` nfc_stream_generator doesn't seem to save the final message to DB?
      // Wait, `chat.py` creates the USER message. But assistant message?
      // Checking `chat.py`: it yields chunks. It doesn't seem to persist the final assistant response.
      // So client MUST save it.

      // We need to saving logic here.
      // We can't use useConversations hook inside this callback easily if it's not passed in.
      // But we can accept a callback or use the store if it had an action.
      // For now, let's just sync to local store ID. Caller (InputBox) is responsible for server save?
      // Or we move server save logic here.
      // Let's defer server save to the caller or add it to args.

      syncMessageToConversation(assistantMessageId)
      return { assistantMessageId, content: assistantMessage }

    } catch (error) {
      console.error("Stream request failed:", error)
      throw error
    } finally {
      setIsConnecting(false)
      setIsStreaming(false)
      abortControllerRef.current = null
    }
  }, [addMessage, updateMessageTransient, addThinkingStep, updateThinkingStep, syncMessageToConversation])

  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsStreaming(false)
    }
  }, [])

  return { streamMessage, isStreaming, abort }
}
