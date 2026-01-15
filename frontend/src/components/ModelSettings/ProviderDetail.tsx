/**
 * Provider Detail Component
 * 右侧配置面板：API密钥、API地址、模型列表
 */

import { useState } from "react"
import {
    CheckCircle2,
    ChevronDown,
    ChevronRight,
    Eye,
    EyeOff,
    Loader2,
    Settings2,
    Trash2,
    XCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useModelProviderStore } from "@/stores/modelProviderStore"
import useCustomToast from "@/hooks/useCustomToast"

export function ProviderDetail() {
    const { providers, selectedProviderId, updateProvider, testConnection, deleteProvider } =
        useModelProviderStore()
    const { showSuccessToast, showErrorToast } = useCustomToast()

    const [apiKey, setApiKey] = useState("")
    const [apiUrl, setApiUrl] = useState("")
    const [showApiKey, setShowApiKey] = useState(false)
    const [isTesting, setIsTesting] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [testResult, setTestResult] = useState<{
        success: boolean
        message: string
    } | null>(null)
    const [isModelsExpanded, setIsModelsExpanded] = useState(true)

    const provider = providers.find((p) => p.id === selectedProviderId)

    // Reset form when provider changes
    const prevProviderId = useState<string | null>(null)[0]
    if (provider && provider.id !== prevProviderId) {
        setApiKey("")
        setApiUrl(provider.api_url)
        setTestResult(null)
    }

    if (!provider) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <Settings2 className="size-12 mb-4 opacity-50" />
                <p>选择一个服务商进行配置</p>
            </div>
        )
    }

    const handleTest = async () => {
        setIsTesting(true)
        setTestResult(null)

        // First save the API key if changed
        if (apiKey) {
            await updateProvider(provider.id, { api_key: apiKey })
        }

        const result = await testConnection(provider.id)
        setTestResult(result)
        setIsTesting(false)

        if (result.success) {
            showSuccessToast(result.message)
            // Update models if available
            if (result.available_models.length > 0) {
                await updateProvider(provider.id, { models: result.available_models })
            }
        } else {
            showErrorToast(result.message)
        }
    }

    const handleSave = async () => {
        setIsSaving(true)
        const updates: Record<string, string> = {}
        if (apiKey) updates.api_key = apiKey
        if (apiUrl !== provider.api_url) updates.api_url = apiUrl

        const success = await updateProvider(provider.id, updates)
        setIsSaving(false)

        if (success) {
            showSuccessToast("配置已保存")
            setApiKey("") // Clear the input after save
        } else {
            showErrorToast("保存失败")
        }
    }

    const handleDelete = async () => {
        if (!confirm(`确定要删除 "${provider.name}" 吗？`)) return

        const success = await deleteProvider(provider.id)
        if (success) {
            showSuccessToast("已删除")
        } else {
            showErrorToast("删除失败")
        }
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h2 className="text-lg font-semibold">{provider.name}</h2>
                    <Settings2 className="size-4 text-muted-foreground" />
                </div>

                {/* Enable/Disable Toggle */}
                <button
                    onClick={() =>
                        updateProvider(provider.id, { is_enabled: !provider.is_enabled })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${provider.is_enabled ? "bg-primary" : "bg-muted"
                        }`}
                >
                    <span
                        className={`inline-block size-4 transform rounded-full bg-white transition-transform ${provider.is_enabled ? "translate-x-6" : "translate-x-1"
                            }`}
                    />
                </button>
            </div>

            {/* API Key */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">API 密钥</label>
                    <button className="text-xs text-muted-foreground hover:text-foreground">
                        多个密钥请用逗号分隔
                    </button>
                </div>
                <div className="flex gap-2">
                    <div className="relative flex-1">
                        <Input
                            type={showApiKey ? "text" : "password"}
                            placeholder={provider.api_key_set ? "••••••••••••••••" : "请输入 API Key"}
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="pr-10"
                        />
                        <button
                            type="button"
                            onClick={() => setShowApiKey(!showApiKey)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                            {showApiKey ? (
                                <EyeOff className="size-4" />
                            ) : (
                                <Eye className="size-4" />
                            )}
                        </button>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleTest}
                        disabled={isTesting || (!apiKey && !provider.api_key_set)}
                    >
                        {isTesting ? (
                            <Loader2 className="size-4 animate-spin" />
                        ) : (
                            "检测"
                        )}
                    </Button>
                </div>

                {/* Test Result */}
                {testResult && (
                    <div
                        className={`flex items-center gap-2 text-sm ${testResult.success ? "text-green-600" : "text-red-600"
                            }`}
                    >
                        {testResult.success ? (
                            <CheckCircle2 className="size-4" />
                        ) : (
                            <XCircle className="size-4" />
                        )}
                        <span>{testResult.message}</span>
                    </div>
                )}
            </div>

            {/* API URL */}
            <div className="space-y-2">
                <div className="flex items-center gap-2">
                    <label className="text-sm font-medium">API 地址</label>
                    <span className="text-xs text-muted-foreground">ⓘ</span>
                </div>
                <Input
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    placeholder="https://api.example.com/v1"
                />
                <p className="text-xs text-muted-foreground">
                    预览: {apiUrl}/chat/completions
                </p>
            </div>

            {/* Models Section */}
            <div className="space-y-3">
                <button
                    onClick={() => setIsModelsExpanded(!isModelsExpanded)}
                    className="flex items-center gap-2 text-sm font-medium"
                >
                    模型
                    <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                        {provider.models.length}
                    </span>
                    {isModelsExpanded ? (
                        <ChevronDown className="size-4" />
                    ) : (
                        <ChevronRight className="size-4" />
                    )}
                </button>

                {isModelsExpanded && (
                    <div className="space-y-2 pl-4">
                        {provider.models.length > 0 ? (
                            provider.models.map((model) => (
                                <div
                                    key={model}
                                    className="flex items-center gap-2 py-1.5 px-3 rounded-md bg-muted/50"
                                >
                                    <span className="text-sm">{model}</span>
                                </div>
                            ))
                        ) : (
                            <p className="text-sm text-muted-foreground">
                                暂无模型，请先配置 API 密钥并点击检测
                            </p>
                        )}
                    </div>
                )}

                <div className="flex gap-2 pl-4">
                    <Button
                        variant="default"
                        size="sm"
                        onClick={handleSave}
                        disabled={isSaving || (!apiKey && apiUrl === provider.api_url)}
                    >
                        {isSaving ? <Loader2 className="size-4 mr-1 animate-spin" /> : null}
                        保存配置
                    </Button>
                </div>
            </div>

            {/* Danger Zone */}
            <div className="pt-6 border-t">
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={handleDelete}
                >
                    <Trash2 className="size-4 mr-2" />
                    删除此服务商
                </Button>
            </div>
        </div>
    )
}
