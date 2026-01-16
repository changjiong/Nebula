import { Link } from "@tanstack/react-router"
import {
    AlertCircle,
    CheckCircle2,
    Clock,
    MoreHorizontal,
    Pencil,
    Play,
    Plus,
    Search,
    Trash2,
} from "lucide-react"
import { useState } from "react"
import { ToolDataGraph } from "@/components/DataGraph/ToolDataGraph"
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
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
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

// Mock data for demonstration
const mockTools = [
    {
        id: "1",
        name: "kechuang_score",
        display_name: "科创能力评分",
        description: "对企业进行科创能力五维评分，包括创新能力、研发投入等",
        tool_type: "ml_model",
        status: "active",
        category: "评分类",
        call_count: 12345,
        success_rate: 99.2,
        avg_latency_ms: 235,
    },
    {
        id: "2",
        name: "enterprise_query",
        display_name: "企业信息查询",
        description: "查询企业基本信息，包括注册资本、法人代表等",
        tool_type: "data_api",
        status: "active",
        category: "数据查询",
        call_count: 45678,
        success_rate: 99.8,
        avg_latency_ms: 120,
    },
    {
        id: "3",
        name: "relation_graph",
        display_name: "关系图谱查询",
        description: "查询企业关联关系，包括股东、子公司等",
        tool_type: "data_api",
        status: "active",
        category: "数据查询",
        call_count: 8901,
        success_rate: 98.5,
        avg_latency_ms: 450,
    },
    {
        id: "4",
        name: "credit_score",
        display_name: "征信评分",
        description: "企业征信评分模型",
        tool_type: "ml_model",
        status: "draft",
        category: "评分类",
        call_count: 0,
        success_rate: 0,
        avg_latency_ms: 0,
    },
]

export function ToolsList() {
    const [search, setSearch] = useState("")
    const [statusFilter, setStatusFilter] = useState<string>("all")
    const [typeFilter, setTypeFilter] = useState<string>("all")
    const [selectedToolId, setSelectedToolId] = useState<string | null>(null)
    const [isGraphOpen, setIsGraphOpen] = useState(false)

    const filteredTools = mockTools.filter((tool) => {
        const matchesSearch =
            tool.name.toLowerCase().includes(search.toLowerCase()) ||
            tool.display_name.toLowerCase().includes(search.toLowerCase())
        const matchesStatus = statusFilter === "all" || tool.status === statusFilter
        const matchesType = typeFilter === "all" || tool.tool_type === typeFilter
        return matchesSearch && matchesStatus && matchesType
    })

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "active":
                return (
                    <Badge variant="default" className="bg-green-500">
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                        启用
                    </Badge>
                )
            case "draft":
                return (
                    <Badge variant="secondary">
                        <Clock className="mr-1 h-3 w-3" />
                        草稿
                    </Badge>
                )
            case "deprecated":
                return (
                    <Badge variant="destructive">
                        <AlertCircle className="mr-1 h-3 w-3" />
                        已废弃
                    </Badge>
                )
            default:
                return <Badge variant="outline">{status}</Badge>
        }
    }

    const getTypeBadge = (type: string) => {
        switch (type) {
            case "ml_model":
                return <Badge variant="outline">🤖 ML模型</Badge>
            case "data_api":
                return <Badge variant="outline">📊 数仓API</Badge>
            case "external_api":
                return <Badge variant="outline">🌐 外部API</Badge>
            default:
                return <Badge variant="outline">{type}</Badge>
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Tools</h1>
                    <p className="text-muted-foreground">
                        Manage knowledge engineering tools
                    </p>
                </div>
                <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Tool
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-wrap gap-4">
                        <div className="flex-1 min-w-[200px]">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                                <Input
                                    placeholder="搜索工具..."
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-[140px]">
                                <SelectValue placeholder="状态" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">全部状态</SelectItem>
                                <SelectItem value="active">启用</SelectItem>
                                <SelectItem value="draft">草稿</SelectItem>
                                <SelectItem value="deprecated">已废弃</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select value={typeFilter} onValueChange={setTypeFilter}>
                            <SelectTrigger className="w-[140px]">
                                <SelectValue placeholder="类型" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">全部类型</SelectItem>
                                <SelectItem value="ml_model">ML模型</SelectItem>
                                <SelectItem value="data_api">数仓API</SelectItem>
                                <SelectItem value="external_api">外部API</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* Tools Table */}
            <Card>
                <CardHeader>
                    <CardTitle>工具列表</CardTitle>
                    <CardDescription>共 {filteredTools.length} 个工具</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[200px]">名称</TableHead>
                                <TableHead>描述</TableHead>
                                <TableHead className="w-[100px]">类型</TableHead>
                                <TableHead className="w-[80px]">状态</TableHead>
                                <TableHead className="w-[80px] text-right">调用次数</TableHead>
                                <TableHead className="w-[80px] text-right">成功率</TableHead>
                                <TableHead className="w-[80px] text-right">延迟</TableHead>
                                <TableHead className="w-[60px]" />
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredTools.map((tool) => (
                                <TableRow key={tool.id}>
                                    <TableCell>
                                        <div>
                                            <div className="font-medium">{tool.display_name}</div>
                                            <div className="text-sm text-muted-foreground font-mono">
                                                {tool.name}
                                            </div>
                                        </div>
                                    </TableCell>
                                    <TableCell className="max-w-[300px] truncate">
                                        {tool.description}
                                    </TableCell>
                                    <TableCell>{getTypeBadge(tool.tool_type)}</TableCell>
                                    <TableCell>{getStatusBadge(tool.status)}</TableCell>
                                    <TableCell className="text-right font-mono">
                                        {tool.call_count.toLocaleString()}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {tool.success_rate > 0 ? `${tool.success_rate}%` : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {tool.avg_latency_ms > 0 ? `${tool.avg_latency_ms}ms` : "-"}
                                    </TableCell>
                                    <TableCell>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" size="icon">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem asChild>
                                                    <Link to="/admin/tools/$id" params={{ id: tool.id }}>
                                                        <Pencil className="mr-2 h-4 w-4" />
                                                        Manage & Map
                                                    </Link>
                                                </DropdownMenuItem>
                                                <DropdownMenuSeparator />
                                                <DropdownMenuItem>
                                                    <Play className="mr-2 h-4 w-4" />
                                                    Test Run
                                                </DropdownMenuItem>
                                                <DropdownMenuItem
                                                    onClick={() => {
                                                        setSelectedToolId(tool.id)
                                                        setIsGraphOpen(true)
                                                    }}
                                                >
                                                    <Search className="mr-2 h-4 w-4" />
                                                    View Graph
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
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Dialog open={isGraphOpen} onOpenChange={setIsGraphOpen}>
                <DialogContent className="max-w-4xl h-[600px]">
                    <DialogHeader>
                        <DialogTitle>Data Lineage Visualization</DialogTitle>
                    </DialogHeader>
                    {selectedToolId && <ToolDataGraph toolId={selectedToolId} />}
                </DialogContent>
            </Dialog>
        </div>
    )
}
