# Hovel

A development environment API that spins up an AI agent-powered workspace, featuring an embeddable web terminal interface for seamless integration into web applications.

## Overview

Hovel is a Flask-based API server that provides a complete development environment management system. It includes advanced branch management capabilities that allow you to create isolated development environments for different features or experiments, with full Docker integration for automatic containerization.

## Features

- **Main API Server**: Flask-based REST API with comprehensive endpoints
- **Branch Management System**: Create isolated development environments for different features
- **Docker Integration**: Full Docker support with automatic containerization and Docker-in-Docker support
- **Git Integration**: Automatic git branch creation and management
- **Environment Isolation**: Each branch runs on its own port with complete environment isolation
- **Automatic Container Management**: Start, stop, and monitor Docker containers for each branch
- **External Template System**: Use external template directories for app duplication (no need to keep app directory in repo)
- **Web Terminal Interface**: Embeddable terminal for web applications

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git (optional, for branch management)

### Running with Docker

```bash
# Clone the repository
git clone <repository-url>
cd hovel

# Start the main API server with Docker-in-Docker support
docker-compose up
```

The API will be available at `http://localhost:8000`

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

## API Endpoints

### Core Endpoints

- `GET /` - Server information and status
- `GET /health` - Health check endpoint
- `GET /api/status` - API status and available endpoints

### Branch Management Endpoints

- `POST /api/branch` - Create a new development branch
  ```json
  {
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }
  ```
  **Note:** A valid Gemini API key is required for branch creation. Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey).
- `GET /api/branches` - List all created branches
- `POST /api/branch/{branch_name}/start` - Start Docker container for a branch
- `POST /api/branch/{branch_name}/stop` - Stop Docker container for a branch
- `GET /api/branch/{branch_name}/status` - Get branch container status
- `GET /api/branch/{branch_name}/logs` - Get branch container logs
- `POST /api/branch/{branch_name}/restart` - Restart branch container

## Docker Integration

### Docker-in-Docker Support

The orchestrator container includes Docker-in-Docker (DinD) support, allowing it to:

- **Automatically start cloned dev environments** when creating new branches
- **Manage multiple isolated containers** for different development branches
- **Monitor container status and logs** through the API
- **Start/stop/restart containers** on demand

### Container Management

Each branch gets its own Docker container with:

- **Unique port assignment** (8001, 8002, 8003, etc.)
- **Isolated environment** with its own dependencies
- **Automatic startup** when `auto_start: true` is specified
- **Health monitoring** and log access

### Example Usage

```bash
# Create a branch with auto-start
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'

# Check branch status
curl http://localhost:8000/api/branch/feature-new-ui/status

# Get branch logs
curl http://localhost:8000/api/branch/feature-new-ui/logs

# Stop branch container
curl -X POST http://localhost:8000/api/branch/feature-new-ui/stop

# Start branch container
curl -X POST http://localhost:8000/api/branch/feature-new-ui/start
```

## External Template System

### Overview

Hovel now supports external template directories, allowing you to keep your app templates outside the main repository. This provides better separation of concerns and makes template management more flexible.

### Setup

1. **Copy your current app directory to the external template location:**
   ```bash
   python setup_template_directory.py
   ```

2. **Restart your Docker container to pick up the new template path:**
   ```bash
   docker-compose down
   docker-compose up
   ```

3. **Test the functionality:**
   ```bash
   python test_template_functionality.py
   ```

4. **Remove the local app directory (optional):**
   ```bash
   python setup_template_directory.py --remove-local
   ```

### Configuration

The system uses the `APP_TEMPLATE_PATH` environment variable to locate templates:
- **Default**: `/opt/hovel-templates/app-template`
- **Custom**: Set `APP_TEMPLATE_PATH` to your preferred location

### Benefits

- ✅ **Clean separation**: Templates are independent of the orchestrator repo
- ✅ **Easy updates**: Update templates without touching the main repo
- ✅ **Multiple templates**: Support different app types and frameworks
- ✅ **Version control**: Templates can be in their own repositories
- ✅ **Team collaboration**: Multiple developers can contribute to templates

## Project Structure

```
hovel/
├── server.py                    # Entry point (simplified, modular)
├── server_old.py               # Original monolithic server (backup)
├── hovel_server/               # New modular package
│   ├── api/                    # Flask route handlers (blueprints)
│   │   ├── status.py          # Health, status, root endpoints
│   │   └── branch.py          # Branch management endpoints
│   ├── core/                   # Business logic (no Flask dependencies)
│   │   ├── utils.py           # Filesystem tracking, port management
│   │   ├── branch.py          # Branch creation and management
│   │   ├── docker.py          # Docker container operations
│   │   ├── git.py             # Git branch operations
│   │   └── gemini.py          # Gemini API integration
│   ├── app_factory.py         # Flask app factory
│   ├── config.py              # App configuration
│   ├── logging_config.py      # Logging setup
│   └── middleware.py          # Request/response logging & error handlers
├── app/                        # Main application directory (can be removed after setup)
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── docker-compose.branch.template.yaml
├── branches/                   # Branch environments (created dynamically)
├── docs/                       # Documentation
│   ├── BRANCH_README.md       # Branch management documentation
│   ├── GEMINI_CLI.md          # Gemini CLI integration guide
│   └── POSTMAN_SETUP.md       # Postman collection setup guide
├── .gemini/                    # Gemini CLI configuration
│   ├── settings.json          # Main configuration (gitignored)
│   └── settings.template.json # Template configuration
├── memory-bank/                # AI Agent Knowledge Base
│   ├── python-environment-troubleshooting.md
│   ├── flask-server-startup-guide.md
│   └── project-plan-comprehensive.md
├── setup_template_directory.py # Template setup script
├── test_template_functionality.py # Template functionality test script
├── run_branch.py              # Branch runner script
├── test_branch_system.py      # System test script
├── test_filesystem_tracking.py # Filesystem tracking test script
├── test_docker_functionality.py # Docker functionality test script
├── create_branch_compose.py   # Docker Compose generator
├── docker-compose.yaml        # Main Docker Compose with DinD support
├── docker-compose.branch.template.yaml
├── Dockerfile                 # Docker configuration with Docker installation
├── requirements.txt           # Python dependencies
├── Hovel_API_Collection.json  # Postman collection for API testing
└── README.md                  # This file
```

**External Template Directory:**
```
/opt/hovel-templates/
└── app-template/              # External template directory
    ├── app.js                # Express.js application
    ├── package.json          # Node.js dependencies
    ├── Dockerfile            # Container configuration
    └── docker-compose.branch.template.yaml # Docker Compose template
```

## Modular Architecture

The server has been refactored into a well-organized, modular package structure for improved maintainability and scalability:

### Key Benefits
- **🧩 Modular Design**: Each module has a single responsibility
- **🧪 Testability**: Core logic can be tested without Flask dependencies
- **🔧 Maintainability**: Easier to locate and fix issues
- **📈 Scalability**: Easy to add new features and endpoints
- **👥 Team Development**: Multiple developers can work on different modules
- **🧠 Reduced Context**: Smaller files are easier to understand

### Module Responsibilities
- **API Layer** (`hovel_server/api/`): Only handles HTTP requests/responses
- **Core Layer** (`hovel_server/core/`): Pure business logic, no Flask dependencies
- **Infrastructure**: Configuration, logging, middleware, app factory

## Development

### Creating a New Branch with Auto-Start

```bash
# Create a new development branch with automatic container startup
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'

# The branch will be created and its Docker container will start automatically
```

### Testing Docker Functionality

```bash
# Run the Docker functionality test suite
python test_docker_functionality.py

# Run the general system test suite
python test_branch_system.py
```

## Configuration

### Environment Variables

- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_APP` - Flask application entry point
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Docker Configuration

The project includes Docker support with:
- **Docker-in-Docker (DinD)** for container management
- **Privileged mode** for Docker daemon access
- **Socket mounting** for Docker communication
- **Multi-stage builds** for optimization
- **Git installation** for branch management
- **Volume mounting** for development
- **Environment variable configuration**

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes: `python test_docker_functionality.py`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please refer to the documentation in the [docs/](docs/) directory or create an issue in the repository.
