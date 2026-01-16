import { createFileRoute } from "@tanstack/react-router"
import {
  addEdge,
  Background,
  type Connection,
  Controls,
  type Edge,
  MarkerType,
  MiniMap,
  type Node,
  Panel,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react"
import { useCallback, useState } from "react"
import "@xyflow/react/dist/style.css"
import { ArrowLeft, Play, Plus, Save, Settings, Trash2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"

export const Route = createFileRoute("/_layout/skills")({
  component: SkillsEditorPage,
})

// Mock tools for the palette
const mockTools = [
  { id: "enterprise_query", name: "企业信息查询", type: "data_api" },
  { id: "kechuang_score", name: "科创能力评分", type: "ml_model" },
  { id: "relation_graph", name: "关系图谱查询", type: "data_api" },
  { id: "credit_score", name: "征信评分", type: "ml_model" },
  { id: "risk_analysis", name: "风险分析", type: "ml_model" },
]

// Initial nodes for demo
const initialNodes: Node[] = [
  {
    id: "input",
    type: "input",
    data: { label: "🎯 用户输入" },
    position: { x: 250, y: 0 },
    style: {
      background: "#e0f2fe",
      border: "2px solid #0284c7",
      borderRadius: "8px",
      padding: "10px",
    },
  },
  {
    id: "step1",
    data: { label: "📊 企业信息查询", tool: "enterprise_query" },
    position: { x: 250, y: 100 },
    style: {
      background: "#f0fdf4",
      border: "2px solid #22c55e",
      borderRadius: "8px",
      padding: "10px",
    },
  },
  {
    id: "step2",
    data: { label: "🤖 科创能力评分", tool: "kechuang_score" },
    position: { x: 100, y: 200 },
    style: {
      background: "#fef3c7",
      border: "2px solid #f59e0b",
      borderRadius: "8px",
      padding: "10px",
    },
  },
  {
    id: "step3",
    data: { label: "🔍 关系图谱查询", tool: "relation_graph" },
    position: { x: 400, y: 200 },
    style: {
      background: "#fef3c7",
      border: "2px solid #f59e0b",
      borderRadius: "8px",
      padding: "10px",
    },
  },
  {
    id: "output",
    type: "output",
    data: { label: "📤 综合结果" },
    position: { x: 250, y: 320 },
    style: {
      background: "#fce7f3",
      border: "2px solid #ec4899",
      borderRadius: "8px",
      padding: "10px",
    },
  },
]

const initialEdges: Edge[] = [
  {
    id: "e-input-step1",
    source: "input",
    target: "step1",
    markerEnd: { type: MarkerType.ArrowClosed },
    animated: true,
  },
  {
    id: "e-step1-step2",
    source: "step1",
    target: "step2",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-step1-step3",
    source: "step1",
    target: "step3",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-step2-output",
    source: "step2",
    target: "output",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e-step3-output",
    source: "step3",
    target: "output",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
]

function SkillsEditorPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [skillName, setSkillName] = useState("企业综合评估")
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)

  const onConnect = useCallback(
    (params: Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            markerEnd: { type: MarkerType.ArrowClosed },
          },
          eds,
        ),
      ),
    [setEdges],
  )

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  const addToolNode = (tool: (typeof mockTools)[0]) => {
    const newNode: Node = {
      id: `tool-${Date.now()}`,
      data: {
        label: `${tool.type === "ml_model" ? "🤖" : "📊"} ${tool.name}`,
        tool: tool.id,
      },
      position: { x: Math.random() * 300 + 100, y: Math.random() * 200 + 100 },
      style: {
        background: tool.type === "ml_model" ? "#fef3c7" : "#f0fdf4",
        border: `2px solid ${tool.type === "ml_model" ? "#f59e0b" : "#22c55e"}`,
        borderRadius: "8px",
        padding: "10px",
      },
    }
    setNodes((nds) => [...nds, newNode])
  }

  const deleteSelectedNode = () => {
    if (!selectedNode) return
    if (selectedNode.type === "input" || selectedNode.type === "output") return

    setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id))
    setEdges((eds) =>
      eds.filter(
        (e) => e.source !== selectedNode.id && e.target !== selectedNode.id,
      ),
    )
    setSelectedNode(null)
  }

  const handleSave = () => {
    const workflow = {
      name: skillName,
      nodes: nodes.map((n) => ({
        id: n.id,
        tool: n.data.tool || null,
        type: n.type || "default",
        position: n.position,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
      })),
    }
    console.log("Saving workflow:", workflow)
    // TODO: Call API to save
    alert("工作流已保存！（模拟）")
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <a href="/tools">
              <ArrowLeft className="h-4 w-4" />
            </a>
          </Button>
          <div>
            <Input
              value={skillName}
              onChange={(e) => setSkillName(e.target.value)}
              className="text-xl font-bold border-none p-0 h-auto focus-visible:ring-0"
            />
            <p className="text-sm text-muted-foreground">
              拖拽工具节点创建工作流
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" />
            保存
          </Button>
          <Button>
            <Play className="mr-2 h-4 w-4" />
            测试运行
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Canvas */}
        <div className="flex-1" style={{ height: "calc(100vh - 140px)" }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            snapToGrid
          >
            <Background />
            <Controls />
            <MiniMap />

            {/* Tool Palette Panel */}
            <Panel position="top-left">
              <Card className="w-64">
                <CardHeader className="py-3">
                  <CardTitle className="text-sm">工具面板</CardTitle>
                  <CardDescription className="text-xs">
                    点击添加到画布
                  </CardDescription>
                </CardHeader>
                <CardContent className="py-2">
                  <div className="space-y-2">
                    {mockTools.map((tool) => (
                      <Button
                        key={tool.id}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addToolNode(tool)}
                      >
                        <Plus className="mr-2 h-3 w-3" />
                        {tool.name}
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {tool.type === "ml_model" ? "ML" : "API"}
                        </Badge>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Panel>

            {/* Selected Node Panel */}
            {selectedNode &&
              selectedNode.type !== "input" &&
              selectedNode.type !== "output" && (
                <Panel position="top-right">
                  <Card className="w-64">
                    <CardHeader className="py-3">
                      <CardTitle className="text-sm flex items-center justify-between">
                        节点配置
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-destructive"
                          onClick={deleteSelectedNode}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="py-2 space-y-3">
                      <div>
                        <label
                          htmlFor="node-id"
                          className="text-xs text-muted-foreground"
                        >
                          节点 ID
                        </label>
                        <p id="node-id" className="font-mono text-sm">
                          {selectedNode.id}
                        </p>
                      </div>
                      <Separator />
                      <div>
                        <label
                          htmlFor="node-tool"
                          className="text-xs text-muted-foreground"
                        >
                          工具
                        </label>
                        <p id="node-tool" className="text-sm">
                          {(selectedNode.data.tool as string) || "无"}
                        </p>
                      </div>
                      <Button variant="outline" size="sm" className="w-full">
                        <Settings className="mr-2 h-3 w-3" />
                        配置参数映射
                      </Button>
                    </CardContent>
                  </Card>
                </Panel>
              )}
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}
