import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import axios from "axios"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"
import { StandardTablesTable } from "@/components/Admin/StandardTablesTable"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const tableSchema = z.object({
  name: z.string().min(1, "Name is required"),
  display_name: z.string().min(1, "Display Name is required"),
  description: z.string().optional(),
  source: z.enum(["data_warehouse", "external_api", "ml_output"]),
  status: z.enum(["active", "draft", "deprecated"]),
})

type TableFormValues = z.infer<typeof tableSchema>

export const Route = createFileRoute("/_layout/admin/data-standards")({
  component: DataStandardsPage,
})

function DataStandardsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ["standard_tables"],
    queryFn: async () => {
      try {
        const res = await axios.get("/api/v1/standard-tables?limit=100")
        return res.data
      } catch (_e) {
        return { data: [], count: 0 }
      }
    },
  })

  // Safe access to data based on API response structure { data: [], count: 0 }
  const standardTables = data?.data || []

  const form = useForm<TableFormValues>({
    resolver: zodResolver(tableSchema),
    defaultValues: {
      source: "data_warehouse",
      status: "active",
      description: "",
      name: "",
      display_name: "",
    },
  })

  const createMutation = useMutation({
    mutationFn: (newTable: TableFormValues) => {
      return axios.post("/api/v1/standard-tables", newTable)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["standard_tables"] })
      setIsCreateOpen(false)
      form.reset()
      toast.success("Standard Table created")
    },
    onError: () => {
      toast.error("Failed to create table")
    },
  })

  const onSubmit = (values: TableFormValues) => {
    createMutation.mutate(values)
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Data Standards</h1>
          <p className="text-muted-foreground mt-1">
            Manage standardized data tables.
          </p>
        </div>

        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Standard Table
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create Standard Table</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4 py-4"
            >
              <div className="space-y-2">
                <Label htmlFor="name">System Name</Label>
                <Input
                  id="name"
                  {...form.register("name")}
                  placeholder="e.g. enterprise_info"
                />
                {form.formState.errors.name && (
                  <p className="text-sm text-red-500">
                    {form.formState.errors.name.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  {...form.register("display_name")}
                  placeholder="e.g. Enterprise Info"
                />
                {form.formState.errors.display_name && (
                  <p className="text-sm text-red-500">
                    {form.formState.errors.display_name.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="source">Source</Label>
                <Select
                  onValueChange={(val) => form.setValue("source", val as any)}
                  defaultValue="data_warehouse"
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Source" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="data_warehouse">
                      Data Warehouse
                    </SelectItem>
                    <SelectItem value="external_api">External API</SelectItem>
                    <SelectItem value="ml_output">ML Output</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input id="description" {...form.register("description")} />
              </div>
              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending}>
                  Create
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <StandardTablesTable data={standardTables} isLoading={isLoading} />
    </div>
  )
}
