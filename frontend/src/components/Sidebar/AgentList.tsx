import { Bot } from "lucide-react"
import { useEffect } from "react"

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { useAgentStore } from "@/stores/agentStore"

export function AgentList() {
    const userAgents = useAgentStore((state) => state.userAgents)
    const selectAgent = useAgentStore((state) => state.selectAgent)
    const loadUserAgents = useAgentStore((state) => state.loadUserAgents)

    useEffect(() => {
        loadUserAgents()
    }, [loadUserAgents])

    if (userAgents.length === 0) {
        return null
    }

    return (
        <Collapsible defaultOpen className="mt-4">
            <CollapsibleTrigger className="flex items-center gap-2 w-full px-2 py-1.5 text-sm font-medium hover:bg-accent rounded-md">
                <Bot className="h-4 w-4" />
                <span>我的 Agent</span>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-1 space-y-1">
                {userAgents.map((agent) => (
                    <div
                        key={agent.id}
                        onClick={() => selectAgent(agent)}
                        className="cursor-pointer p-2 rounded-md text-sm flex items-start gap-2 hover:bg-accent"
                    >
                        <span className="shrink-0">{agent.icon || "🤖"}</span>
                        <div className="min-w-0">
                            <div className="font-medium truncate">{agent.name}</div>
                            {agent.description && (
                                <div className="text-xs text-muted-foreground truncate">
                                    {agent.description}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </CollapsibleContent>
        </Collapsible>
    )
}
