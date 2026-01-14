import { ChevronsLeft, ChevronsRight } from "lucide-react"

import { Logo } from "@/components/Common/Logo"
import { Button } from "@/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { cn } from "@/lib/utils"
import { AgentList } from "./AgentList"
import { ConversationList } from "./ConversationList"
import { NewConversationButton } from "./NewConversationButton"
import { User } from "./User"

export function AppSidebar(): React.JSX.Element {
  const { user: currentUser } = useAuth()
  const { state, toggleSidebar } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center relative">
        <Logo variant="responsive" />

        {/* Custom Trigger */}
        <Button
          onClick={toggleSidebar}
          variant="ghost"
          size="icon"
          className={cn(
            "absolute right-2 top-6 h-6 w-6 text-muted-foreground hidden md:flex",
            isCollapsed && "left-1/2 -translate-x-1/2 top-14 rotate-180",
          )}
        >
          {isCollapsed ? (
            <ChevronsRight className="size-4" />
          ) : (
            <ChevronsLeft className="size-4" />
          )}
        </Button>
      </SidebarHeader>
      <SidebarContent className="px-2">
        {/* New Conversation Button */}
        <NewConversationButton />

        {/* Agent List */}
        <AgentList />

        {/* Conversation History */}
        <ConversationList />

        {/* No separate Management Group anymore, moved to User Menu */}
      </SidebarContent>
      <SidebarFooter>
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
