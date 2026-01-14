import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface RadarDataPoint {
  axis: string
  value: number
}

interface RadarChartProps {
  data: RadarDataPoint[]
  maxValue?: number
  size?: number
  title?: string
  showLabels?: boolean
  showValues?: boolean
  fillColor?: string
  strokeColor?: string
}

export function RadarChart({
  data,
  maxValue = 100,
  size = 300,
  title,
  showLabels = true,
  showValues = true,
  fillColor = "rgba(59, 130, 246, 0.3)",
  strokeColor = "rgb(59, 130, 246)",
}: RadarChartProps) {
  const center = size / 2
  const radius = size * 0.35
  const levels = 5 // Number of concentric circles

  // Calculate points for the radar polygon
  const points = useMemo(() => {
    if (!data || data.length < 3) return []

    const angleStep = (Math.PI * 2) / data.length

    return data.map((point, index) => {
      const angle = angleStep * index - Math.PI / 2 // Start from top
      const normalizedValue = Math.min(point.value, maxValue) / maxValue
      const x = center + radius * normalizedValue * Math.cos(angle)
      const y = center + radius * normalizedValue * Math.sin(angle)
      return { x, y, ...point }
    })
  }, [data, maxValue, center, radius])

  // Calculate axis endpoints
  const axes = useMemo(() => {
    if (!data || data.length < 3) return []

    const angleStep = (Math.PI * 2) / data.length

    return data.map((point, index) => {
      const angle = angleStep * index - Math.PI / 2
      return {
        x1: center,
        y1: center,
        x2: center + radius * Math.cos(angle),
        y2: center + radius * Math.sin(angle),
        labelX: center + (radius + 25) * Math.cos(angle),
        labelY: center + (radius + 25) * Math.sin(angle),
        axis: point.axis,
        value: point.value,
      }
    })
  }, [data, center, radius])

  // Generate polygon path
  const polygonPath = useMemo(() => {
    if (points.length < 3) return ""
    return `${points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ")} Z`
  }, [points])

  // Generate level circles
  const levelCircles = useMemo(() => {
    const circles = []
    for (let i = 1; i <= levels; i++) {
      const levelRadius = (radius / levels) * i
      circles.push(levelRadius)
    }
    return circles
  }, [radius])

  if (!data || data.length < 3) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center">
            需要至少 3 个数据点来渲染雷达图
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {title && (
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className="flex flex-col items-center">
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="overflow-visible"
        >
          {/* Background circles (levels) */}
          {levelCircles.map((r, i) => (
            <circle
              key={i}
              cx={center}
              cy={center}
              r={r}
              fill="none"
              stroke="currentColor"
              strokeOpacity={0.1}
              strokeWidth={1}
            />
          ))}

          {/* Axis lines */}
          {axes.map((axis, i) => (
            <line
              key={i}
              x1={axis.x1}
              y1={axis.y1}
              x2={axis.x2}
              y2={axis.y2}
              stroke="currentColor"
              strokeOpacity={0.2}
              strokeWidth={1}
            />
          ))}

          {/* Data polygon */}
          <path
            d={polygonPath}
            fill={fillColor}
            stroke={strokeColor}
            strokeWidth={2}
          />

          {/* Data points */}
          {points.map((point, i) => (
            <circle
              key={i}
              cx={point.x}
              cy={point.y}
              r={4}
              fill={strokeColor}
            />
          ))}

          {/* Axis labels */}
          {showLabels &&
            axes.map((axis, i) => (
              <text
                key={i}
                x={axis.labelX}
                y={axis.labelY}
                textAnchor="middle"
                dominantBaseline="middle"
                className="fill-current text-xs font-medium"
              >
                {axis.axis}
              </text>
            ))}
        </svg>

        {/* Value legend */}
        {showValues && (
          <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
            {data.map((point, i) => (
              <div key={i} className="flex items-center justify-between gap-2">
                <span className="text-muted-foreground">{point.axis}</span>
                <span className="font-semibold tabular-nums">
                  {point.value.toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
