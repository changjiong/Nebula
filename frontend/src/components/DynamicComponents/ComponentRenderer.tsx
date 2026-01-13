import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { ReactNode } from "react"

export interface DynamicComponentProps {
    component_type: string
    title?: string
    props: {
        data: any
        config?: any
    }
    actions?: Array<{
        type: "inject_to_system" | "export" | "navigate"
        label: string
        params?: any
    }>
}

interface ComponentRendererProps {
    payload: DynamicComponentProps
}

export function ComponentRenderer({ payload }: ComponentRendererProps): ReactNode {
    const { component_type, title, props } = payload

    // Get component from registry
    const Component = componentRegistry[component_type]

    if (!Component) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Unknown Component</CardTitle>
                    <CardDescription>Component type "{component_type}" not found</CardDescription>
                </CardHeader>
            </Card>
        )
    }

    return (
        <div className="space-y-2">
            {title && <h3 className="text-lg font-semibold">{title}</h3>}
            <Component {...props} />
            {payload.actions && payload.actions.length > 0 && (
                <div className="flex gap-2 mt-4">
                    {payload.actions.map((action, idx) => (
                        <button
                            key={idx}
                            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            onClick={() => handleAction(action)}
                        >
                            {action.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    )
}

function handleAction(action: DynamicComponentProps["actions"][0]) {
    console.log("Action triggered:", action)
    // TODO: Implement action handlers
}

// Component registry - maps component type to React component
const componentRegistry: Record<string, React.ComponentType<any>> = {}

// Register a component
export function registerComponent(type: string, component: React.ComponentType<any>) {
    componentRegistry[type] = component
}
