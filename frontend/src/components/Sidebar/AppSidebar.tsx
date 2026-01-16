import { ChevronsLeft, ChevronsRight } from "lucide-react"

import { Logo } from "@/components/Common/Logo"
import { Button } from "@/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
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
      <SidebarHeader className="px-4 py-4 group-data-[collapsible=icon]:px-2 group-data-[collapsible=icon]:py-3 group-data-[collapsible=icon]:items-center">
        {/* When collapsed: show expand button at top */}
        {isCollapsed ? (
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={toggleSidebar}
                tooltip="Expand Sidebar"
                className="h-8 w-8"
              >
                <ChevronsRight className="size-4" />
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        ) : (
          <div className="flex items-center justify-between w-full">
            <Logo variant="responsive" />
            <Button
              onClick={toggleSidebar}
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-muted-foreground hover:text-foreground hidden md:flex"
            >
              <ChevronsLeft className="size-4" />
            </Button>
          </div>
        )}
      </SidebarHeader>
      <SidebarContent className="px-2 group-data-[collapsible=icon]:px-1">
        {/* New Conversation Button */}
        <NewConversationButton />

        {/* Agent List */}
        <AgentList />



        {/* Conversation History */}
        <ConversationList />
      </SidebarContent>
      <SidebarFooter>
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
