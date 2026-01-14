/**
 * RelationGraph - Enterprise Relationship Visualization
 *
 * Displays corporate relationships in a tree/graph structure.
 * Used for showing parent-child relationships, subsidiaries, and affiliate companies.
 */

import { Building2, ChevronDown, ChevronRight } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface RelationNode {
  id: string
  name: string
  type: "parent" | "self" | "child" | "sibling" | "affiliate"
  credit_code?: string
  share_ratio?: string
  children?: RelationNode[]
  [key: string]: any
}

interface RelationGraphProps {
  data: {
    root: RelationNode
    centerNodeId?: string
  }
  config?: {
    expandLevel?: number
    showShareRatio?: boolean
    maxDepth?: number
  }
}

function RelationNodeItem({
  node,
  level = 0,
  expandLevel = 2,
  showShareRatio = true,
}: {
  node: RelationNode
  level?: number
  expandLevel?: number
  showShareRatio?: boolean
}) {
  const [expanded, setExpanded] = useState(level < expandLevel)
  const hasChildren = node.children && node.children.length > 0

  const typeStyles = {
    parent: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    self: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    child:
      "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    sibling:
      "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
    affiliate: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  }

  const typeLabels = {
    parent: "母公司",
    self: "当前企业",
    child: "子公司",
    sibling: "关联企业",
    affiliate: "参股企业",
  }

  return (
    <div className="relative">
      <div
        className={`flex items-center gap-2 p-2 rounded-lg hover:bg-muted/50 cursor-pointer ${
          node.type === "self" ? "bg-muted/30 border border-primary/20" : ""
        }`}
        onClick={() => hasChildren && setExpanded(!expanded)}
        style={{ marginLeft: `${level * 24}px` }}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          )
        ) : (
          <div className="w-4" />
        )}
        <Building2 className="h-4 w-4 text-muted-foreground" />
        <span
          className={`text-sm font-medium ${node.type === "self" ? "text-primary" : ""}`}
        >
          {node.name}
        </span>
        <Badge variant="outline" className={typeStyles[node.type]}>
          {typeLabels[node.type]}
        </Badge>
        {showShareRatio && node.share_ratio && (
          <span className="text-xs text-muted-foreground ml-2">
            持股 {node.share_ratio}
          </span>
        )}
      </div>
      {expanded && hasChildren && (
        <div className="mt-1">
          {node.children!.map((child) => (
            <RelationNodeItem
              key={child.id}
              node={child}
              level={level + 1}
              expandLevel={expandLevel}
              showShareRatio={showShareRatio}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function RelationGraph({ data, config }: RelationGraphProps) {
  const expandLevel = config?.expandLevel ?? 2
  const showShareRatio = config?.showShareRatio ?? true

  if (!data?.root) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>关联企业图谱</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">暂无关联企业数据</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5" />
          关联企业图谱
        </CardTitle>
      </CardHeader>
      <CardContent>
        <RelationNodeItem
          node={data.root}
          expandLevel={expandLevel}
          showShareRatio={showShareRatio}
        />
      </CardContent>
    </Card>
  )
}
