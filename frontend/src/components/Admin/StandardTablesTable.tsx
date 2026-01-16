import {
  AlertCircle,
  CheckCircle2,
  Clock,
  MoreHorizontal,
  Pencil,
  Trash2,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export interface StandardTable {
  id: string
  name: string
  display_name: string
  description?: string
  category?: string
  source: "data_warehouse" | "external_api" | "ml_output"
  status: "active" | "draft" | "deprecated"
  updated_at: string
}

interface StandardTablesTableProps {
  data: StandardTable[]
  isLoading?: boolean
}

export function StandardTablesTable({
  data,
  isLoading,
}: StandardTablesTableProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="default" className="bg-green-500">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Active
          </Badge>
        )
      case "draft":
        return (
          <Badge variant="secondary">
            <Clock className="mr-1 h-3 w-3" />
            Draft
          </Badge>
        )
      case "deprecated":
        return (
          <Badge variant="destructive">
            <AlertCircle className="mr-1 h-3 w-3" />
            Deprecated
          </Badge>
        )
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getSourceBadge = (source: string) => {
    switch (source) {
      case "data_warehouse":
        return <Badge variant="outline">Data Warehouse</Badge>
      case "external_api":
        return <Badge variant="outline">External API</Badge>
      case "ml_output":
        return <Badge variant="outline">ML Output</Badge>
      default:
        return <Badge variant="outline">{source}</Badge>
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Standard Tables</CardTitle>
        <CardDescription>{data.length} standard tables defined</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[200px]">Name</TableHead>
              <TableHead>Category</TableHead>
              <TableHead className="w-[150px]">Source</TableHead>
              <TableHead className="w-[100px]">Status</TableHead>
              <TableHead className="w-[150px]">Last Updated</TableHead>
              <TableHead className="w-[60px]" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((table) => (
              <TableRow key={table.id}>
                <TableCell>
                  <div>
                    <div className="font-medium">{table.display_name}</div>
                    <div className="text-sm text-muted-foreground font-mono">
                      {table.name}
                    </div>
                  </div>
                </TableCell>
                <TableCell>{table.category || "-"}</TableCell>
                <TableCell>{getSourceBadge(table.source)}</TableCell>
                <TableCell>{getStatusBadge(table.status)}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(table.updated_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-destructive">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
            {data.length === 0 && !isLoading && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center py-8 text-muted-foreground"
                >
                  No standard tables found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
