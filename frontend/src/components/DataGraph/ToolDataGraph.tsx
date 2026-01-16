import {
  addEdge,
  Background,
  type Connection,
  Controls,
  MarkerType,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react"
import { useCallback, useEffect } from "react"
import "@xyflow/react/dist/style.css"

import { TableNode } from "./TableNode"
import { ToolNode } from "./ToolNode"

const nodeTypes = {
  tool: ToolNode,
  table: TableNode,
}

const initialNodes = [
  {
    id: "tool-1",
    type: "tool",
    position: { x: 250, y: 150 },
    data: {
      label: "kechuang_score",
      description: "Scores enterprise innovation",
    },
  },
  {
    id: "table-input",
    type: "table",
    position: { x: 0, y: 50 },
    data: {
      label: "enterprise_info",
      fields: [
        { name: "credit_code", type: "string" },
        { name: "company_name", type: "string" },
      ],
    },
  },
  {
    id: "table-output",
    type: "table",
    position: { x: 550, y: 50 },
    data: {
      label: "kechuang_scores",
      fields: [
        { name: "total_score", type: "number" },
        { name: "risk_level", type: "string" },
      ],
    },
  },
]

const initialEdges = [
  {
    id: "e1-2",
    source: "table-input",
    target: "tool-1",
    animated: true,
    label: "credit_code -> input",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
  {
    id: "e2-3",
    source: "tool-1",
    target: "table-output",
    animated: true,
    label: "output -> total_score",
    markerEnd: { type: MarkerType.ArrowClosed },
  },
]

export function ToolDataGraph({ toolId }: { toolId: string }) {
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  // TODO: Fetch real data based on toolId and update nodes/edges
  useEffect(() => {
    console.log("Fetching graph for tool:", toolId)
  }, [toolId])

  return (
    <div className="h-[500px] w-full border rounded-md bg-slate-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
