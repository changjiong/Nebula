import { Bot, ChevronDown } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { useAgentStore } from "@/stores/agentStore"

// Category icons mapping (using Lucide icons would be better, but emojis work for now)
const categoryIcons: Record<string, string> = {
  entity_resolution: "🏢",
  risk_evaluation: "📊",
  relationship_mining: "🔗",
  marketing: "💰",
  default: "🤖",
}

export function AgentList() {
  const userAgents = useAgentStore((state) => state.userAgents)
  const selectAgent = useAgentStore((state) => state.selectAgent)
  const loadUserAgents = useAgentStore((state) => state.loadUserAgents)
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"
  const [isOpen, setIsOpen] = useState(true)

  useEffect(() => {
    loadUserAgents()
  }, [loadUserAgents])

  // Take first 5 agents for display
  const displayAgents = useMemo(() => userAgents.slice(0, 5), [userAgents])

  if (userAgents.length === 0) {
    return null
  }

  // When collapsed, show only the Bot icon as a group indicator
  if (isCollapsed) {
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton tooltip="Agents">
            <Bot className="size-4" />
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    )
  }

  return (
    <SidebarMenu>
      <Collapsible
        open={isOpen}
        onOpenChange={setIsOpen}
        className="group/collapsible"
      >
        <SidebarMenuItem>
          <CollapsibleTrigger asChild>
            <SidebarMenuButton tooltip="Agents">
              <Bot className="size-4" />
              <span>Agents</span>
              <ChevronDown className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
            </SidebarMenuButton>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <SidebarMenuSub>
              {displayAgents.map((agent) => (
                <SidebarMenuSubItem key={agent.id}>
                  <SidebarMenuSubButton
                    onClick={() => selectAgent(agent)}
                    className="text-sm"
                  >
                    <span className="shrink-0">
                      {agent.icon ||
                        categoryIcons[agent.category || "default"] ||
                        "🤖"}
                    </span>
                    <span className="truncate">{agent.name}</span>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
              ))}
            </SidebarMenuSub>
          </CollapsibleContent>
        </SidebarMenuItem>
      </Collapsible>
    </SidebarMenu>
  )
}
