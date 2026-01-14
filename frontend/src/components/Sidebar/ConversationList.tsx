import { ChevronRight, MoreHorizontal } from "lucide-react"
import { useState } from "react"
import { HistoryModal } from "@/components/Chat/HistoryModal"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

export function ConversationList() {
  const conversations = useChatStore((state) => state.conversations)
  const currentConversationId = useChatStore(
    (state) => state.currentConversationId,
  )
  const switchConversation = useChatStore((state) => state.switchConversation)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"

  if (conversations.length === 0) {
    return null
  }

  // Limit displayed items
  const MAX_ITEMS = 10
  const displayConversations = conversations.slice(0, MAX_ITEMS)

  return (
    <Collapsible defaultOpen className="group/collapsible">
      <SidebarGroup>
        <SidebarGroupLabel
          asChild
          className="group/label w-full justify-between hover:bg-sidebar-accent hover:text-sidebar-accent-foreground cursor-pointer"
        >
          <CollapsibleTrigger>
            <span>History</span>
            <ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90" />
          </CollapsibleTrigger>
        </SidebarGroupLabel>
        <CollapsibleContent>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* Timeline Container */}
              <div
                className={cn(
                  "relative ml-3 border-l border-sidebar-border pl-2 my-1",
                  isCollapsed && "ml-0 border-l-0 pl-0",
                )}
              >
                {displayConversations.map((conv) => (
                  <SidebarMenuItem key={conv.id}>
                    <SidebarMenuButton
                      onClick={() => switchConversation(conv.id)}
                      isActive={currentConversationId === conv.id}
                      className="h-8 text-xs mb-1"
                      tooltip={conv.title || "New Conversation"}
                    >
                      <span
                        className={cn(
                          "truncate",
                          currentConversationId === conv.id && "font-semibold",
                        )}
                      >
                        {conv.title || "New Conversation"}
                      </span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}

                {conversations.length > MAX_ITEMS && (
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      onClick={() => setIsModalOpen(true)}
                      className="text-xs text-muted-foreground h-7"
                      tooltip="View All"
                    >
                      <MoreHorizontal className="size-3 mr-2" />
                      <span>View All ({conversations.length})</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )}
              </div>
            </SidebarMenu>
          </SidebarGroupContent>
        </CollapsibleContent>
      </SidebarGroup>

      <HistoryModal open={isModalOpen} onOpenChange={setIsModalOpen} />
    </Collapsible>
  )
}
