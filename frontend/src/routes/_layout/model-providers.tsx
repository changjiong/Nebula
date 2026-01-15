import { createFileRoute } from "@tanstack/react-router"

import ModelSettings from "@/components/ModelSettings"

export const Route = createFileRoute("/_layout/model-providers")({
    component: ModelProviders,
    head: () => ({
        meta: [
            {
                title: "Model Providers - ADTEC",
            },
        ],
    }),
})

function ModelProviders() {
    return (
        <div className="flex flex-col gap-6 h-full">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">Model Providers</h1>
                <p className="text-muted-foreground">
                    配置 AI 模型服务商的 API 地址和密钥
                </p>
            </div>
            <ModelSettings />
        </div>
    )
}
