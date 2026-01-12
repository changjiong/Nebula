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

    // Listen for 'message' events (chat messages)
    eventSource.current.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data)
        addMessage({
          id: data.id || Date.now().toString(),
          role: data.role,
          content: data.content,
          timestamp: Date.now(),
          agentId: data.agentId,
        })
      } catch (e) {
        console.error("Failed to parse message:", e)
      }
    })

    // Listen for 'thought' events (thinking chain updates)
    eventSource.current.addEventListener("thought", (event) => {
      try {
        const data = JSON.parse(event.data)
        // Assuming data contains: { id, type: 'new' | 'update', ...stepData }
        if (data.type === "new") {
          addThinkingStep({
            id: data.id,
            title: data.title,
            status: "in-progress",
            content: data.content || "",
            timestamp: Date.now(),
          })
        } else if (data.type === "update") {
          updateThinkingStep(data.id, data.updates)
        }
      } catch (e) {
        console.error("Failed to parse thought:", e)
      }
    })

    return () => {
      eventSource.current?.close()
      eventSource.current = null
      setIsConnecting(false)
    }
  }, [url, addMessage, updateThinkingStep, setIsConnecting, addThinkingStep])
}
