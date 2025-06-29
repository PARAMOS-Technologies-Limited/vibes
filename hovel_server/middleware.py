from flask import request, jsonify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_middleware(app):
    """Setup request/response logging and error handlers"""
    
    @app.before_request
    def log_request():
        """Log all incoming requests"""
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")

    @app.after_request
    def log_response(response):
        """Log all outgoing responses"""
        logger.info(f"Response: {response.status_code}")
        return response

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