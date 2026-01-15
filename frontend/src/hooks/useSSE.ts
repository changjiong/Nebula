import { useEffect, useRef } from "react"
import { useChatStore } from "@/stores/chatStore"


export function useSSE(url: string | null) {
  const eventSource = useRef<EventSource | null>(null)
  const { addMessage, updateThinkingStep, setIsConnecting, addThinkingStep } =
    useChatStore()

  useEffect(() => {
    if (!url) {
      if (eventSource.current) {
        eventSource.current.close()
        eventSource.current = null
      }
      return
    }

    setIsConnecting(true)
    eventSource.current = new EventSource(url)

    eventSource.current.onopen = () => {
      console.log("SSE Connected")
      setIsConnecting(false)
    }

    eventSource.current.onerror = (err) => {
      console.error("SSE Error:", err)
      setIsConnecting(false)
      eventSource.current?.close()
    }

    // Default message handler for all events (since backend sends everything as data: {...})
    eventSource.current.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        const eventType = payload.event || payload.type // Support both keys
        const eventData = typeof payload.data === 'string' ? JSON.parse(payload.data) : payload.data

        if (!eventType) return

        switch (eventType) {
          case "tool_call":
            addThinkingStep({
              id: eventData.id,
              title: `调用工具: ${eventData.name}`,
              status: "in-progress",
              content: `参数:\n${JSON.stringify(eventData.arguments, null, 2)}`,
              timestamp: Date.now(),
              // Use api-call icon type
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
                : `执行完成`,
              // Update subitem with result
              subItems: [{
                id: `sub-${eventData.id}`,
                type: "api-call",
                title: eventData.name,
                content: `参数:\n${JSON.stringify({} /* args unavailable here directly unless mapped */, null, 2)}\n\n结果:\n${eventData.result}`,
                previewable: true
              }]
            })
            // Append result to content if needed, or just status update
            break

          case "thinking":
            // Legacy thinking event (or R1 reasoning)
            if (eventData.status === "in-progress" && !eventData.content) {
              // Initial step creation
              addThinkingStep({
                id: eventData.id,
                title: eventData.title,
                status: "in-progress",
                content: "",
                timestamp: Date.now()
              })
            } else {
              // Update
              updateThinkingStep(eventData.id, {
                status: eventData.status,
                content: eventData.content,
                title: eventData.title
              })
            }
            break

          case "message":
            // Standard chat message content
            if (eventData.content) {
              // Add or append message? 
              // Currently addMessage adds a NEW message. 
              // If streaming chunks, we might need a way to append to the LAST message.
              // But our implementation currently yields "partial" messages?
              // Wait, `llm_thinking.py` yields separate chunks. `chat.py` with NFC yields chunks.
              // useChatStore has `updateMessageTransient` but requires message ID.
              // The backend doesn't send message ID in the chunk for NFC generator, only content.
              // So we need to handle "accumulating" the assistant message.

              // For now, let's assume `addMessage` handles accumulation if we pass same ID? 
              // No, addMessage appends to array.

              // We need logic here to create a message ONCE, then update it.
              // Since we don't have a stable message ID from backend for the final answer yet,
              // we can generate one on client side when stream starts? 
              // Or simple workaround: If last message is assistant, update it.

              // Implementation detail: NFC generator in `chat.py` sends `final_response` chunks.
              // It's text content.
              // We should check if we already have an assistant message at the end.
              const { messages, updateMessage, addMessage: storeAddMessage } = useChatStore.getState()
              const lastMsg = messages[messages.length - 1]

              if (lastMsg && lastMsg.role === "assistant" && !lastMsg.agentId /* assuming agentId marks something else? */) {
                // Append to last message
                updateMessage(lastMsg.id, lastMsg.content + eventData.content)
              } else {
                // New message
                storeAddMessage({
                  id: Date.now().toString(),
                  role: "assistant",
                  content: eventData.content,
                  timestamp: Date.now()
                })
              }
            }
            break

          case "error":
            console.error("Stream error:", eventData)
            addThinkingStep({
              id: `error-${Date.now()}`,
              title: "系统错误",
              status: "failed",
              content: eventData.message,
              timestamp: Date.now()
            })
            break

          case "done":
            // Stream finished
            eventSource.current?.close()
            setIsConnecting(false)
            break
        }

      } catch (e) {
        console.error("Failed to parse SSE message:", e)
      }
    }

    return () => {
      eventSource.current?.close()
      eventSource.current = null
      setIsConnecting(false)
    }
  }, [url, addMessage, updateThinkingStep, setIsConnecting, addThinkingStep])
}
