#!/usr/bin/env python3
"""
Main API Server Entry Point
This is the entry point that starts the Flask application using the modular app factory.
"""

import os
import sys
import logging
from hovel_server.app_factory import create_app
from hovel_server.core.utils import initialize_branch_system

# Get logger
logger = logging.getLogger(__name__)

def main():
    """Main function to run the server"""
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Initialize the branch system
    initialize_branch_system()
    
    # Create the Flask app using the factory
    app = create_app()
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 