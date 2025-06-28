#!/usr/bin/env python3
"""
Main API Server
This is the primary server file that handles the API endpoints and business logic.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    logger.info(f"Response: {response.status_code}")
    return response

@app.route('/')
def root():
    """Root endpoint with server information"""
    return jsonify({
        'message': 'Welcome to the Main API Server!',
        'server': 'server.py',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'main-api-server',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime': 'running'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_status': 'operational',
        'endpoints': [
            '/',
            '/health',
            '/api/status',
            '/api/data',
            '/api/process'
        ],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get sample data"""
    return jsonify({
        'data': [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300}
        ],
        'count': 3,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/process', methods=['POST'])
def process_data():
    """Process incoming data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process the data (example processing)
        processed_data = {
            'received': data,
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'success'
        }
        
        logger.info(f"Processed data: {data}")
        return jsonify(processed_data), 200
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 500

def main():
    """Main function to run the server"""
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 