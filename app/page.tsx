"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { DynamicValue } from "@/components/DynamicValue"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  ComposedChart,
} from "recharts"
import {
  Factory,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  Zap,
  CheckCircle,
  AlertTriangle,
  Settings,
  Wrench,
  RefreshCw,
  Play,
  Pause,
} from "lucide-react"
import { DataModelSelector } from "@/components/DataModelSelector"
import { ApiClient } from "@/lib/api"

// Generate comprehensive sample data
const generateOEEData = () => {
  const data = []
  const now = new Date()

  for (let i = 168; i >= 0; i--) {
    // 7 days of hourly data
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000)
    const hour = timestamp.getHours()
    const dayOfWeek = timestamp.getDay()

    // Shift patterns
    const shift = hour < 8 ? "Night" : hour < 16 ? "Day" : "Evening"
    const shiftFactor = shift === "Day" ? 1.0 : shift === "Evening" ? 0.92 : 0.85

    // Weekly patterns
    const weeklyFactor = dayOfWeek === 0 || dayOfWeek === 6 ? 0.9 : 1.0

    // Generate correlated metrics with realistic patterns
    const availability = Math.max(0.5, Math.min(0.98, 0.85 * shiftFactor * weeklyFactor + (Math.random() - 0.5) * 0.1))
    const performance = Math.max(0.4, Math.min(0.95, 0.8 * shiftFactor + (Math.random() - 0.5) * 0.15))
    const quality = Math.max(0.7, Math.min(0.99, 0.9 * shiftFactor + (Math.random() - 0.5) * 0.08))

    const oee = availability * performance * quality

    // Environmental factors
    const temp = 20 + Math.sin(i / 24) * 5 + (Math.random() - 0.5) * 6
    const humidity = 45 + Math.sin((i + 12) / 24) * 10 + (Math.random() - 0.5) * 10
    const energyPrice = 0.12 + Math.sin((hour / 24) * Math.PI * 2) * 0.03 + (Math.random() - 0.5) * 0.02

    // Worker fatigue
    const shiftHour = hour % 8
    const fatigue = Math.max(0, Math.min(1, 0.1 + (shiftHour / 8) * 0.4 + (Math.random() - 0.5) * 0.2))

    // Downtime
    const downtime = Math.random() < 0.05 ? Math.random() * 2 : 0

    data.push({
      timestamp,
      hour: i,
      time: timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      date: timestamp.toLocaleDateString(),
      OEE: oee,
      availability,
      performance,
      quality,
      shift,
      temp,
      humidity,
      energy_price: energyPrice,
      fatigue,
      downtime,
      // Predicted values (simple trend + noise)
      predicted_oee: Math.max(0.3, Math.min(1.0, oee + (Math.random() - 0.5) * 0.1)),
    })
  }

  return data
}

// Statistical functions
const calculateTrend = (data: any[], key: string) => {
  if (data.length < 2) return 0
  const recent = data.slice(-6).map((d) => d[key])
  const older = data.slice(-12, -6).map((d) => d[key])
  const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length
  const olderAvg = older.reduce((a, b) => a + b, 0) / older.length
  return ((recentAvg - olderAvg) / olderAvg) * 100
}

const calculateCorrelation = (x: number[], y: number[]) => {
  const n = x.length
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = y.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0)

  const numerator = n * sumXY - sumX * sumY
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))

  return denominator === 0 ? 0 : numerator / denominator
}

export default function Home() {
  const [data, setData] = useState(generateOEEData())
  const [isLive, setIsLive] = useState(false)
  const [selectedVariables, setSelectedVariables] = useState(["OEE", "availability", "performance", "quality"])
  const [chartType, setChartType] = useState("line")
  const [dateRange, setDateRange] = useState("7d")
  const [forecastHorizon, setForecastHorizon] = useState([24])
  const [lookbackWindow, setLookbackWindow] = useState([24])
  const [modelType, setModelType] = useState("LSTM")
  
  // New state variables
  const [datasetId, setDatasetId] = useState<string>("")
  const [modelId, setModelId] = useState<string>("")
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [analysisLoading, setAnalysisLoading] = useState<boolean>(false)
  const [analysisError, setAnalysisError] = useState<string>("")
  const [showDataSelector, setShowDataSelector] = useState<boolean>(false)

  // Live data simulation
  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      setData((prevData) => {
        const newData = [...prevData.slice(1)]
        const lastPoint = prevData[prevData.length - 1]
        const now = new Date()

        // Generate new data point with some continuity
        const newPoint = {
          ...lastPoint,
          timestamp: now,
          time: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          OEE: Math.max(0.3, Math.min(1.0, lastPoint.OEE + (Math.random() - 0.5) * 0.05)),
          availability: Math.max(0.5, Math.min(0.98, lastPoint.availability + (Math.random() - 0.5) * 0.03)),
          performance: Math.max(0.4, Math.min(0.95, lastPoint.performance + (Math.random() - 0.5) * 0.04)),
          quality: Math.max(0.7, Math.min(0.99, lastPoint.quality + (Math.random() - 0.5) * 0.02)),
        }

        newData.push(newPoint)
        return newData
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [isLive])

  // Filter data based on date range
  const filteredData = useMemo(() => {
    const hours = dateRange === "24h" ? 24 : dateRange === "7d" ? 168 : 720 // 30d
    return data.slice(-hours)
  }, [data, dateRange])

  // Calculate metrics
  const currentMetrics = useMemo(() => {
    const latest = filteredData[filteredData.length - 1]
    if (!latest) return null

    return {
      oee: latest.OEE,
      availability: latest.availability,
      performance: latest.performance,
      quality: latest.quality,
      oee_trend: calculateTrend(filteredData, "OEE"),
      availability_trend: calculateTrend(filteredData, "availability"),
      performance_trend: calculateTrend(filteredData, "performance"),
      quality_trend: calculateTrend(filteredData, "quality"),
    }
  }, [filteredData])

  // Calculate correlations
  const correlations = useMemo(() => {
    const variables = ["OEE", "availability", "performance", "quality", "temp", "humidity", "energy_price", "fatigue"]
    const matrix: { [key: string]: { [key: string]: number } } = {}

    variables.forEach((var1) => {
      matrix[var1] = {}
      variables.forEach((var2) => {
        const x = filteredData.map((d) => d[var1])
        const y = filteredData.map((d) => d[var2])
        matrix[var1][var2] = calculateCorrelation(x, y)
      })
    })

    return matrix
  }, [filteredData])

  // Generate recommendations
  const recommendations = useMemo(() => {
    if (!currentMetrics) return []

    const recs = []

    if (currentMetrics.availability < 0.8) {
      recs.push({
        type: "maintenance",
        priority: "high",
        title: "Schedule Preventive Maintenance",
        description: "Availability is below 80%. Consider scheduling maintenance to prevent unplanned downtime.",
        impact: "Could improve availability by 8-12%",
      })
    }

    if (currentMetrics.performance < 0.75) {
      recs.push({
        type: "optimization",
        priority: "medium",
        title: "Optimize Machine Settings",
        description: "Performance metrics indicate potential for speed optimization.",
        impact: "Expected 5-8% performance improvement",
      })
    }

    if (currentMetrics.quality < 0.85) {
      recs.push({
        type: "quality",
        priority: "high",
        title: "Review Quality Parameters",
        description: "Quality rate below target. Check calibration and process parameters.",
        impact: "Reduce defect rate by 3-5%",
      })
    }

    if (currentMetrics.oee_trend < -2) {
      recs.push({
        type: "alert",
        priority: "critical",
        title: "Declining OEE Trend Detected",
        description: `OEE has declined by ${Math.abs(currentMetrics.oee_trend).toFixed(1)}% recently.`,
        impact: "Prevent further degradation",
      })
    }

    return recs
  }, [currentMetrics])

  const renderChart = () => {
    const chartData = filteredData.map((d) => ({
      ...d,
      time: d.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      OEE: d.OEE * 100,
      availability: d.availability * 100,
      performance: d.performance * 100,
      quality: d.quality * 100,
      predicted_oee: d.predicted_oee * 100,
    }))

    const colors = {
      OEE: "#3b82f6",
      availability: "#8b5cf6",
      performance: "#06b6d4",
      quality: "#10b981",
      predicted_oee: "#f59e0b",
    }

    switch (chartType) {
      case "area":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f9fafb",
                }}
              />
              {selectedVariables.map((variable, index) => (
                <Area
                  key={variable}
                  type="monotone"
                  dataKey={variable}
                  stackId="1"
                  stroke={colors[variable as keyof typeof colors]}
                  fill={colors[variable as keyof typeof colors]}
                  fillOpacity={0.6}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        )

      case "bar":
        const dailyData = chartData.reduce((acc: any[], curr) => {
          const date = curr.timestamp.toLocaleDateString()
          const existing = acc.find((d) => d.date === date)
          if (existing) {
            selectedVariables.forEach((variable) => {
              existing[variable] = (existing[variable] + curr[variable]) / 2
            })
          } else {
            const newEntry: any = { date }
            selectedVariables.forEach((variable) => {
              newEntry[variable] = curr[variable]
            })
            acc.push(newEntry)
          }
          return acc
        }, [])

        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f9fafb",
                }}
              />
              {selectedVariables.map((variable) => (
                <Bar key={variable} dataKey={variable} fill={colors[variable as keyof typeof colors]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )

      case "scatter":
        if (selectedVariables.length >= 2) {
          return (
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey={selectedVariables[0]} stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                <YAxis dataKey={selectedVariables[1]} stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                    color: "#f9fafb",
                  }}
                />
                <Scatter dataKey={selectedVariables[1]} fill={colors[selectedVariables[0] as keyof typeof colors]} />
              </ScatterChart>
            </ResponsiveContainer>
          )
        }
        return (
          <div className="flex items-center justify-center h-96 text-gray-400">
            Select at least 2 variables for scatter plot
          </div>
        )

      default: // line chart
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1f2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                  color: "#f9fafb",
                }}
              />
              {selectedVariables.map((variable) => (
                <Line
                  key={variable}
                  type="monotone"
                  dataKey={variable}
                  stroke={colors[variable as keyof typeof colors]}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
              {selectedVariables.includes("OEE") && (
                <Line
                  type="monotone"
                  dataKey="predicted_oee"
                  stroke={colors.predicted_oee}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        )
    }
  }

  // New function to handle data and model selection
  const handleDataModelSelect = async (selectedDatasetId: string, selectedModelId: string) => {
    setDatasetId(selectedDatasetId)
    setModelId(selectedModelId)
    setShowDataSelector(false)
    
    try {
      setAnalysisLoading(true)
      setAnalysisError("")
      
      const apiClient = new ApiClient()
      const results = await apiClient.runAnalytics({
        datasetId: selectedDatasetId,
        modelId: selectedModelId,
        analysisType: "basic"
      })
      
      setAnalysisResults(results)
    } catch (err: any) {
      setAnalysisError(err.message || "An error occurred during analysis")
      console.error("Analysis error:", err)
    } finally {
      setAnalysisLoading(false)
    }
  }

  if (!currentMetrics) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-gray-900/60">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Factory className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">🏭 OEE Analytics Dashboard</h1>
                <p className="text-sm text-gray-400">Overall Equipment Effectiveness Analysis & Forecasting</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant={isLive ? "destructive" : "default"}
                onClick={() => setIsLive(!isLive)}
                className="flex items-center space-x-2"
              >
                {isLive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                <span>{isLive ? "Stop Live" : "Start Live"}</span>
              </Button>
              <Button variant="outline" onClick={() => setData(generateOEEData())}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Controls */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  Dashboard Controls
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-300 mb-2 block">Time Period</label>
                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger className="bg-gray-700 border-gray-600">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-gray-600">
                      <SelectItem value="24h">Last 24 Hours</SelectItem>
                      <SelectItem value="7d">Last 7 Days</SelectItem>
                      <SelectItem value="30d">Last 30 Days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-300 mb-2 block">Chart Type</label>
                  <Select value={chartType} onValueChange={setChartType}>
                    <SelectTrigger className="bg-gray-700 border-gray-600">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-700 border-gray-600">
                      <SelectItem value="line">Line Chart</SelectItem>
                      <SelectItem value="area">Area Chart</SelectItem>
                      <SelectItem value="bar">Bar Chart</SelectItem>
                      <SelectItem value="scatter">Scatter Plot</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-300 mb-3 block">Variables</label>
                  <div className="space-y-2">
                    {["OEE", "availability", "performance", "quality", "temp", "humidity"].map((variable) => (
                      <div key={variable} className="flex items-center space-x-2">
                        <Checkbox
                          id={variable}
                          checked={selectedVariables.includes(variable)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedVariables([...selectedVariables, variable])
                            } else {
                              setSelectedVariables(selectedVariables.filter((v) => v !== variable))
                            }
                          }}
                        />
                        <label htmlFor={variable} className="text-sm text-gray-300 capitalize">
                          {variable.replace("_", " ")}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator className="bg-gray-700" />

                <div>
                  <label className="text-sm font-medium text-gray-300 mb-2 block">Data & Model Selection</label>
                  <DataModelSelector 
                    onSelect={handleDataModelSelect} 
                    className="mb-4 bg-gray-700 p-3 rounded-md"
                  />
                </div>

                <div>
                  <label className="text-xs text-gray-400 mb-1 block">
                    Forecast Horizon: <DynamicValue value={forecastHorizon[0]} fallback="--" format={(val) => `${val}h`} />
                  </label>
                  <Slider
                    value={forecastHorizon}
                    onValueChange={setForecastHorizon}
                    max={168}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="text-xs text-gray-400 mb-1 block">
                    Lookback Window: <DynamicValue value={lookbackWindow[0]} fallback="--" format={(val) => `${val}h`} />
                  </label>
                  <Slider
                    value={lookbackWindow}
                    onValueChange={setLookbackWindow}
                    max={168}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-400">Average OEE</p>
                      <p className="text-2xl font-bold text-blue-400">
                        <DynamicValue 
                          value={currentMetrics.oee * 100} 
                          fallback="--"
                          format={(val) => `${val.toFixed(1)}%`}
                        />
                      </p>
                      <div className="flex items-center mt-1">
                        {currentMetrics.oee_trend > 0 ? (
                          <TrendingUp className="h-4 w-4 text-green-400 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400 mr-1" />
                        )}
                        <span className={`text-sm ${currentMetrics.oee_trend > 0 ? "text-green-400" : "text-red-400"}`}>
                          <DynamicValue 
                            value={currentMetrics.oee_trend} 
                            fallback="--"
                            format={(val) => `${val > 0 ? "+" : ""}${val.toFixed(1)}%`}
                          />
                        </span>
                      </div>
                    </div>
                    <Activity className="h-8 w-8 text-blue-400" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-400">Availability</p>
                      <p className="text-2xl font-bold text-purple-400">
                        <DynamicValue 
                          value={currentMetrics.availability * 100} 
                          fallback="--"
                          format={(val) => `${val.toFixed(1)}%`}
                        />
                      </p>
                      <div className="flex items-center mt-1">
                        {currentMetrics.availability_trend > 0 ? (
                          <TrendingUp className="h-4 w-4 text-green-400 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400 mr-1" />
                        )}
                        <span
                          className={`text-sm ${currentMetrics.availability_trend > 0 ? "text-green-400" : "text-red-400"}`}
                        >
                          <DynamicValue 
                            value={currentMetrics.availability_trend} 
                            fallback="--"
                            format={(val) => `${val > 0 ? "+" : ""}${val.toFixed(1)}%`}
                          />
                        </span>
                      </div>
                    </div>
                    <Clock className="h-8 w-8 text-purple-400" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-400">Performance</p>
                      <p className="text-2xl font-bold text-cyan-400">
                        <DynamicValue 
                          value={currentMetrics.performance * 100} 
                          fallback="--"
                          format={(val) => `${val.toFixed(1)}%`}
                        />
                      </p>
                      <div className="flex items-center mt-1">
                        {currentMetrics.performance_trend > 0 ? (
                          <TrendingUp className="h-4 w-4 text-green-400 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400 mr-1" />
                        )}
                        <span
                          className={`text-sm ${currentMetrics.performance_trend > 0 ? "text-green-400" : "text-red-400"}`}
                        >
                          <DynamicValue 
                            value={currentMetrics.performance_trend} 
                            fallback="--"
                            format={(val) => `${val > 0 ? "+" : ""}${val.toFixed(1)}%`}
                          />
                        </span>
                      </div>
                    </div>
                    <Zap className="h-8 w-8 text-cyan-400" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800 border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-400">Quality</p>
                      <p className="text-2xl font-bold text-green-400">
                        <DynamicValue 
                          value={currentMetrics.quality * 100} 
                          fallback="--"
                          format={(val) => `${val.toFixed(1)}%`}
                        />
                      </p>
                      <div className="flex items-center mt-1">
                        {currentMetrics.quality_trend > 0 ? (
                          <TrendingUp className="h-4 w-4 text-green-400 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400 mr-1" />
                        )}
                        <span
                          className={`text-sm ${currentMetrics.quality_trend > 0 ? "text-green-400" : "text-red-400"}`}
                        >
                          <DynamicValue 
                            value={currentMetrics.quality_trend} 
                            fallback="--"
                            format={(val) => `${val > 0 ? "+" : ""}${val.toFixed(1)}%`}
                          />
                        </span>
                      </div>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-400" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Chart */}
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">OEE Trend & Analysis</CardTitle>
                <CardDescription className="text-gray-400">
                  Real-time monitoring with predictive insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                {datasetId && modelId ? (
                  renderChart()
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-400">
                    Please select a dataset and model from the controls section to view analysis
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tabs for detailed analysis */}
            <Tabs defaultValue="analysis" className="w-full">
              <TabsList className="grid w-full grid-cols-4 bg-gray-800">
                <TabsTrigger value="analysis" className="data-[state=active]:bg-gray-700">
                  Analysis
                </TabsTrigger>
                <TabsTrigger value="correlations" className="data-[state=active]:bg-gray-700">
                  Correlations
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="data-[state=active]:bg-gray-700">
                  Recommendations
                </TabsTrigger>
                <TabsTrigger value="forecasting" className="data-[state=active]:bg-gray-700">
                  Forecasting
                </TabsTrigger>
              </TabsList>

              <TabsContent value="analysis" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-white text-lg">Shift Performance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart
                          data={[
                            { shift: "Day", oee: 82.5, availability: 88.2, performance: 85.1, quality: 91.3 },
                            { shift: "Evening", oee: 78.9, availability: 84.7, performance: 82.3, quality: 89.8 },
                            { shift: "Night", oee: 74.2, availability: 81.5, performance: 79.6, quality: 87.4 },
                          ]}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="shift" stroke="#9ca3af" />
                          <YAxis stroke="#9ca3af" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#1f2937",
                              border: "1px solid #374151",
                              borderRadius: "8px",
                              color: "#f9fafb",
                            }}
                          />
                          <Bar dataKey="oee" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  <Card className="bg-gray-800 border-gray-700">
                    <CardHeader>
                      <CardTitle className="text-white text-lg">Environmental Impact</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={200}>
                        <ScatterChart
                          data={filteredData.map((d) => ({
                            temp: d.temp,
                            oee: d.OEE * 100,
                            humidity: d.humidity,
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="temp" stroke="#9ca3af" />
                          <YAxis dataKey="oee" stroke="#9ca3af" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#1f2937",
                              border: "1px solid #374151",
                              borderRadius: "8px",
                              color: "#f9fafb",
                            }}
                          />
                          <Scatter dataKey="oee" fill="#10b981" />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="correlations" className="space-y-4">
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white">Correlation Matrix</CardTitle>
                    <CardDescription className="text-gray-400">
                      Relationships between different variables
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-6 gap-2 text-xs">
                      {Object.keys(correlations).map((var1) => (
                        <div key={var1} className="space-y-2">
                          <div className="font-medium text-gray-300 text-center">{var1}</div>
                          {Object.keys(correlations).map((var2) => (
                            <div
                              key={`${var1}-${var2}`}
                              className="h-8 flex items-center justify-center rounded text-white text-xs font-medium"
                              style={{
                                backgroundColor: `rgba(${correlations[var1][var2] > 0 ? "16, 185, 129" : "239, 68, 68"}, ${Math.abs(correlations[var1][var2])})`,
                              }}
                            >
                              <DynamicValue 
                                value={correlations[var1][var2]} 
                                fallback="--"
                                format={(val) => val.toFixed(2)}
                              />
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4">
                <div className="grid gap-4">
                  {recommendations.length > 0 ? (
                    recommendations.map((rec, index) => (
                      <Card key={index} className="bg-gray-800 border-gray-700">
                        <CardContent className="p-4">
                          <div className="flex items-start space-x-3">
                            <div
                              className={`p-2 rounded-full ${
                                rec.priority === "critical"
                                  ? "bg-red-900"
                                  : rec.priority === "high"
                                    ? "bg-orange-900"
                                    : rec.priority === "medium"
                                      ? "bg-yellow-900"
                                      : "bg-green-900"
                              }`}
                            >
                              {rec.type === "maintenance" ? (
                                <Wrench className="h-4 w-4" />
                              ) : rec.type === "optimization" ? (
                                <Settings className="h-4 w-4" />
                              ) : rec.type === "quality" ? (
                                <CheckCircle className="h-4 w-4" />
                              ) : (
                                <AlertTriangle className="h-4 w-4" />
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-white">{rec.title}</h4>
                                <Badge
                                  variant={
                                    rec.priority === "critical"
                                      ? "destructive"
                                      : rec.priority === "high"
                                        ? "destructive"
                                        : rec.priority === "medium"
                                          ? "secondary"
                                          : "default"
                                  }
                                >
                                  {rec.priority}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-300 mb-2">{rec.description}</p>
                              <p className="text-xs text-green-400 font-medium">{rec.impact}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <Card className="bg-gray-800 border-gray-700">
                      <CardContent className="p-8 text-center">
                        <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-400" />
                        <h3 className="font-medium text-white mb-2">All Systems Operating Optimally</h3>
                        <p className="text-sm text-gray-400">No recommendations at this time</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="forecasting" className="space-y-4">
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader>
                    <CardTitle className="text-white">OEE Forecasting</CardTitle>
                    <CardDescription className="text-gray-400">
                      {forecastHorizon[0]}-hour forecast using {modelType} model
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <Button className="w-full">Generate Forecast</Button>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart
                        data={filteredData.slice(-48).map((d) => ({
                          time: d.time,
                          actual: d.OEE * 100,
                          forecast: d.predicted_oee * 100,
                          upper: d.predicted_oee * 100 + 5,
                          lower: d.predicted_oee * 100 - 5,
                        }))}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
                        <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#1f2937",
                            border: "1px solid #374151",
                            borderRadius: "8px",
                            color: "#f9fafb",
                          }}
                        />
                        <Area dataKey="upper" fill="#3b82f6" fillOpacity={0.1} stroke="none" />
                        <Area dataKey="lower" fill="#3b82f6" fillOpacity={0.1} stroke="none" />
                        <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2} dot={false} />
                        <Line
                          type="monotone"
                          dataKey="forecast"
                          stroke="#f59e0b"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>

                    <div className="grid grid-cols-4 gap-4 mt-4">
                      <div className="text-center">
                        <p className="text-sm text-gray-400">Min Forecast</p>
                        <p className="text-lg font-bold text-white">
                          <DynamicValue value={68.2} fallback="--" format={(val) => `${val}%`} />
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-400">Max Forecast</p>
                        <p className="text-lg font-bold text-white">
                          <DynamicValue value={84.7} fallback="--" format={(val) => `${val}%`} />
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-400">Mean Forecast</p>
                        <p className="text-lg font-bold text-white">
                          <DynamicValue value={76.4} fallback="--" format={(val) => `${val}%`} />
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-sm text-gray-400">Trend</p>
                        <p className="text-lg font-bold text-green-400">
                          <DynamicValue value={2.1} fallback="--" format={(val) => `+${val}%`} />
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  )
}
