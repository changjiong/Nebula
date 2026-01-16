import {
  addEdge,
  Background,
  type Connection,
  Controls,
  Edge,
  MarkerType,
  Node,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react"
import { useCallback, useEffect } from "react"
import "@xyflow/react/dist/style.css"
import { useQuery } from "@tanstack/react-query"
import axios from "axios"

import { TableNode } from "./TableNode"
import { ToolNode } from "./ToolNode"

const nodeTypes = {
  tool: ToolNode,
  table: TableNode,
}

interface ToolDataGraphProps {
  toolId: string
}

export function ToolDataGraph({ toolId }: ToolDataGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  const { data: graphData, isLoading } = useQuery({
    queryKey: ["tool_data_graph", toolId],
    queryFn: async () => {
      const res = await axios.get(`/api/v1/tools/${toolId}/data-graph`)
      return res.data
    },
    enabled: !!toolId,
  })

  useEffect(() => {
    if (!graphData) return

    const { tool, mappings, tables } = graphData

    const newNodes: Node[] = []
    const newEdges: Edge[] = []

    // 1. Central Tool Node
    newNodes.push({
      id: `tool-${tool.id}`,
      type: "tool",
      position: { x: 400, y: 250 },
      data: {
        label: tool.display_name || tool.name,
        description: tool.description,
        toolType: tool.tool_type, // Pass extra info if needed
      },
    })

    // 2. Table Nodes (Position them left for inputs, right for outputs based on mappings)
    // We need to determine if a table is generally an input source or output target
    // A table might be both, but let's heuristically place them.

    // Group mappings by table
    const tableMappings: Record<string, { inputs: any[], outputs: any[] }> = {}
    tables.forEach((t: any) => {
      tableMappings[t.id] = { inputs: [], outputs: [] }
    })

    mappings.forEach((m: any) => {
      if (tableMappings[m.table_id]) {
        if (m.param_direction === "input") {
          tableMappings[m.table_id].inputs.push(m)
        } else {
          tableMappings[m.table_id].outputs.push(m)
        }
      }
    })

    // Create Table Nodes and Edges
    let inputY = 50
    let outputY = 50

    tables.forEach((table: any) => {
      const mapping = tableMappings[table.id]
      if (!mapping) return

      const isInput = mapping.inputs.length > 0
      const isOutput = mapping.outputs.length > 0

      // Determine position
      let x = 0
      let y = 0

      if (isInput && !isOutput) {
        x = 50
        y = inputY
        inputY += 200
      } else if (!isInput && isOutput) {
        x = 750
        y = outputY
        outputY += 200
      } else {
        // Mixed, put somewhere in between or stacked
        x = 400
        y = Math.max(inputY, outputY) + 300
      }

      newNodes.push({
        id: `table-${table.id}`,
        type: "table",
        position: { x, y },
        data: {
          label: table.display_name || table.name,
          fields: [], // We might want to list mapped fields here?
          // For now, TableNode expects 'fields' array, let's pass all fields or just mapped ones?
          // Ideally passing all fields is better context, but we don't have them in 'tables' response 
          // unless 'tables' includes fields.
          // The backend: `tables = session.exec(select(StandardTable).where(StandardTable.id.in_(table_ids))).all()`
          // This usually lazy loads fields. So fields might be empty or valid if serialization handles it.
          // Let's rely on what we have. API response usually just dumps model. 
          // If fields are missing, we might need to fetch them.
          // But `StandardTable` includes `fields` relationship. By default SQLModel/Pydantic might not include relationship unless configured.
          // Let's assume for now.
        }
      })

      // Create Edges
      mapping.inputs.forEach((m: any) => {
        newEdges.push({
          id: `edge-${m.id}`,
          source: `table-${table.id}`,
          target: `tool-${tool.id}`,
          label: `${m.param_path}`, // Display parameter name on edge
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed },
        })
      })

      mapping.outputs.forEach((m: any) => {
        newEdges.push({
          id: `edge-${m.id}`,
          source: `tool-${tool.id}`,
          target: `table-${table.id}`,
          label: `${m.param_path}`,
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed },
        })
      })
    })

    setNodes(newNodes)
    setEdges(newEdges)

  }, [graphData, toolId, setNodes, setEdges])

  if (isLoading) return <div>Loading graph...</div>

  return (
    <div className="h-[600px] w-full border rounded-md bg-slate-50">
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
