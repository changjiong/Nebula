/**
 * Skill Store - State management for Skill CRUD and workflow editing
 */

import { create } from "zustand"

// Types matching backend models
export interface WorkflowNode {
  id: string
  tool: string
  depends_on: string[]
  params_mapping: Record<string, string>
  condition?: string
}

export interface Skill {
  id: string
  name: string
  display_name: string
  description: string
  workflow: {
    nodes: WorkflowNode[]
    output_mapping?: Record<string, string>
  }
  tool_ids: string[]
  input_schema: Record<string, unknown>
  output_schema: Record<string, unknown>
  version: string
  status: string
  category: string
  tags: string[]
  visibility: string
  allowed_departments: string[]
  allowed_roles: string[]
  call_count: number
  avg_latency_ms: number
  success_rate: number
  created_at: string
  updated_at: string
}

export interface SkillCreate {
  name: string
  display_name: string
  description: string
  workflow?: {
    nodes: WorkflowNode[]
    output_mapping?: Record<string, string>
  }
  tool_ids?: string[]
  input_schema?: Record<string, unknown>
  output_schema?: Record<string, unknown>
  version?: string
  status?: string
  category?: string
  tags?: string[]
}

export interface SkillUpdate {
  name?: string
  display_name?: string
  description?: string
  workflow?: {
    nodes: WorkflowNode[]
    output_mapping?: Record<string, string>
  }
  tool_ids?: string[]
  input_schema?: Record<string, unknown>
  output_schema?: Record<string, unknown>
  version?: string
  status?: string
  category?: string
  tags?: string[]
}

export interface SkillTestResult {
  success: boolean
  result?: Record<string, unknown>
  error?: string
  latency_ms: number
  tool_results?: Record<string, unknown>
}

// ReactFlow compatible types for editor
export interface EditorNode {
  id: string
  type?: string
  data: {
    label: string
    tool?: string
    params_mapping?: Record<string, string>
  }
  position: { x: number; y: number }
  style?: Record<string, string>
}

export interface EditorEdge {
  id: string
  source: string
  target: string
}

interface SkillsState {
  // Data
  skills: Skill[]
  selectedSkill: Skill | null
  isLoading: boolean
  error: string | null

  // Editor state
  editorNodes: EditorNode[]
  editorEdges: EditorEdge[]
  isEditing: boolean

  // Actions
  setSkills: (skills: Skill[]) => void
  setSelectedSkill: (skill: Skill | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setEditorNodes: (nodes: EditorNode[]) => void
  setEditorEdges: (edges: EditorEdge[]) => void
  setIsEditing: (editing: boolean) => void

  // API Actions
  fetchSkills: () => Promise<void>
  createSkill: (skill: SkillCreate) => Promise<Skill | null>
  updateSkill: (id: string, update: SkillUpdate) => Promise<Skill | null>
  deleteSkill: (id: string) => Promise<boolean>
  testSkill: (
    id: string,
    params: Record<string, unknown>,
  ) => Promise<SkillTestResult | null>

  // Editor Actions
  loadSkillIntoEditor: (skill: Skill) => void
  saveEditorToSkill: () => Skill | null
}

const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token")
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  }
}

export const useSkillStore = create<SkillsState>((set, get) => ({
  // Initial state
  skills: [],
  selectedSkill: null,
  isLoading: false,
  error: null,
  editorNodes: [],
  editorEdges: [],
  isEditing: false,

  // Simple setters
  setSkills: (skills) => set({ skills }),
  setSelectedSkill: (skill) => set({ selectedSkill: skill }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setEditorNodes: (nodes) => set({ editorNodes: nodes }),
  setEditorEdges: (edges) => set({ editorEdges: edges }),
  setIsEditing: (editing) => set({ isEditing: editing }),

  // API Actions
  fetchSkills: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch("/api/v1/skills/", {
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error("Failed to fetch skills")
      }

      const data = await response.json()
      set({ skills: data.data, isLoading: false })
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
    }
  },

  createSkill: async (skillData) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch("/api/v1/skills/", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(skillData),
      })

      if (!response.ok) {
        throw new Error("Failed to create skill")
      }

      const newSkill = await response.json()
      set((state) => ({
        skills: [newSkill, ...state.skills],
        isLoading: false,
      }))
      return newSkill
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
      return null
    }
  },

  updateSkill: async (id, update) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`/api/v1/skills/${id}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify(update),
      })

      if (!response.ok) {
        throw new Error("Failed to update skill")
      }

      const updatedSkill = await response.json()
      set((state) => ({
        skills: state.skills.map((s) => (s.id === id ? updatedSkill : s)),
        selectedSkill:
          state.selectedSkill?.id === id ? updatedSkill : state.selectedSkill,
        isLoading: false,
      }))
      return updatedSkill
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
      return null
    }
  },

  deleteSkill: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch(`/api/v1/skills/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      })

      if (!response.ok) {
        throw new Error("Failed to delete skill")
      }

      set((state) => ({
        skills: state.skills.filter((s) => s.id !== id),
        selectedSkill:
          state.selectedSkill?.id === id ? null : state.selectedSkill,
        isLoading: false,
      }))
      return true
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false })
      return false
    }
  },

  testSkill: async (id, params) => {
    try {
      const response = await fetch(`/api/v1/skills/${id}/test`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ params }),
      })

      if (!response.ok) {
        throw new Error("Failed to test skill")
      }

      return await response.json()
    } catch (error) {
      set({ error: (error as Error).message })
      return null
    }
  },

  // Editor Actions
  loadSkillIntoEditor: (skill) => {
    // Convert workflow to ReactFlow format
    const nodes: EditorNode[] = []
    const edges: EditorEdge[] = []

    // Add input node
    nodes.push({
      id: "input",
      type: "input",
      data: { label: "🎯 用户输入" },
      position: { x: 250, y: 0 },
    })

    // Add workflow nodes
    skill.workflow.nodes.forEach((wfNode, index) => {
      nodes.push({
        id: wfNode.id,
        data: {
          label: wfNode.tool,
          tool: wfNode.tool,
          params_mapping: wfNode.params_mapping,
        },
        position: {
          x: 100 + (index % 3) * 150,
          y: 100 + Math.floor(index / 3) * 100,
        },
      })

      // Create edges from dependencies
      if (wfNode.depends_on.length === 0) {
        edges.push({
          id: `e-input-${wfNode.id}`,
          source: "input",
          target: wfNode.id,
        })
      } else {
        wfNode.depends_on.forEach((dep) => {
          edges.push({
            id: `e-${dep}-${wfNode.id}`,
            source: dep,
            target: wfNode.id,
          })
        })
      }
    })

    // Add output node
    nodes.push({
      id: "output",
      type: "output",
      data: { label: "📤 输出" },
      position: { x: 250, y: 300 },
    })

    // Connect leaf nodes to output
    const leafNodes = nodes.filter(
      (n) =>
        n.id !== "input" &&
        n.id !== "output" &&
        !edges.some((e) => e.source === n.id),
    )
    leafNodes.forEach((leaf) => {
      edges.push({
        id: `e-${leaf.id}-output`,
        source: leaf.id,
        target: "output",
      })
    })

    set({
      editorNodes: nodes,
      editorEdges: edges,
      selectedSkill: skill,
      isEditing: true,
    })
  },

  saveEditorToSkill: () => {
    const { editorNodes, editorEdges, selectedSkill } = get()

    // Convert ReactFlow format back to workflow
    const workflowNodes: WorkflowNode[] = editorNodes
      .filter((n) => n.type !== "input" && n.type !== "output" && n.data.tool)
      .map((n) => {
        const incomingEdges = editorEdges.filter((e) => e.target === n.id)
        const depends_on = incomingEdges
          .map((e) => e.source)
          .filter((s) => s !== "input")

        return {
          id: n.id,
          tool: n.data.tool!,
          depends_on,
          params_mapping: n.data.params_mapping || {},
        }
      })

    if (!selectedSkill) return null

    return {
      ...selectedSkill,
      workflow: {
        nodes: workflowNodes,
      },
      tool_ids: workflowNodes.map((n) => n.tool),
    }
  },
}))
