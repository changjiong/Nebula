import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface ScoreCardProps {
    data: {
        total_score: number
        score_breakdown?: Record<string, number>
        rank?: number
        level?: string
    }
    config?: {
        maxScore?: number
        showBreakdown?: boolean
    }
}

export function ScoreCard({ data, config = {} }: ScoreCardProps) {
    const { maxScore = 100, showBreakdown = true } = config
    const percentage = (data.total_score / maxScore) * 100

    const getScoreColor = (score: number) => {
        if (score >= 80) return "text-green-600"
        if (score >= 60) return "text-yellow-600"
        return "text-red-600"
    }

    const getLevelBadge = (level: string) => {
        const colors: Record<string, string> = {
            excellent: "bg-green-100 text-green-800",
            good: "bg-blue-100 text-blue-800",
            average: "bg-yellow-100 text-yellow-800",
            poor: "bg-red-100 text-red-800",
        }
        return colors[level.toLowerCase()] || "bg-gray-100 text-gray-800"
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>综合评分</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-end justify-between">
                    <div>
                        <div className={`text-5xl font-bold ${getScoreColor(data.total_score)}`}>
                            {data.total_score}
                        </div>
                        <div className="text-sm text-muted-foreground">满分 {maxScore}</div>
                    </div>
                    {data.level && (
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getLevelBadge(data.level)}`}>
                            {data.level}
                        </div>
                    )}
                    {data.rank && (
                        <div className="text-right">
                            <div className="text-2xl font-semibold">#{data.rank}</div>
                            <div className="text-sm text-muted-foreground">排名</div>
                        </div>
                    )}
                </div>

                <Progress value={percentage} className="h-2" />

                {showBreakdown && data.score_breakdown && (
                    <div className="space-y-2 pt-4 border-t">
                        <div className="text-sm font-medium">评分明细</div>
                        {Object.entries(data.score_breakdown).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between">
                                <span className="text-sm text-muted-foreground capitalize">{key}</span>
                                <div className="flex items-center gap-2">
                                    <Progress value={value} className="h-1 w-24" />
                                    <span className="text-sm font-medium w-8 text-right">{value}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
