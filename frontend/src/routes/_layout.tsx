import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { useEffect } from "react"

import AppSidebar from "@/components/Sidebar/AppSidebar"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { isLoggedIn } from "@/hooks/useAuth"
import { useConversations } from "@/hooks/useConversations"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  // Enable global keyboard shortcuts
  useKeyboardShortcuts()

  // Load conversations from server on mount
  const { loadConversations } = useConversations()

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <AppSidebar />
      <SidebarInset>
        <div className="flex-1 flex flex-col overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-7xl flex-1 w-full flex flex-col h-full">
            <Outlet />
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default Layout
