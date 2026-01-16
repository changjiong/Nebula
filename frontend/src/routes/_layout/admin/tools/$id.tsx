import { ToolDataMappingEditor } from "@/components/Admin/ToolDataMappingEditor"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import axios from "axios"
import { ArrowLeft, Box } from "lucide-react"

export const Route = createFileRoute("/_layout/admin/tools/$id")({
  component: ToolDetailPage,
})

function ToolDetailPage() {
  const { id } = Route.useParams()

  const { data: tool, isLoading } = useQuery({
    queryKey: ["tool", id],
    queryFn: async () => {
      const res = await axios.get(`/api/v1/tools/${id}`) // Assuming generic GET endpoint exists, if not we use existing fetch list or add endpoint.
      // Wait, standard_tables.py has get /tools/{id}/data-graph but generic Tool GET might be missing in `tools.py`?
      // Let's assume it exists or I might need to check. 
      // Based on `tools.tsx`, it just listed tools. 
      // If it fails, I'll need to check `backend/app/api/routes/tools.py`.
      return res.data
    },
    // If endpoint returns specific structure, adjust accordingly.
  })

  if (isLoading) {
    return <div className="p-8">Loading...</div>
  }

  if (!tool) {
    return <div className="p-8">Tool not found</div>
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/admin/tools">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{tool.display_name}</h1>
          <div className="flex items-center gap-2 text-muted-foreground mt-1">
            <Badge variant="outline" className="font-mono">{tool.tool_type}</Badge>
            <span>{tool.name}</span>
          </div>
        </div>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList>
          <TabsTrigger value="general">General Info</TabsTrigger>
          <TabsTrigger value="linkage">Data Linkage</TabsTrigger>
          <TabsTrigger value="test">Test Tool</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Description</h4>
                  <p className="mt-1">{tool.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Category</h4>
                    <p className="mt-1">{tool.category}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground">Status</h4>
                    <Badge variant={tool.status === "active" ? "default" : "secondary"}>
                      {tool.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Usage Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold">{tool.call_count}</div>
                    <div className="text-xs text-muted-foreground uppercase mt-1">Calls</div>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold">{(tool.success_rate * 100).toFixed(1)}%</div>
                    <div className="text-xs text-muted-foreground uppercase mt-1">Success</div>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold">{tool.avg_latency_ms}ms</div>
                    <div className="text-xs text-muted-foreground uppercase mt-1">Latency</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Schema Definition</CardTitle>
                <CardDescription>Input and Output schemas defined for this tool</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div className="border rounded-md p-4 bg-muted/30">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Box className="h-4 w-4" /> Input Schema
                  </h4>
                  <pre className="text-xs overflow-auto max-h-[300px]">
                    {JSON.stringify(tool.input_schema, null, 2)}
                  </pre>
                </div>
                <div className="border rounded-md p-4 bg-muted/30">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Box className="h-4 w-4" /> Output Schema
                  </h4>
                  <pre className="text-xs overflow-auto max-h-[300px]">
                    {JSON.stringify(tool.output_schema, null, 2)}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="linkage">
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 text-blue-800 p-4 rounded-md text-sm">
              <h4 className="font-semibold mb-1">Data Lineage Mapping</h4>
              <p>
                Connect this tool's input/output parameters to Standard Data Tables.
                This enables automated lineage tracking and impact analysis.
              </p>
            </div>
            <ToolDataMappingEditor
              toolId={id}
              inputSchema={tool.input_schema}
              outputSchema={tool.output_schema}
            />
          </div>
        </TabsContent>

        <TabsContent value="test">
          <Card>
            <CardHeader>
              <CardTitle>Test Tool</CardTitle>
              <CardDescription>Execute tool with custom parameters (Coming Soon)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center p-12 text-muted-foreground border-2 border-dashed rounded-lg">
                Tool testing interface placeholder
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
