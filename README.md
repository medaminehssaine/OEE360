# OEE360 - Data Analytics Platform

OEE360 is a comprehensive data analytics platform that allows users to upload datasets, manage models, and perform various types of analysis. The application features both a modern web interface built with Next.js and a powerful Python Flask backend for data processing.

## Features

- **Dataset Management**
  - Upload CSV and JSON datasets
  - Browse and manage your datasets
  - Real-time dataset preview
  
- **Model Management**
  - Upload models (JSON, PKL, JOBLIB formats)
  - Track model metadata and performance metrics
  - Use predefined models (SARIMA, LSTM, GRU) or upload custom models

- **Data Analysis**
  - Analyze datasets using selected models
  - Generate forecasts with configurable parameters
  - Visualize analysis results

- **Real-time Analytics**
  - Toggle between static and live data analysis
  - Adjust forecast horizon and lookback window parameters

## Technology Stack

### Frontend

- Next.js (React framework)
- TypeScript
- Shadcn UI components
- Embla Carousel

### Backend

- Flask (Python)
- Pandas for data processing
- NumPy for numerical operations

## Project Structure

``` bash
├── app/                      # Next.js application
│   ├── analyze/              # Analysis page
│   ├── api/                  # Next.js API routes
│       ├── datasets/         # Dataset management API
│       ├── models/           # Model management API
├── components/               # React components
│   ├── ui/                   # UI components
│   ├── DataModelSelector.tsx # Dataset and model selection component
├── data/                     # Data storage
│   ├── datasets/             # Stored datasets
│   ├── models/               # Stored models
├── lib/                      # Helper functions
├── scripts/                  # Python scripts
│   ├── generate_datasets.py  # Generate sample datasets
│   ├── train_models.py       # Train sample models
├── app.py                    # Flask backend
```

## Installation

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- npm or yarn

### Setup

1. Clone the repository

   ```bash
   git clone https://github.com/medaminehssaine/OEE360.git
   cd OEE360
   ```

2. Install frontend dependencies

   ```bash
   npm install
   ```

3. Create Python virtual environment

   ```bash
   # Create virtual environment
   python -m venv env
   
   # Activate virtual environment (Windows)
   env\Scripts\activate.bat
   # OR for Mac/Linux:
   # source env/bin/activate
   ```

4. Install Python packages

   ```bash
   pip install -r requirements.txt
   ```

5. Generate sample datasets and train models

   ```bash
   python scripts/generate_datasets.py
   python scripts/train_models.py
   ```

## Usage

1. Start the Flask backend

   ```bash
   python app.py
   ```

2. In a separate terminal, start the Next.js development server

   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3000`

## API Documentation

### Dataset API

- `GET /api/datasets` - List all datasets
- `POST /api/datasets` - Upload a new dataset
- `GET /api/datasets/:id` - Get a specific dataset
- `DELETE /api/datasets/:id` - Delete a dataset

### Model API

- `GET /api/models` - List all models
- `POST /api/models` - Upload a new model
- `DELETE /api/models/:id` - Delete a model

### Analytics API

- `POST /api/analytics` - Run analysis with selected dataset and model

## Development

### Adding New Features

1. Backend Features:
   - Add new routes to `app.py`
   - Create corresponding API endpoints in Next.js API routes

2. Frontend Features:
   - Add new pages in the `app` directory
   - Create components in the `components` directory

### Running Tests

```bash
# Run frontend tests
npm test

# Run backend tests
python -m pytest
```
