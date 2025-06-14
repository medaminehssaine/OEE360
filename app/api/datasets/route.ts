import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

const DATASETS_DIR = path.join(process.cwd(), 'data', 'datasets')

export async function GET(request: NextRequest) {
  try {
    // Ensure datasets directory exists
    if (!fs.existsSync(DATASETS_DIR)) {
      fs.mkdirSync(DATASETS_DIR, { recursive: true })
    }

    // Check if we're requesting a specific dataset
    const url = new URL(request.url)
    const id = url.searchParams.get('id')
    
    if (id) {
      // Return a specific dataset
      const filePath = path.join(DATASETS_DIR, id)
      
      if (!fs.existsSync(filePath)) {
        return NextResponse.json({ error: 'Dataset not found' }, { status: 404 })
      }
      
      const stats = fs.statSync(filePath)
      const fileContent = fs.readFileSync(filePath, 'utf-8')
      
      // Parse content based on file type
      let parsedData
      if (id.endsWith('.json')) {
        parsedData = JSON.parse(fileContent)
      } else if (id.endsWith('.csv')) {
        // For CSV, just return raw content (client can parse)
        parsedData = fileContent
      }
      
      return NextResponse.json({
        dataset: {
          id,
          name: id,
          size: stats.size,
          lastModified: stats.mtime,
          type: path.extname(id).slice(1),
          data: parsedData
        }
      })
    }

    const files = fs.readdirSync(DATASETS_DIR)
    const datasets = files
      .filter(file => file.endsWith('.csv') || file.endsWith('.json'))
      .map(file => {
        const filePath = path.join(DATASETS_DIR, file)
        const stats = fs.statSync(filePath)
        return {
          id: file,
          name: file,
          size: stats.size,
          lastModified: stats.mtime,
          type: path.extname(file).slice(1)
        }
      })

    return NextResponse.json({ datasets })
  } catch (error) {
    console.error('Error reading datasets:', error)
    return NextResponse.json({ error: 'Failed to read datasets' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Get optional metadata
    const metadataField = formData.get('metadata')
    let metadata = {}
    if (metadataField) {
      try {
        metadata = typeof metadataField === 'string' 
          ? JSON.parse(metadataField) 
          : metadataField
      } catch (e) {
        console.warn('Invalid metadata format, ignoring')
      }
    }

    // Validate file type
    const allowedTypes = ['.csv', '.json']
    const fileExtension = path.extname(file.name).toLowerCase()
    if (!allowedTypes.includes(fileExtension)) {
      return NextResponse.json({ 
        error: 'Invalid file type. Only CSV and JSON files are allowed.' 
      }, { status: 400 })
    }

    // Ensure datasets directory exists
    if (!fs.existsSync(DATASETS_DIR)) {
      fs.mkdirSync(DATASETS_DIR, { recursive: true })
    }

    // Generate a unique filename to prevent overwrites
    const timestamp = new Date().getTime()
    const uniqueFilename = `${path.basename(file.name, fileExtension)}_${timestamp}${fileExtension}`
    const filePath = path.join(DATASETS_DIR, uniqueFilename)
    
    const buffer = Buffer.from(await file.arrayBuffer())
    fs.writeFileSync(filePath, buffer)
    
    // Save metadata if provided
    if (Object.keys(metadata).length > 0) {
      const metadataPath = path.join(DATASETS_DIR, `${uniqueFilename}.metadata.json`)
      fs.writeFileSync(metadataPath, JSON.stringify(metadata))
    }

    return NextResponse.json({ 
      message: 'File uploaded successfully',
      filename: uniqueFilename,
      id: uniqueFilename,
      size: buffer.length,
      lastModified: new Date(),
      type: fileExtension.slice(1)
    })
  } catch (error) {
    console.error('Error uploading file:', error)
    return NextResponse.json({ error: 'Failed to upload file' }, { status: 500 })
  }
}