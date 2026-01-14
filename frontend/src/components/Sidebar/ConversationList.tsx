import { Clock, History, Search } from "lucide-react"
import { useState, useMemo } from "react"

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

export function ConversationList() {
    const conversations = useChatStore((state) => state.conversations)
    const currentConversationId = useChatStore(
        (state) => state.currentConversationId,
    )
    const switchConversation = useChatStore((state) => state.switchConversation)

    const [searchQuery, setSearchQuery] = useState("")

    // Filter conversations based on search query
    const filteredConversations = useMemo(() => {
        if (!searchQuery.trim()) {
            return conversations
        }
        const query = searchQuery.toLowerCase()
        return conversations.filter((conv) =>
            (conv.title || "新对话").toLowerCase().includes(query)
        )
    }, [conversations, searchQuery])

    if (conversations.length === 0) {
        return null
    }

    return (
        <Collapsible defaultOpen className="mt-4">
            <CollapsibleTrigger className="flex items-center gap-2 w-full px-2 py-1.5 text-sm font-medium hover:bg-accent rounded-md">
                <History className="h-4 w-4" />
                <span>历史对话</span>
                {conversations.length > 0 && (
                    <span className="ml-auto text-xs text-muted-foreground">
                        {conversations.length}
                    </span>
                )}
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-1 space-y-1">
                {/* Search input */}
                {conversations.length > 3 && (
                    <div className="relative px-1 mb-2">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                        <Input
                            type="text"
                            placeholder="搜索对话..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="h-8 pl-8 text-xs"
                        />
                    </div>
                )}

                {/* Conversation list */}
                {filteredConversations.length > 0 ? (
                    filteredConversations.map((conv) => (
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
                    ))
                ) : (
                    <div className="px-2 py-4 text-xs text-muted-foreground text-center">
                        未找到匹配的对话
                    </div>
                )}
            </CollapsibleContent>
        </Collapsible>
    )
}
