/**
 * Provider Detail Component
 * 右侧配置面板：API密钥、API地址、模型列表
 * Enhanced with CherryStudio-inspired features:
 * 1. API key help link
 * 2. API format toggle (OpenAI/Anthropic)
 * 3. Model search
 * 4. Manage/Add buttons
 * 5. Documentation links
 */

import { useEffect, useState, useMemo } from "react"
import {
    CheckCircle2,
    ChevronDown,
    ChevronRight,
    Eye,
    EyeOff,
    ExternalLink,
    Loader2,
    Plus,
    Search,
    Settings2,
    Trash2,
    XCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import { useModelProviderStore } from "@/stores/modelProviderStore"
import useCustomToast from "@/hooks/useCustomToast"
import { getProviderConfig, supportsAnthropicFormat } from "@/config/providerConfig"
import { ManageModelsDialog, type ModelItem } from "./ManageModelsDialog"
import { AddCustomModelDialog, type CustomModelData } from "./AddCustomModelDialog"

type ApiMode = "openai" | "anthropic"

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

    // Feature 2: API format mode
    const [apiMode, setApiMode] = useState<ApiMode>("openai")

    // Feature 3: Model search
    const [showSearch, setShowSearch] = useState(false)
    const [searchQuery, setSearchQuery] = useState("")

    // Feature 4: Dialogs
    const [showManageDialog, setShowManageDialog] = useState(false)
    const [showAddDialog, setShowAddDialog] = useState(false)
    const [isRefreshingModels, setIsRefreshingModels] = useState(false)
    const [availableModels, setAvailableModels] = useState<string[]>([])  // Models from API for selection

    const provider = providers.find((p) => p.id === selectedProviderId)
    const providerConfig = provider ? getProviderConfig(provider.provider_type) : undefined
    const canToggleApiFormat = provider ? supportsAnthropicFormat(provider.provider_type) : false

    // Reset form when provider changes
    useEffect(() => {
        if (provider) {
            setApiKey("")
            setApiUrl(provider.api_url)
            setApiMode("openai")
            setTestResult(null)
            setShowSearch(false)
            setSearchQuery("")
        }
    }, [selectedProviderId, provider?.api_url])

    // Convert models to ModelItem: combine selected (provider.models) + available (from API)
    // Selected models are enabled, available models are shown but disabled until user selects
    const modelItems: ModelItem[] = useMemo(() => {
        if (!provider) return []
        const selectedSet = new Set(provider.models)

        // Start with selected models (is_enabled = true)
        const items: ModelItem[] = provider.models.map((modelId) => ({
            id: modelId,
            name: modelId,
            is_enabled: true,
        }))

        // Add available models that are not selected (is_enabled = false)
        for (const modelId of availableModels) {
            if (!selectedSet.has(modelId)) {
                items.push({
                    id: modelId,
                    name: modelId,
                    is_enabled: false,
                })
            }
        }

        return items
    }, [provider?.models, availableModels])

    // Filtered models for display
    const filteredModels = useMemo(() => {
        if (!searchQuery) return provider?.models || []
        return (provider?.models || []).filter((model) =>
            model.toLowerCase().includes(searchQuery.toLowerCase())
        )
    }, [provider?.models, searchQuery])

    if (!provider) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <Settings2 className="size-12 mb-4 opacity-50" />
                <p>选择一个服务商进行配置</p>
            </div>
        )
    }

    const handleApiModeChange = (mode: ApiMode) => {
        setApiMode(mode)
        if (mode === "anthropic" && providerConfig?.anthropicApiUrl) {
            setApiUrl(providerConfig.anthropicApiUrl)
        } else if (mode === "openai" && providerConfig?.apiUrl) {
            setApiUrl(providerConfig.apiUrl)
        }
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
            showSuccessToast(`${result.message}，发现 ${result.available_models.length} 个模型`)
            // Store available models for manual selection (don't auto-add to provider)
            if (result.available_models.length > 0) {
                setAvailableModels(result.available_models)
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

    const handleToggleModel = (modelId: string) => {
        // Toggle model in list - for now just remove/add
        const currentModels = provider.models
        const isEnabled = currentModels.includes(modelId)

        const newModels = isEnabled
            ? currentModels.filter((m) => m !== modelId)
            : [...currentModels, modelId]

        updateProvider(provider.id, { models: newModels })
    }

    const handleRefreshModels = async () => {
        setIsRefreshingModels(true)
        const result = await testConnection(provider.id)
        setIsRefreshingModels(false)

        if (result.success && result.available_models.length > 0) {
            // Store available models for manual selection (don't auto-add)
            setAvailableModels(result.available_models)
            showSuccessToast(`发现 ${result.available_models.length} 个模型`)
        }
    }

    const handleSelectAll = () => {
        // Add all available models to provider's selected list
        const allModels = [...new Set([...provider.models, ...availableModels])]
        updateProvider(provider.id, { models: allModels })
    }

    const handleClearAll = () => {
        // Clear all selected models
        updateProvider(provider.id, { models: [] })
    }

    const handleAddCustomModel = async (model: CustomModelData) => {
        // Add custom model to the list
        if (!provider.models.includes(model.id)) {
            await updateProvider(provider.id, {
                models: [...provider.models, model.id]
            })
            showSuccessToast(`已添加模型: ${model.name}`)
        } else {
            showErrorToast("模型已存在")
        }
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h2 className="text-lg font-semibold">{provider.name}</h2>
                    {/* Feature 5: Official website link */}
                    {providerConfig?.officialUrl && (
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <a
                                        href={providerConfig.officialUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-muted-foreground hover:text-foreground"
                                    >
                                        <ExternalLink className="size-4" />
                                    </a>
                                </TooltipTrigger>
                                <TooltipContent>访问官网</TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    )}
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
                    <span className="text-xs text-muted-foreground">
                        多个密钥请用逗号分隔
                    </span>
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

                {/* Feature 1: API Key Help Link */}
                {providerConfig?.apiKeyUrl && (
                    <a
                        href={providerConfig.apiKeyUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline inline-flex items-center gap-1"
                    >
                        点击这里获取密钥
                    </a>
                )}

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
                    {/* Feature 2: API Format Toggle */}
                    {canToggleApiFormat ? (
                        <Select value={apiMode} onValueChange={(v) => handleApiModeChange(v as ApiMode)}>
                            <SelectTrigger className="w-auto h-auto p-0 border-0 shadow-none font-medium text-sm">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="openai">API 地址</SelectItem>
                                <SelectItem value="anthropic">Anthropic API 地址</SelectItem>
                            </SelectContent>
                        </Select>
                    ) : (
                        <label className="text-sm font-medium">API 地址</label>
                    )}
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger>
                                <span className="text-xs text-muted-foreground cursor-help">ⓘ</span>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>API 请求的基础 URL</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
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
                <div className="flex items-center gap-2">
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

                    {/* Feature 3: Model Search Toggle */}
                    <button
                        onClick={() => setShowSearch(!showSearch)}
                        className={`p-1 rounded hover:bg-muted ${showSearch ? "bg-muted" : ""}`}
                    >
                        <Search className="size-4 text-muted-foreground" />
                    </button>
                </div>

                {/* Feature 3: Search Input */}
                {showSearch && (
                    <Input
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="搜索模型..."
                        className="h-8"
                        autoComplete="off"
                    />
                )}

                {isModelsExpanded && (
                    <div className="space-y-2 pl-4">
                        {filteredModels.length > 0 ? (
                            filteredModels.slice(0, 10).map((model) => (
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
                        {filteredModels.length > 10 && (
                            <p className="text-xs text-muted-foreground">
                                还有 {filteredModels.length - 10} 个模型...
                            </p>
                        )}
                    </div>
                )}

                {/* Feature 5: Documentation Links */}
                {(providerConfig?.docsUrl || providerConfig?.modelsUrl) && (
                    <p className="text-xs text-muted-foreground pl-4">
                        查看{" "}
                        {providerConfig.docsUrl && (
                            <a
                                href={providerConfig.docsUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline"
                            >
                                {provider.name} 文档
                            </a>
                        )}
                        {providerConfig.docsUrl && providerConfig.modelsUrl && " 和 "}
                        {providerConfig.modelsUrl && (
                            <a
                                href={providerConfig.modelsUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline"
                            >
                                模型
                            </a>
                        )}
                        {" "}获取更多详情
                    </p>
                )}

                {/* Feature 4: Manage and Add Buttons */}
                <div className="flex gap-2 pl-4">
                    <Button
                        variant="default"
                        size="sm"
                        onClick={() => setShowManageDialog(true)}
                    >
                        <Settings2 className="size-4 mr-1" />
                        管理
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAddDialog(true)}
                    >
                        <Plus className="size-4 mr-1" />
                        添加
                    </Button>
                </div>
            </div>

            {/* Save Button */}
            <div className="pt-2">
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

            {/* Feature 4: Manage Models Dialog */}
            <ManageModelsDialog
                open={showManageDialog}
                onOpenChange={setShowManageDialog}
                providerName={provider.name}
                models={modelItems}
                onToggleModel={handleToggleModel}
                onRefresh={handleRefreshModels}
                isRefreshing={isRefreshingModels}
                onSelectAll={handleSelectAll}
                onClearAll={handleClearAll}
            />

            {/* Feature 4: Add Custom Model Dialog */}
            <AddCustomModelDialog
                open={showAddDialog}
                onOpenChange={setShowAddDialog}
                onAdd={handleAddCustomModel}
            />
        </div>
    )
}
