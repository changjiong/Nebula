import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"

interface DataTableProps {
    data: Array<Record<string, any>>
    config?: {
        columns?: Array<{
            key: string
            title: string
            width?: number
            sortable?: boolean
        }>
        pagination?: {
            pageSize: number
        }
        exportable?: boolean
    }
}

export function DataTable({ data, config }: DataTableProps) {
    const columns = config?.columns || Object.keys(data[0] || {}).map((key) => ({
        key,
        title: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " "),
    }))

    const handleExport = () => {
        // TODO: Implement export to Excel
        console.log("Exporting data:", data)
    }

    return (
        <div className="space-y-4">
            {config?.exportable && (
                <div className="flex justify-end">
                    <Button onClick={handleExport} variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        导出Excel
                    </Button>
                </div>
            )}
            <div className="rounded-md border">
                <Table>
                    {data.length > 0 && (
                        <TableCaption>共 {data.length} 条记录</TableCaption>
                    )}
                    <TableHeader>
                        <TableRow>
                            {columns.map((col) => (
                                <TableHead key={col.key} style={{ width: col.width }}>
                                    {col.title}
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row, idx) => (
                            <TableRow key={idx}>
                                {columns.map((col) => (
                                    <TableCell key={col.key}>{row[col.key]}</TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}
