/**
 * Add Provider Dialog
 * 添加新服务商对话框
 */

import { useState } from "react"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useModelProviderStore } from "@/stores/modelProviderStore"
import useCustomToast from "@/hooks/useCustomToast"

// 预置服务商列表（与后端同步）
const PRESET_PROVIDERS = [
    { type: "openai", name: "OpenAI", url: "https://api.openai.com/v1" },
    { type: "deepseek", name: "DeepSeek", url: "https://api.deepseek.com/v1" },
    { type: "gemini", name: "Google Gemini", url: "https://generativelanguage.googleapis.com/v1beta" },
    { type: "qwen", name: "阿里通义千问", url: "https://dashscope.aliyuncs.com/compatible-mode/v1" },
    { type: "anthropic", name: "Anthropic Claude", url: "https://api.anthropic.com/v1" },
    { type: "moonshot", name: "月之暗面 Kimi", url: "https://api.moonshot.cn/v1" },
    { type: "zhipu", name: "智谱 GLM", url: "https://open.bigmodel.cn/api/paas/v4" },
    { type: "baidu", name: "百度文心一言", url: "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop" },
    { type: "custom", name: "自定义", url: "" },
]

interface AddProviderDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function AddProviderDialog({ open, onOpenChange }: AddProviderDialogProps) {
    const { createProvider } = useModelProviderStore()
    const { showSuccessToast, showErrorToast } = useCustomToast()

    const [providerType, setProviderType] = useState("")
    const [name, setName] = useState("")
    const [apiUrl, setApiUrl] = useState("")
    const [apiKey, setApiKey] = useState("")
    const [isCreating, setIsCreating] = useState(false)

    const handleProviderTypeChange = (type: string) => {
        setProviderType(type)
        const preset = PRESET_PROVIDERS.find((p) => p.type === type)
        if (preset && type !== "custom") {
            setName(preset.name)
            setApiUrl(preset.url)
        } else {
            setName("")
            setApiUrl("")
        }
    }

    const handleCreate = async () => {
        if (!name || !providerType || !apiUrl) {
            showErrorToast("请填写所有必填字段")
            return
        }

        setIsCreating(true)
        const result = await createProvider({
            name,
            provider_type: providerType,
            api_url: apiUrl,
            api_key: apiKey,
            is_enabled: !!apiKey, // Auto-enable if API key is provided
            icon: providerType,
            models: [],
        })
        setIsCreating(false)

        if (result) {
            showSuccessToast("服务商已添加")
            onOpenChange(false)
            // Reset form
            setProviderType("")
            setName("")
            setApiUrl("")
            setApiKey("")
        } else {
            showErrorToast("添加失败")
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>添加模型服务商</DialogTitle>
                    <DialogDescription>
                        选择预置服务商或添加自定义服务商
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {/* Provider Type */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">服务商类型</label>
                        <Select value={providerType} onValueChange={handleProviderTypeChange}>
                            <SelectTrigger>
                                <SelectValue placeholder="选择服务商类型" />
                            </SelectTrigger>
                            <SelectContent>
                                {PRESET_PROVIDERS.map((p) => (
                                    <SelectItem key={p.type} value={p.type}>
                                        {p.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Name */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">显示名称</label>
                        <Input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="如：我的 OpenAI"
                        />
                    </div>

                    {/* API URL */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">API 地址</label>
                        <Input
                            value={apiUrl}
                            onChange={(e) => setApiUrl(e.target.value)}
                            placeholder="https://api.example.com/v1"
                        />
                    </div>

                    {/* API Key (optional) */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">
                            API 密钥 <span className="text-muted-foreground">(可选)</span>
                        </label>
                        <Input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="sk-..."
                        />
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        取消
                    </Button>
                    <Button onClick={handleCreate} disabled={isCreating || !name || !providerType || !apiUrl}>
                        {isCreating && <Loader2 className="size-4 mr-2 animate-spin" />}
                        添加
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
