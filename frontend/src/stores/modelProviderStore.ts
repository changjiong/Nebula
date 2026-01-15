/**
 * Model Provider Store
 * Manages AI model provider configurations (OpenAI, DeepSeek, Gemini, etc.)
 */

import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface ModelProvider {
    id: string
    name: string
    provider_type: string
    api_url: string
    api_key_set: boolean
    is_enabled: boolean
    icon?: string
    models: string[]
    created_at: string
    updated_at: string
}

export interface AvailableModel {
    id: string
    name: string
    provider_id: string
    provider_name: string
    provider_type: string
}

interface ModelProviderState {
    providers: ModelProvider[]
    selectedProviderId: string | null
    selectedModelId: string | null
    isLoading: boolean
    error: string | null

    // Derived state: all enabled models
    getEnabledModels: () => AvailableModel[]

    // Actions
    setProviders: (providers: ModelProvider[]) => void
    selectProvider: (id: string | null) => void
    selectModel: (id: string | null) => void
    updateProviderLocally: (id: string, updates: Partial<ModelProvider>) => void
    setLoading: (loading: boolean) => void
    setError: (error: string | null) => void

    // API Actions
    fetchProviders: () => Promise<void>
    initPresets: () => Promise<void>
    createProvider: (data: CreateProviderData) => Promise<ModelProvider | null>
    updateProvider: (id: string, data: UpdateProviderData) => Promise<boolean>
    deleteProvider: (id: string) => Promise<boolean>
    testConnection: (id: string) => Promise<TestResult>
}

interface CreateProviderData {
    name: string
    provider_type: string
    api_url: string
    api_key?: string
    is_enabled?: boolean
    icon?: string
    models?: string[]
}

interface UpdateProviderData {
    name?: string
    provider_type?: string
    api_url?: string
    api_key?: string
    is_enabled?: boolean
    icon?: string
    models?: string[]
}

interface TestResult {
    success: boolean
    message: string
    available_models: string[]
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

function getAuthHeaders() {
    const token = localStorage.getItem("access_token")
    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
    }
}

export const useModelProviderStore = create<ModelProviderState>()(
    persist(
        (set, get) => ({
            providers: [],
            selectedProviderId: null,
            selectedModelId: null,
            isLoading: false,
            error: null,

            getEnabledModels: () => {
                const { providers } = get()
                return providers
                    .filter((p) => p.is_enabled && p.models.length > 0)
                    .flatMap((p) =>
                        p.models.map((modelId) => ({
                            id: modelId,
                            name: modelId,
                            provider_id: p.id,
                            provider_name: p.name,
                            provider_type: p.provider_type,
                        })),
                    )
            },



            setProviders: (providers) => {
                set({ providers })
                // Ensure selectedModelId is valid
                const { selectedModelId, getEnabledModels } = get()
                const enabled = getEnabledModels()
                if (enabled.length > 0) {
                    // If no model selected, or selected model no longer valid, select first available
                    if (!selectedModelId || !enabled.find(m => m.id === selectedModelId)) {
                        set({ selectedModelId: enabled[0].id })
                    }
                }
            },
            selectProvider: (id) => set({ selectedProviderId: id }),
            selectModel: (id) => set({ selectedModelId: id }),
            updateProviderLocally: (id, updates) =>
                set((state) => ({
                    providers: state.providers.map((p) =>
                        p.id === id ? { ...p, ...updates } : p,
                    ),
                })),
            setLoading: (isLoading) => set({ isLoading }),
            setError: (error) => set({ error }),

            fetchProviders: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await fetch(`${API_URL}/api/v1/model-providers/`, {
                        headers: getAuthHeaders(),
                    })
                    if (!response.ok) throw new Error("Failed to fetch providers")
                    const data = await response.json()

                    // Manually trigger setProviders logic to update defaults
                    const { setProviders } = get()
                    setProviders(data.data)
                    set({ isLoading: false })

                    // Select first provider if none selected
                    const { selectedProviderId } = get()
                    if (!selectedProviderId && data.data.length > 0) {
                        set({ selectedProviderId: data.data[0].id })
                    }
                } catch (error) {
                    set({
                        error: error instanceof Error ? error.message : "Unknown error",
                        isLoading: false,
                    })
                }
            },

            initPresets: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await fetch(
                        `${API_URL}/api/v1/model-providers/init-presets`,
                        {
                            method: "POST",
                            headers: getAuthHeaders(),
                        },
                    )
                    if (!response.ok) throw new Error("Failed to initialize presets")
                    const data = await response.json()
                    // Manually trigger setProviders logic to update defaults
                    const { setProviders } = get()
                    setProviders(data.data)
                    set({ isLoading: false })

                    // Select first provider
                    if (data.data.length > 0) {
                        set({ selectedProviderId: data.data[0].id })
                    }
                } catch (error) {
                    set({
                        error: error instanceof Error ? error.message : "Unknown error",
                        isLoading: false,
                    })
                }
            },

            createProvider: async (data) => {
                try {
                    const response = await fetch(`${API_URL}/api/v1/model-providers/`, {
                        method: "POST",
                        headers: getAuthHeaders(),
                        body: JSON.stringify(data),
                    })
                    if (!response.ok) {
                        const error = await response.json()
                        throw new Error(error.detail || "Failed to create provider")
                    }
                    const provider = await response.json()
                    set((state) => ({
                        providers: [...state.providers, provider],
                        selectedProviderId: provider.id,
                    }))
                    return provider
                } catch (error) {
                    set({ error: error instanceof Error ? error.message : "Unknown error" })
                    return null
                }
            },

            updateProvider: async (id, data) => {
                try {
                    const response = await fetch(
                        `${API_URL}/api/v1/model-providers/${id}`,
                        {
                            method: "PUT",
                            headers: getAuthHeaders(),
                            body: JSON.stringify(data),
                        },
                    )
                    if (!response.ok) throw new Error("Failed to update provider")
                    const updated = await response.json()
                    set((state) => ({
                        providers: state.providers.map((p) => (p.id === id ? updated : p)),
                    }))
                    return true
                } catch (error) {
                    set({ error: error instanceof Error ? error.message : "Unknown error" })
                    return false
                }
            },

            deleteProvider: async (id) => {
                try {
                    const response = await fetch(
                        `${API_URL}/api/v1/model-providers/${id}`,
                        {
                            method: "DELETE",
                            headers: getAuthHeaders(),
                        },
                    )
                    if (!response.ok) throw new Error("Failed to delete provider")
                    set((state) => ({
                        providers: state.providers.filter((p) => p.id !== id),
                        selectedProviderId:
                            state.selectedProviderId === id
                                ? state.providers[0]?.id || null
                                : state.selectedProviderId,
                    }))
                    return true
                } catch (error) {
                    set({ error: error instanceof Error ? error.message : "Unknown error" })
                    return false
                }
            },

            testConnection: async (id) => {
                try {
                    const response = await fetch(
                        `${API_URL}/api/v1/model-providers/${id}/test`,
                        {
                            method: "POST",
                            headers: getAuthHeaders(),
                        },
                    )
                    if (!response.ok) throw new Error("Test request failed")
                    return await response.json()
                } catch (error) {
                    return {
                        success: false,
                        message: error instanceof Error ? error.message : "Connection failed",
                        available_models: [],
                    }
                }
            },
        }),
        {
            name: "model-provider-storage",
            partialize: (state) => ({
                selectedProviderId: state.selectedProviderId,
                selectedModelId: state.selectedModelId,
            }),
        },
    ),
)
