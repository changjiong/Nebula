/**
 * Provider List Component
 * 左侧服务商列表，带搜索框和添加按钮
 */

import { Plus, Search } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useModelProviderStore } from "@/stores/modelProviderStore"
import { AddProviderDialog } from "./AddProviderDialog"
import { ProviderListItem } from "./ProviderListItem"

export function ProviderList() {
  const { providers, selectedProviderId, selectProvider } =
    useModelProviderStore()
  const [searchQuery, setSearchQuery] = useState("")
  const [showAddDialog, setShowAddDialog] = useState(false)

  const filteredProviders = providers.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="搜索模型平台..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-9 text-sm"
            autoComplete="off"
          />
        </div>
      </div>

      {/* Provider List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredProviders.map((provider) => (
            <ProviderListItem
              key={provider.id}
              provider={provider}
              isSelected={provider.id === selectedProviderId}
              onSelect={() => selectProvider(provider.id)}
            />
          ))}
        </div>
      </ScrollArea>

      {/* Footer: Add Button */}
      <div className="p-3 border-t">
        <Button
          variant="outline"
          size="sm"
          className="w-full justify-start gap-2"
          onClick={() => setShowAddDialog(true)}
        >
          <Plus className="size-4" />
          添加
        </Button>
      </div>

      {/* Add Provider Dialog */}
      <AddProviderDialog open={showAddDialog} onOpenChange={setShowAddDialog} />
    </div>
  )
}
