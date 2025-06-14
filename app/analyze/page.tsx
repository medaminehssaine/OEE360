'use client'

import { useState } from 'react'
import { DataModelSelector } from '@/components/DataModelSelector'
import { ApiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function AnalyzePage() {
  const [datasetId, setDatasetId] = useState<string>('')
  const [modelId, setModelId] = useState<string>('')
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const handleSelection = async (selectedDatasetId: string, selectedModelId: string) => {
    setDatasetId(selectedDatasetId)
    setModelId(selectedModelId)
    
    try {
      setLoading(true)
      setError('')
      
      const apiClient = new ApiClient()
      const analysisResults = await apiClient.runAnalytics({
        datasetId: selectedDatasetId,
        modelId: selectedModelId,
        analysisType: 'basic' // You can extend this to allow selecting analysis types
      })
      
      setResults(analysisResults)
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Data Analysis</h1>
      
      {!datasetId || !modelId ? (
        <DataModelSelector onSelect={handleSelection} />
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Analysis Results</h2>
            <button 
              className="text-blue-500 hover:underline"
              onClick={() => {
                setDatasetId('')
                setModelId('')
                setResults(null)
              }}
            >
              Choose Different Data
            </button>
          </div>
          
          {loading && <div className="text-center py-8">Running analysis...</div>}
          
          {error && <div className="text-red-500 p-4 border border-red-300 bg-red-50 rounded">{error}</div>}
          
          {results && (
            <Card>
              <CardHeader>
                <CardTitle>
                  Analysis of {datasetId} using {modelId}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-100 p-4 rounded overflow-auto">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}