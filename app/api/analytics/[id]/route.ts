import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

const MODELS_DIR = path.join(process.cwd(), 'data', 'models')

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const filePath = path.join(MODELS_DIR, params.id)
    
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'Model not found' }, { status: 404 })
    }

    // Try to read metadata
    const metadataPath = path.join(MODELS_DIR, `${path.parse(params.id).name}_metadata.json`)
    let metadata = {}
    if (fs.existsSync(metadataPath)) {
      try {
        metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'))
      } catch (error) {
        console.warn('Failed to read metadata:', error)
      }
    }

    const stats = fs.statSync(filePath)

    return NextResponse.json({ 
      id: params.id,
      name: params.id,
      size: stats.size,
      lastModified: stats.mtime,
      type: path.extname(params.id).slice(1),
      ...metadata
    })
  } catch (error) {
    console.error('Error reading model:', error)
    return NextResponse.json({ error: 'Failed to read model' }, { status: 500 })
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const filePath = path.join(MODELS_DIR, params.id)
    
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'Model not found' }, { status: 404 })
    }

    fs.unlinkSync(filePath)

    // Also delete metadata if it exists
    const metadataPath = path.join(MODELS_DIR, `${path.parse(params.id).name}_metadata.json`)
    if (fs.existsSync(metadataPath)) {
      fs.unlinkSync(metadataPath)
    }

    return NextResponse.json({ message: 'Model deleted successfully' })
  } catch (error) {
    console.error('Error deleting model:', error)
    return NextResponse.json({ error: 'Failed to delete model' }, { status: 500 })
  }
}