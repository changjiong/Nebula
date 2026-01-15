/**
 * Provider List Item Component
 * 单个服务商项：图标、名称、开关
 */

import { useState } from "react"
import {
    Bot,
    Brain,
    Cloud,
    Cpu,
    Globe,
    Sparkles,
    Zap,
} from "lucide-react"
import { cn } from "@/lib/utils"
import {
    ModelProvider,
    useModelProviderStore,
} from "@/stores/modelProviderStore"

// Provider icon mapping
const PROVIDER_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
    openai: Brain,
    deepseek: Sparkles,
    gemini: Sparkles,
    qwen: Cloud,
    anthropic: Bot,
    moonshot: Globe,
    zhipu: Cpu,
    baidu: Cloud,
    default: Zap,
}

// Provider colors
const PROVIDER_COLORS: Record<string, string> = {
    openai: "bg-emerald-500",
    deepseek: "bg-blue-500",
    gemini: "bg-violet-500",
    qwen: "bg-orange-500",
    anthropic: "bg-amber-600",
    moonshot: "bg-slate-700",
    zhipu: "bg-indigo-500",
    baidu: "bg-red-500",
    default: "bg-gray-500",
}

interface ProviderListItemProps {
    provider: ModelProvider
    isSelected: boolean
    onSelect: () => void
}

export function ProviderListItem({
    provider,
    isSelected,
    onSelect,
}: ProviderListItemProps) {
    const { updateProvider } = useModelProviderStore()
    const [isUpdating, setIsUpdating] = useState(false)

    const IconComponent =
        PROVIDER_ICONS[provider.provider_type] || PROVIDER_ICONS.default
    const colorClass =
        PROVIDER_COLORS[provider.provider_type] || PROVIDER_COLORS.default

    const handleToggle = async (e: React.MouseEvent) => {
        e.stopPropagation()
        if (isUpdating) return

        setIsUpdating(true)
        await updateProvider(provider.id, { is_enabled: !provider.is_enabled })
        setIsUpdating(false)
    }

    return (
        <div
            onClick={onSelect}
            className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors",
                isSelected
                    ? "bg-accent"
                    : "hover:bg-accent/50",
            )}
        >
            {/* Icon */}
            <div
                className={cn(
                    "flex items-center justify-center size-8 rounded-lg text-white",
                    colorClass,
                )}
            >
                <IconComponent className="size-4" />
            </div>

            {/* Name */}
            <span className="flex-1 text-sm font-medium truncate">
                {provider.name}
            </span>

            {/* Toggle Switch */}
            <button
                onClick={handleToggle}
                disabled={isUpdating}
                className={cn(
                    "relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors",
                    provider.is_enabled ? "bg-primary" : "bg-muted",
                    isUpdating && "opacity-50 cursor-wait",
                )}
            >
                <span
                    className={cn(
                        "inline-block size-3.5 transform rounded-full bg-white transition-transform",
                        provider.is_enabled ? "translate-x-5" : "translate-x-1",
                    )}
                />
            </button>
        </div>
    )
}
