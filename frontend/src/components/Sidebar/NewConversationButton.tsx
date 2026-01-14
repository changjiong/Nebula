import { Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useChatStore } from "@/stores/chatStore"

export function NewConversationButton() {
  const createNewConversation = useChatStore(
    (state) => state.createNewConversation,
  )

  return (
    <Button onClick={createNewConversation} className="w-full" size="sm">
      <Plus className="mr-2 h-4 w-4" />
      新建对话
    </Button>
  )
}
