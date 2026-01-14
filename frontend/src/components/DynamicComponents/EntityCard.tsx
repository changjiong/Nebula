import { Building2, Calendar, MapPin, User } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

interface EntityCardProps {
  data: {
    name: string
    credit_code: string
    legal_person?: string
    registered_capital?: string
    status?: string
    region?: string
    established_date?: string
    [key: string]: any
  }
  config?: any
}

export function EntityCard({ data }: EntityCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-xl flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              {data.name}
            </CardTitle>
            <CardDescription>
              统一社会信用代码：{data.credit_code}
            </CardDescription>
          </div>
          {data.status && (
            <Badge variant={data.status === "存续" ? "default" : "secondary"}>
              {data.status}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {data.legal_person && (
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                <span className="text-muted-foreground">法定代表人：</span>
                {data.legal_person}
              </span>
            </div>
          )}
          {data.registered_capital && (
            <div className="flex items-center gap-2">
              <span className="text-sm">
                <span className="text-muted-foreground">注册资本：</span>
                {data.registered_capital}
              </span>
            </div>
          )}
          {data.region && (
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">{data.region}</span>
            </div>
          )}
          {data.established_date && (
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                <span className="text-muted-foreground">成立日期：</span>
                {data.established_date}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
