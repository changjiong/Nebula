/**
 * Model Settings - Main Component
 * 模型服务商管理页面，参考 CherryStudio UI
 */

import { Loader2 } from "lucide-react"
import { useEffect } from "react"
import { useModelProviderStore } from "@/stores/modelProviderStore"
import { ProviderDetail } from "./ProviderDetail"
import { ProviderList } from "./ProviderList"

export default function ModelSettings() {
  const { providers, isLoading, fetchProviders, initPresets } =
    useModelProviderStore()

  useEffect(() => {
    // Fetch providers on mount
    fetchProviders().then(() => {
      // If no providers exist, initialize presets
      const { providers: currentProviders } = useModelProviderStore.getState()
      if (currentProviders.length === 0) {
        initPresets()
      }
    })
  }, [fetchProviders, initPresets])

  if (isLoading && providers.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-200px)] min-h-[500px] gap-0 rounded-lg border bg-background overflow-hidden">
      {/* Left: Provider List */}
      <div className="w-64 border-r flex-shrink-0">
        <ProviderList />
      </div>

      {/* Right: Provider Detail */}
      <div className="flex-1 overflow-auto">
        <ProviderDetail />
      </div>
    </div>
  )
}

export { ModelSettings }
