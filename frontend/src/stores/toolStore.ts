/**
 * Tool Store - State management for Tool CRUD operations
 */

import { create } from "zustand"

// Types matching backend models
export interface Tool {
    id: string
    name: string
    display_name: string
    description: string
    tool_type: string
    service_config: Record<string, unknown>
    input_schema: Record<string, unknown>
    output_schema: Record<string, unknown>
    examples: Array<Record<string, unknown>>
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

export interface ToolCreate {
    name: string
    display_name: string
    description: string
    tool_type?: string
    service_config?: Record<string, unknown>
    input_schema?: Record<string, unknown>
    output_schema?: Record<string, unknown>
    examples?: Array<Record<string, unknown>>
    version?: string
    status?: string
    category?: string
    tags?: string[]
    visibility?: string
    allowed_departments?: string[]
    allowed_roles?: string[]
}

export interface ToolUpdate {
    name?: string
    display_name?: string
    description?: string
    tool_type?: string
    service_config?: Record<string, unknown>
    input_schema?: Record<string, unknown>
    output_schema?: Record<string, unknown>
    examples?: Array<Record<string, unknown>>
    version?: string
    status?: string
    category?: string
    tags?: string[]
    visibility?: string
    allowed_departments?: string[]
    allowed_roles?: string[]
}

export interface ToolTestResult {
    success: boolean
    result?: Record<string, unknown>
    error?: string
    latency_ms: number
}

interface ToolsState {
    // Data
    tools: Tool[]
    selectedTool: Tool | null
    isLoading: boolean
    error: string | null

    // Filters
    searchQuery: string
    statusFilter: string
    typeFilter: string
    categoryFilter: string

    // Actions
    setTools: (tools: Tool[]) => void
    setSelectedTool: (tool: Tool | null) => void
    setLoading: (loading: boolean) => void
    setError: (error: string | null) => void
    setSearchQuery: (query: string) => void
    setStatusFilter: (status: string) => void
    setTypeFilter: (type: string) => void
    setCategoryFilter: (category: string) => void

    // API Actions
    fetchTools: () => Promise<void>
    createTool: (tool: ToolCreate) => Promise<Tool | null>
    updateTool: (id: string, update: ToolUpdate) => Promise<Tool | null>
    deleteTool: (id: string) => Promise<boolean>
    testTool: (id: string, params: Record<string, unknown>) => Promise<ToolTestResult | null>
}

// API helper
const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token")
    return {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
    }
}

export const useToolStore = create<ToolsState>((set, get) => ({
    // Initial state
    tools: [],
    selectedTool: null,
    isLoading: false,
    error: null,
    searchQuery: "",
    statusFilter: "all",
    typeFilter: "all",
    categoryFilter: "all",

    // Simple setters
    setTools: (tools) => set({ tools }),
    setSelectedTool: (tool) => set({ selectedTool: tool }),
    setLoading: (loading) => set({ isLoading: loading }),
    setError: (error) => set({ error }),
    setSearchQuery: (query) => set({ searchQuery: query }),
    setStatusFilter: (status) => set({ statusFilter: status }),
    setTypeFilter: (type) => set({ typeFilter: type }),
    setCategoryFilter: (category) => set({ categoryFilter: category }),

    // API Actions
    fetchTools: async () => {
        set({ isLoading: true, error: null })
        try {
            const { searchQuery, statusFilter, typeFilter } = get()
            const params = new URLSearchParams()
            if (searchQuery) params.append("search", searchQuery)
            if (statusFilter !== "all") params.append("status", statusFilter)
            if (typeFilter !== "all") params.append("tool_type", typeFilter)

            const response = await fetch(`/api/v1/tools/?${params}`, {
                headers: getAuthHeaders(),
            })

            if (!response.ok) {
                throw new Error("Failed to fetch tools")
            }

            const data = await response.json()
            set({ tools: data.data, isLoading: false })
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
        }
    },

    createTool: async (toolData) => {
        set({ isLoading: true, error: null })
        try {
            const response = await fetch("/api/v1/tools/", {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify(toolData),
            })

            if (!response.ok) {
                throw new Error("Failed to create tool")
            }

            const newTool = await response.json()
            set((state) => ({
                tools: [newTool, ...state.tools],
                isLoading: false,
            }))
            return newTool
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
            return null
        }
    },

    updateTool: async (id, update) => {
        set({ isLoading: true, error: null })
        try {
            const response = await fetch(`/api/v1/tools/${id}`, {
                method: "PATCH",
                headers: getAuthHeaders(),
                body: JSON.stringify(update),
            })

            if (!response.ok) {
                throw new Error("Failed to update tool")
            }

            const updatedTool = await response.json()
            set((state) => ({
                tools: state.tools.map((t) => (t.id === id ? updatedTool : t)),
                selectedTool:
                    state.selectedTool?.id === id ? updatedTool : state.selectedTool,
                isLoading: false,
            }))
            return updatedTool
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
            return null
        }
    },

    deleteTool: async (id) => {
        set({ isLoading: true, error: null })
        try {
            const response = await fetch(`/api/v1/tools/${id}`, {
                method: "DELETE",
                headers: getAuthHeaders(),
            })

            if (!response.ok) {
                throw new Error("Failed to delete tool")
            }

            set((state) => ({
                tools: state.tools.filter((t) => t.id !== id),
                selectedTool: state.selectedTool?.id === id ? null : state.selectedTool,
                isLoading: false,
            }))
            return true
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false })
            return false
        }
    },

    testTool: async (id, params) => {
        try {
            const response = await fetch(`/api/v1/tools/${id}/test`, {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({ params }),
            })

            if (!response.ok) {
                throw new Error("Failed to test tool")
            }

            return await response.json()
        } catch (error) {
            set({ error: (error as Error).message })
            return null
        }
    },
}))
