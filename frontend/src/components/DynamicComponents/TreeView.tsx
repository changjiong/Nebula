/**
 * TreeView - Hierarchical Data Visualization
 *
 * Displays hierarchical data (like equity penetration) in an expandable tree structure.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronRight, GitBranch } from "lucide-react"
import { useState } from "react"

interface TreeNode {
    id: string
    label: string
    value?: string | number
    icon?: string
    children?: TreeNode[]
    metadata?: Record<string, any>
}

interface TreeViewProps {
    data: {
        root: TreeNode
        title?: string
    }
    config?: {
        defaultExpanded?: boolean
        maxDepth?: number
        showValues?: boolean
    }
}

function TreeNodeItem({
    node,
    level = 0,
    defaultExpanded = true,
    showValues = true,
}: {
    node: TreeNode
    level?: number
    defaultExpanded?: boolean
    showValues?: boolean
}) {
    const [expanded, setExpanded] = useState(defaultExpanded && level < 2)
    const hasChildren = node.children && node.children.length > 0

    return (
        <div className="relative">
            {/* Connection lines */}
            {level > 0 && (
                <div
                    className="absolute left-0 top-0 bottom-0 border-l-2 border-dashed border-muted-foreground/30"
                    style={{ marginLeft: `${(level - 1) * 24 + 8}px` }}
                />
            )}

            <div
                className={`flex items-center gap-2 py-1.5 px-2 rounded hover:bg-muted/50 cursor-pointer transition-colors`}
                onClick={() => hasChildren && setExpanded(!expanded)}
                style={{ marginLeft: `${level * 24}px` }}
            >
                {hasChildren ? (
                    <button className="p-0.5 hover:bg-muted rounded">
                        {expanded ? (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                            <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                    </button>
                ) : (
                    <div className="w-5" />
                )}

                <span className="text-sm">{node.label}</span>

                {showValues && node.value && (
                    <span className="text-xs text-muted-foreground ml-auto">
                        {typeof node.value === "number" ? `${node.value}%` : node.value}
                    </span>
                )}
            </div>

            {expanded && hasChildren && (
                <div>
                    {node.children!.map((child) => (
                        <TreeNodeItem
                            key={child.id}
                            node={child}
                            level={level + 1}
                            defaultExpanded={defaultExpanded}
                            showValues={showValues}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export function TreeView({ data, config }: TreeViewProps) {
    const defaultExpanded = config?.defaultExpanded ?? true
    const showValues = config?.showValues ?? true

    if (!data?.root) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>{data?.title || "层级结构"}</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground text-sm">暂无数据</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <GitBranch className="h-5 w-5" />
                    {data.title || "层级结构"}
                </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
                <TreeNodeItem
                    node={data.root}
                    defaultExpanded={defaultExpanded}
                    showValues={showValues}
                />
            </CardContent>
        </Card>
    )
}
