import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import AppSidebar from "@/components/Sidebar/AppSidebar"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { isLoggedIn } from "@/hooks/useAuth"
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

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <main className="flex-1 p-6 md:p-8 flex flex-col">
          <div className="mx-auto max-w-7xl flex-1 w-full flex flex-col">
            <Outlet />
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default Layout
