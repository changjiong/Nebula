import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import axios from "axios"
import { ArrowLeftRight, Trash2 } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface ToolDataMappingEditorProps {
  toolId: string
  inputSchema: any
  outputSchema: any
}

// Helper to extract leaf paths from JSON schema
const extractPaths = (schema: any, prefix = ""): string[] => {
  if (!schema || !schema.properties) return []
  let paths: string[] = []
  for (const key in schema.properties) {
    const prop = schema.properties[key]
    const currentPath = prefix ? `${prefix}.${key}` : key
    if (prop.type === "object" && prop.properties) {
      paths = [...paths, ...extractPaths(prop, currentPath)]
    } else {
      paths.push(currentPath)
    }
  }
  return paths
}

export function ToolDataMappingEditor({
  toolId,
  inputSchema,
  outputSchema,
}: ToolDataMappingEditorProps) {
  const queryClient = useQueryClient()
  const [selectedTableId, setSelectedTableId] = useState<string>("")
  const [selectedDirection, setSelectedDirection] = useState<
    "input" | "output"
  >("output")
  const [selectedParam, setSelectedParam] = useState<string>("")
  const [selectedFieldId, setSelectedFieldId] = useState<string>("")

  // Fetch Existing Mappings
  const { data: mappingData } = useQuery({
    queryKey: ["tool_mappings", toolId],
    queryFn: async () => {
      const res = await axios.get(`/api/v1/tools/${toolId}/data-graph`)
      return res.data // { mappings, tables }
    },
  })

  // Fetch All Standard Tables
  const { data: standardTables } = useQuery({
    queryKey: ["standard_tables_list"],
    queryFn: async () => {
      const res = await axios.get("/api/v1/standard-tables?limit=100")
      return res.data.data
    },
  })

  // Fetch Fields for Selected Table
  const { data: selectedTable } = useQuery({
    queryKey: ["standard_table", selectedTableId],
    queryFn: async () => {
      if (!selectedTableId) return null
      const res = await axios.get(`/api/v1/standard-tables/${selectedTableId}`)
      return res.data
    },
    enabled: !!selectedTableId,
  })

  // Create Mapping Mutation
  const createMappingMutation = useMutation({
    mutationFn: () => {
      return axios.post("/api/v1/tools/mappings", {
        tool_id: toolId,
        param_path: selectedParam,
        param_direction: selectedDirection,
        table_id: selectedTableId,
        field_id: selectedFieldId,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tool_mappings", toolId] })
      toast.success("Mapping created")
      // Reset selections partially
      setSelectedParam("")
      setSelectedFieldId("")
    },
    onError: () => {
      toast.error("Failed to create mapping")
    },
  })

  // Delete Mapping Mutation
  const deleteMappingMutation = useMutation({
    mutationFn: (id: string) => {
      return axios.delete(`/api/v1/tools/mappings/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tool_mappings", toolId] })
      toast.success("Mapping deleted")
    },
  })

  // Derived State
  const inputPaths = extractPaths(inputSchema)
  const outputPaths = extractPaths(outputSchema)
  const availableParams =
    selectedDirection === "input" ? inputPaths : outputPaths
  const availableFields = selectedTable?.fields || []

  // enrich mappings with table/field info
  const enrichedMappings = mappingData?.mappings?.map((m: any) => {
    // We can find table/field info from mappingData.tables if returned, or we rely on backend response.
    // The backend `get_tool_data_graph` returns `mappings` and associated `tables`.
    // However, `mappings` objects only have IDs. We need to match IDs.
    // Ideally we should augment the API to return expanded objects or use the `tables` list.
    // Note: `tables` from that API might not include fields if not eager loaded.
    // Let's check backend implementation. `StandardTable` model has `fields` relationship.
    // `get_tool_data_graph` returns `tables` from simple select, so lazy loading might apply.
    // But usually SQLModel relationships are lazy.
    // Let's assume we might display IDs if names are missing, or better, fetch details.
    // Actually the component fetches individual table details? No, it only fetches `selectedTable`.

    // Workaround: We display what we have.
    // Ideally we should update the `get_tool_data_graph` API to return full details
    // or fetch all referenced tables.
    // For now, let's look up in the `standardTables` list if available.
    const tableInfo = standardTables?.find((t: any) => t.id === m.table_id)

    // We don't have field names easily without fetching all tables detailed.
    // Display raw path + table name for now.
    return {
      ...m,
      tableName: tableInfo?.name || m.table_id,
      fieldName: m.field_id, // Placeholder
    }
  })

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Editor Panel */}
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle>Add Mapping</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <span className="text-sm font-medium block">1. Direction</span>
            <div className="flex gap-2">
              <Button
                variant={selectedDirection === "input" ? "default" : "outline"}
                onClick={() => setSelectedDirection("input")}
                size="sm"
                className="w-full"
              >
                Input
              </Button>
              <Button
                variant={selectedDirection === "output" ? "default" : "outline"}
                onClick={() => setSelectedDirection("output")}
                size="sm"
                className="w-full"
              >
                Output
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-sm font-medium block">2. Parameter Path</span>
            <Select value={selectedParam} onValueChange={setSelectedParam}>
              <SelectTrigger>
                <SelectValue placeholder="Select parameter" />
              </SelectTrigger>
              <SelectContent>
                {availableParams.length === 0 ? (
                  <SelectItem value="_none" disabled>
                    No parameters found
                  </SelectItem>
                ) : (
                  availableParams.map((p) => (
                    <SelectItem key={p} value={p}>
                      {p}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-center py-2">
            <ArrowLeftRight className="h-4 w-4 text-muted-foreground rotate-90" />
          </div>

          <div className="space-y-2">
            <span className="text-sm font-medium block">
              3. Target Standard Table
            </span>
            <Select value={selectedTableId} onValueChange={setSelectedTableId}>
              <SelectTrigger>
                <SelectValue placeholder="Select table" />
              </SelectTrigger>
              <SelectContent>
                {standardTables?.map((t: any) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.display_name} ({t.name})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <span className="text-sm font-medium block">4. Target Field</span>
            <Select
              value={selectedFieldId}
              onValueChange={setSelectedFieldId}
              disabled={!selectedTableId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select field" />
              </SelectTrigger>
              <SelectContent>
                {availableFields.map((f: any) => (
                  <SelectItem key={f.id} value={f.id}>
                    {f.display_name} ({f.name})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            className="w-full mt-4"
            onClick={() => createMappingMutation.mutate()}
            disabled={
              !selectedParam ||
              !selectedFieldId ||
              createMappingMutation.isPending
            }
          >
            Create Mapping
          </Button>
        </CardContent>
      </Card>

      {/* List Panel */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Existing Mappings</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Direction</TableHead>
                <TableHead>Param Path</TableHead>
                <TableHead>Standard Table</TableHead>
                <TableHead>Field ID</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {enrichedMappings?.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="text-center py-8 text-muted-foreground"
                  >
                    No mappings defined.
                  </TableCell>
                </TableRow>
              ) : (
                enrichedMappings?.map((m: any) => (
                  <TableRow key={m.id}>
                    <TableCell>
                      <Badge
                        variant={
                          m.param_direction === "input"
                            ? "secondary"
                            : "default"
                        }
                      >
                        {m.param_direction}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm">
                      {m.param_path}
                    </TableCell>
                    <TableCell>{m.tableName}</TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {m.field_id}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-500 hover:text-red-600 hover:bg-red-50"
                        onClick={() => deleteMappingMutation.mutate(m.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
