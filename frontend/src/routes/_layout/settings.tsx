import { createFileRoute } from "@tanstack/react-router"

import { AdminSettings } from "@/components/Admin/AdminSettings"
import ModelSettings from "@/components/ModelSettings"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import UserInformation from "@/components/UserSettings/UserInformation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Settings - ADTEC",
      },
    ],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()

  // Base settings for all users
  const tabs = [
    { value: "my-profile", title: "My Profile", component: UserInformation },
    { value: "password", title: "Password", component: ChangePassword },
    { value: "model-providers", title: "Model Providers", component: ModelSettings },
    { value: "danger-zone", title: "Danger Zone", component: DeleteAccount },
  ]

  // Add Admin tab for superusers
  if (currentUser?.is_superuser) {
    // Insert Admin before Danger Zone
    tabs.splice(tabs.length - 1, 0, {
      value: "admin",
      title: "Admin",
      component: AdminSettings
    })
  }

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-6 h-full">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      <Tabs defaultValue="my-profile" className="flex-1 flex flex-col">
        <TabsList className="w-full justify-start overflow-x-auto">
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.title}
            </TabsTrigger>
          ))}
        </TabsList>
        <div className="mt-6 flex-1 overflow-y-auto">
          {tabs.map((tab) => (
            <TabsContent key={tab.value} value={tab.value} className="mt-0 h-full">
              <tab.component />
            </TabsContent>
          ))}
        </div>
      </Tabs>
    </div>
  )
}
