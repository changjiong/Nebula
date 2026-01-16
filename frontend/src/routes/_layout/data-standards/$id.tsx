import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import axios from "axios"
import { ArrowLeft, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"

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
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

// --- Schemas & Types ---

const fieldSchema = z.object({
    name: z.string().min(1, "Name is required"),
    display_name: z.string().min(1, "Display Name is required"),
    data_type: z.enum(["string", "number", "boolean", "date", "json", "array"]),
    description: z.string().optional(),
    is_primary_key: z.boolean(),
    is_nullable: z.boolean(),
})

type FieldFormValues = z.infer<typeof fieldSchema>

interface StandardTable {
    id: string
    name: string
    display_name: string
    description?: string
    source: string
    status: string
    fields: TableField[]
}

interface TableField {
    id: string
    name: string
    display_name: string
    data_type: string
    description?: string
    is_primary_key: boolean
    is_nullable: boolean
}

// --- Route Definition ---

export const Route = createFileRoute("/_layout/data-standards/$id")({
    component: StandardTableDetailPage,
    loader: async ({ params }) => {
        // We can just pass params here if we want to prefetch, 
        // but using useQuery in component is fine for now
        return { id: params.id }
    }
})

// --- Components ---

function StandardTableDetailPage() {
    const { id } = Route.useParams()
    const queryClient = useQueryClient()
    const [isAddFieldOpen, setIsAddFieldOpen] = useState(false)

    // Fetch Table Details
    const { data: table, isLoading } = useQuery<StandardTable>({
        queryKey: ["standard_table", id],
        queryFn: async () => {
            const res = await axios.get(`/api/v1/standard-tables/${id}`)
            return res.data
        },
    })

    // Add Field Mutation
    const addFieldMutation = useMutation({
        mutationFn: (values: FieldFormValues) => {
            return axios.post("/api/v1/standard-tables/fields", {
                ...values,
                table_id: id,
            })
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["standard_table", id] })
            setIsAddFieldOpen(false)
            toast.success("Field added successfully")
        },
        onError: () => {
            toast.error("Failed to add field")
        },
    })

    // Delete Field Mutation
    const deleteFieldMutation = useMutation({
        mutationFn: (fieldId: string) => {
            return axios.delete(`/api/v1/standard-tables/fields/${fieldId}`)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["standard_table", id] })
            toast.success("Field deleted")
        },
    })

    // Form handling
    const form = useForm<FieldFormValues>({
        resolver: zodResolver(fieldSchema),
        defaultValues: {
            data_type: "string",
            is_primary_key: false,
            is_nullable: true,
            name: "",
            display_name: "",
            description: "",
        },
    })

    const onAddFieldSubmit = (values: FieldFormValues) => {
        addFieldMutation.mutate(values)
        form.reset()
    }

    if (isLoading) {
        return <div className="p-8">Loading...</div>
    }

    if (!table) {
        return <div className="p-8">Table not found</div>
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link to="/data-standards">
                        <ArrowLeft className="h-5 w-5" />
                    </Link>
                </Button>
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">{table.display_name}</h1>
                    <div className="flex items-center gap-2 text-muted-foreground mt-1">
                        <Badge variant="outline">{table.source}</Badge>
                        <span>{table.name}</span>
                    </div>
                </div>
            </div>

            {/* Basic Info Card (Optional expansion) */}
            <div className="bg-card border rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold mb-2">Description</h3>
                <p className="text-muted-foreground">
                    {table.description || "No description provided."}
                </p>
            </div>

            {/* Fields Section */}
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-lg font-semibold">Table Fields</h2>
                    <Dialog open={isAddFieldOpen} onOpenChange={setIsAddFieldOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="mr-2 h-4 w-4" />
                                Add Field
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Add Field</DialogTitle>
                            </DialogHeader>
                            <form onSubmit={form.handleSubmit(onAddFieldSubmit)} className="space-y-4 py-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Field Name (En)</Label>
                                        <Input {...form.register("name")} placeholder="e.g. amount" />
                                        {form.formState.errors.name && <p className="text-red-500 text-xs">{form.formState.errors.name.message}</p>}
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Display Name</Label>
                                        <Input {...form.register("display_name")} placeholder="e.g. Amount" />
                                        {form.formState.errors.display_name && <p className="text-red-500 text-xs">{form.formState.errors.display_name.message}</p>}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label>Data Type</Label>
                                    <Select onValueChange={(v) => form.setValue("data_type", v as any)} defaultValue="string">
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select type" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="string">String</SelectItem>
                                            <SelectItem value="number">Number</SelectItem>
                                            <SelectItem value="boolean">Boolean</SelectItem>
                                            <SelectItem value="date">Date</SelectItem>
                                            <SelectItem value="json">JSON</SelectItem>
                                            <SelectItem value="array">Array</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Input {...form.register("description")} />
                                </div>

                                <div className="flex gap-4">
                                    <label className="flex items-center gap-2 text-sm">
                                        <input type="checkbox" {...form.register("is_primary_key")} className="rounded border-gray-300" />
                                        Primary Key
                                    </label>
                                    <label className="flex items-center gap-2 text-sm">
                                        <input type="checkbox" {...form.register("is_nullable")} className="rounded border-gray-300" />
                                        Nullable
                                    </label>
                                </div>

                                <DialogFooter>
                                    <Button type="submit" disabled={addFieldMutation.isPending}>Add Field</Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>

                {/* Fields Table */}
                <div className="border rounded-md">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Field Name</TableHead>
                                <TableHead>Display Name</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Attributes</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {table.fields?.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                        No fields defined yet.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                table.fields?.map((field: TableField) => (
                                    <TableRow key={field.id}>
                                        <TableCell className="font-medium">{field.name}</TableCell>
                                        <TableCell>{field.display_name}</TableCell>
                                        <TableCell>
                                            <Badge variant="secondary" className="font-mono text-xs">{field.data_type}</Badge>
                                        </TableCell>
                                        <TableCell className="space-x-2">
                                            {field.is_primary_key && <Badge variant="default" className="text-[10px] h-5">PK</Badge>}
                                            {!field.is_nullable && <Badge variant="outline" className="text-[10px] h-5">Not Null</Badge>}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-red-500 hover:text-red-600 hover:bg-red-50"
                                                onClick={() => {
                                                    if (confirm("Are you sure you want to delete this field?")) {
                                                        deleteFieldMutation.mutate(field.id)
                                                    }
                                                }}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    )
}
