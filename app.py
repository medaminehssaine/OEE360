from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
import pandas as pd
import numpy as np
import logging
from datetime import datetime

app = Flask(__name__)
app.config['DATASET_FOLDER'] = os.path.join(os.getcwd(), 'data', 'datasets')
app.config['MODEL_FOLDER'] = os.path.join(os.getcwd(), 'data', 'models')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Ensure directories exist
os.makedirs(app.config['DATASET_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate file types
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Dataset routes
@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    try:
        datasets = []
        for file in os.listdir(app.config['DATASET_FOLDER']):
            if file.endswith('.csv') or file.endswith('.json'):
                file_path = os.path.join(app.config['DATASET_FOLDER'], file)
                stats = os.stat(file_path)
                datasets.append({
                    'id': file,
                    'name': file,
                    'size': stats.st_size,
                    'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    'type': file.rsplit('.', 1)[1]
                })
        return jsonify({'datasets': datasets})
    except Exception as e:
        logger.error(f"Error reading datasets: {e}")
        return jsonify({'error': 'Failed to read datasets'}), 500

@app.route('/api/datasets', methods=['POST'])
def upload_dataset():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ['csv', 'json']):
            return jsonify({'error': 'Invalid file type. Only CSV and JSON files are allowed.'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['DATASET_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error uploading dataset: {e}")
        return jsonify({'error': 'Failed to upload dataset'}), 500

@app.route('/api/datasets/<id>', methods=['GET'])
def get_dataset(id):
    try:
        file_path = os.path.join(app.config['DATASET_FOLDER'], id)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Dataset not found'}), 404
        
        if id.endswith('.csv'):
            df = pd.read_csv(file_path)
            data = df.to_dict('records')
        elif id.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        return jsonify({'data': data, 'filename': id})
    except Exception as e:
        logger.error(f"Error reading dataset: {e}")
        return jsonify({'error': 'Failed to read dataset'}), 500

@app.route('/api/datasets/<id>', methods=['DELETE'])
def delete_dataset(id):
    try:
        file_path = os.path.join(app.config['DATASET_FOLDER'], id)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Dataset not found'}), 404
        
        os.remove(file_path)
        return jsonify({'message': 'Dataset deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting dataset: {e}")
        return jsonify({'error': 'Failed to delete dataset'}), 500

# Model routes
@app.route('/api/models', methods=['GET'])
def get_models():
    try:
        models = []
        for file in os.listdir(app.config['MODEL_FOLDER']):
            file_path = os.path.join(app.config['MODEL_FOLDER'], file)
            stats = os.stat(file_path)
            
            # Check if there's a metadata file
            metadata = {}
            metadata_path = os.path.join(app.config['MODEL_FOLDER'], f"{file}.metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            models.append({
                'id': file,
                'name': file,
                'size': stats.st_size,
                'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'type': file.rsplit('.', 1)[1] if '.' in file else 'unknown',
                'description': metadata.get('description', ''),
                'accuracy': metadata.get('accuracy', None),
                'version': metadata.get('version', '1.0')
            })
        return jsonify({'models': models})
    except Exception as e:
        logger.error(f"Error reading models: {e}")
        return jsonify({'error': 'Failed to read models'}), 500

@app.route('/api/models', methods=['POST'])
def upload_model():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['MODEL_FOLDER'], filename)
        file.save(file_path)
        
        # Save metadata if provided
        if 'metadata' in request.form:
            metadata = json.loads(request.form['metadata'])
            metadata_path = os.path.join(app.config['MODEL_FOLDER'], f"{filename}.metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
        
        return jsonify({'message': 'Model uploaded successfully', 'filename': filename})
    except Exception as e:
        logger.error(f"Error uploading model: {e}")
        return jsonify({'error': 'Failed to upload model'}), 500

@app.route('/api/models/<id>', methods=['DELETE'])
def delete_model(id):
    try:
        file_path = os.path.join(app.config['MODEL_FOLDER'], id)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Model not found'}), 404
        
        os.remove(file_path)
        
        # Remove metadata if exists
        metadata_path = os.path.join(app.config['MODEL_FOLDER'], f"{id}.metadata.json")
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            
        return jsonify({'message': 'Model deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting model: {e}")
        return jsonify({'error': 'Failed to delete model'}), 500

# Analytics route
@app.route('/api/analytics', methods=['POST'])
def run_analytics():
    try:
        data = request.json
        dataset_id = data.get('datasetId')
        model_id = data.get('modelId')
        analysis_type = data.get('analysisType')
        
        if not dataset_id or not model_id:
            return jsonify({'error': 'Dataset ID and Model ID are required'}), 400
        
        dataset_path = os.path.join(app.config['DATASET_FOLDER'], dataset_id)
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_id)
        
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Dataset not found'}), 404
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model not found'}), 404
        
        # Load dataset
        if dataset_id.endswith('.csv'):
            df = pd.read_csv(dataset_path)
            dataset = df.to_dict('records')
        elif dataset_id.endswith('.json'):
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
        else:
            return jsonify({'error': 'Unsupported dataset format'}), 400
        
        # Perform analytics (simplified version)
        analytics_results = perform_basic_analytics(dataset, analysis_type)
        
        return jsonify({
            'success': True,
            'datasetId': dataset_id,
            'modelId': model_id,
            'analysisType': analysis_type,
            'results': analytics_results
        })
    except Exception as e:
        logger.error(f"Error performing analytics: {e}")
        return jsonify({'error': 'Failed to perform analytics'}), 500

def perform_basic_analytics(data, analysis_type):
    # This is a simplified analytics function
    # In a real implementation, you would load and use the model here
    results = {
        'rowCount': len(data),
        'timestamp': datetime.now().isoformat(),
        'analysisType': analysis_type,
        'summary': {}
    }
    
    # Calculate basic statistics for numeric columns
    if len(data) > 0:
        numeric_columns = []
        for key in data[0].keys():
            try:
                float(data[0][key])
                numeric_columns.append(key)
            except (ValueError, TypeError):
                pass
        
        for column in numeric_columns:
            values = []
            for row in data:
                try:
                    values.append(float(row[column]))
                except (ValueError, TypeError):
                    pass
            
            if values:
                results['summary'][column] = {
                    'mean': np.mean(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'count': len(values)
                }
    
    return results

if __name__ == '__main__':
    app.run(debug=True, port=5000)
