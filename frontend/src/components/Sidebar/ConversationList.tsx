import { Clock, History } from "lucide-react"

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

export function ConversationList() {
    const conversations = useChatStore((state) => state.conversations)
    const currentConversationId = useChatStore(
        (state) => state.currentConversationId,
    )
    const switchConversation = useChatStore((state) => state.switchConversation)

    if (conversations.length === 0) {
        return null
    }

    return (
        <Collapsible defaultOpen className="mt-4">
            <CollapsibleTrigger className="flex items-center gap-2 w-full px-2 py-1.5 text-sm font-medium hover:bg-accent rounded-md">
                <History className="h-4 w-4" />
                <span>历史对话</span>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-1 space-y-1">
                {conversations.map((conv) => (
                    <div
                        key={conv.id}
                        onClick={() => switchConversation(conv.id)}
                        className={cn(
                            "cursor-pointer p-2 rounded-md text-sm flex items-start gap-2 hover:bg-accent",
                            currentConversationId === conv.id && "bg-accent",
                        )}
                    >
                        <Clock className="h-4 w-4 mt-0.5 shrink-0" />
                        <span className="truncate">{conv.title || "新对话"}</span>
                    </div>
                ))}
            </CollapsibleContent>
        </Collapsible>
    )
}
