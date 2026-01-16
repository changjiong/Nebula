import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SkillsEditor } from "./Skills/SkillsEditor"
import { ToolsList } from "./Tools/ToolsList"
import { UsersList } from "./Users/UsersList"

export function AdminSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold tracking-tight">Administration</h2>
        <p className="text-muted-foreground">
          System-wide configurations and management
        </p>
      </div>

      <Tabs defaultValue="users" className="w-full">
        <TabsList>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
        </TabsList>
        <TabsContent value="users" className="mt-6">
          <UsersList />
        </TabsContent>
        <TabsContent value="tools" className="mt-6">
          <ToolsList />
        </TabsContent>
        <TabsContent value="skills" className="mt-6">
          <SkillsEditor />
        </TabsContent>
      </Tabs>
    </div>
  )
}
