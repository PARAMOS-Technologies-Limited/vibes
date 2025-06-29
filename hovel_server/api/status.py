from flask import Blueprint, jsonify
from datetime import datetime

status_bp = Blueprint('status', __name__)

@status_bp.route('/')
def root():
    return jsonify({
        'message': 'Welcome to the Main API Server!',
        'server': 'server.py',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    })

@status_bp.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'main-api-server',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime': 'running'
    })

@status_bp.route('/api/status')
def api_status():
    return jsonify({
        'api_status': 'operational',
        'endpoints': [
            '/',
            '/health',
            '/api/status',
            '/api/branch',
            '/api/branches',
            '/api/branch/{branch_name}/start',
            '/api/branch/{branch_name}/stop',
            '/api/branch/{branch_name}/status',
            '/api/branch/{branch_name}/logs',
            '/api/branch/{branch_name}/restart',
            '/api/branch/{branch_name} (DELETE)'
        ],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }) 