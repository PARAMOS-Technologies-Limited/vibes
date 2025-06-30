# Hovel - Development Environment Orchestrator

A Flask-based API server that orchestrates development environments using Docker-in-Docker (DinD) technology. Create isolated branches of your application, each running in its own container with unique ports and complete environment isolation.

## Features

- **Branch Management**: Create isolated development branches via API
- **Docker-in-Docker**: Full container orchestration with DinD support
- **Service Selection**: Choose which Docker services to include and start
- **Automatic Port Assignment**: Each branch gets unique ports (8001, 8002, etc.)
- **Git Integration**: Automatic git branch creation and management
- **Gemini AI Integration**: Built-in Gemini CLI support with web terminals
- **External Templates**: Configurable template system for different app types
- **Background Tasks**: Asynchronous container building and management
- **Health Monitoring**: Real-time container status and log access

## Quick Start

### 1. Start the Orchestrator

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or directly with Python
python server.py
```

The orchestrator runs on port 8000.

### 2. Create Your First Branch

```bash
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "services": ["app", "database"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'
```

**Note:** A valid Gemini API key is required for branch creation. Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## API Endpoints

### Branch Management

- `POST /api/branch` - Create a new development branch
  ```json
  {
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "services": ["app", "database", "cache"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }
  ```
  **Services Parameter:** Specify which Docker services to include in the branch. If not specified, defaults to `["app"]` for backward compatibility.

- `GET /api/branches` - List all created branches
- `POST /api/branch/{branch_name}/start` - Start Docker container for a branch
  ```json
  {
    "services": ["app", "database"]
  }
  ```
  **Services Parameter:** Specify which services to start. If not provided, starts all services defined in the branch's Docker Compose file.

- `POST /api/branch/{branch_name}/stop` - Stop Docker container for a branch
- `GET /api/branch/{branch_name}/status` - Get branch container status
- `GET /api/branch/{branch_name}/logs` - Get branch container logs
- `POST /api/branch/{branch_name}/restart` - Restart branch container

## Service Selection

The new services parameter allows you to:

### During Branch Creation
- **Include specific services**: Only the specified services will be included in the branch's Docker Compose file
- **Filter templates**: The system will filter the Docker Compose template to include only the requested services
- **Backward compatibility**: If no services are specified, defaults to `["app"]`

### During Container Start
- **Start specific services**: Only start the specified services from the branch's Docker Compose file
- **Flexible startup**: Start all services by omitting the services parameter, or start specific ones by providing a list

### Example Usage

```bash
# Create branch with multiple services
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "full-stack-feature",
    "services": ["app", "database", "redis", "nginx"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'

# Start only specific services
curl -X POST http://localhost:8000/api/branch/full-stack-feature/start \
  -H "Content-Type: application/json" \
  -d '{
    "services": ["app", "database"]
  }'

# Start all services in the branch
curl -X POST http://localhost:8000/api/branch/full-stack-feature/start
```

## Docker Integration

### Docker-in-Docker Support

The orchestrator container includes Docker-in-Docker (DinD) support, allowing it to:

- **Automatically start cloned dev environments** when creating new branches
- **Manage multiple isolated containers** for different development branches
- **Monitor container status and logs** through the API
- **Start/stop/restart containers** on demand
- **Selectively start services** within each branch

### Container Management

Each branch gets its own Docker container with:

- **Unique port assignment** (8001, 8002, 8003, etc.)
- **Isolated environment** with its own dependencies
- **Automatic startup** when `auto_start: true` is specified
- **Health monitoring** and log access
- **Service-level control** for starting specific components

### Example Usage

```bash
# Create a branch with auto-start
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "services": ["app", "database"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'

# Check branch status
curl http://localhost:8000/api/branch/feature-new-ui/status

# Get branch logs
curl http://localhost:8000/api/branch/feature-new-ui/logs

# Stop branch container
curl -X POST http://localhost:8000/api/branch/feature-new-ui/stop

# Start specific services
curl -X POST http://localhost:8000/api/branch/feature-new-ui/start \
  -H "Content-Type: application/json" \
  -d '{"services": ["app"]}'
```

## Architecture

### Modular Design

The system is built with a modular architecture:

```
hovel_server/
├── api/                    # Flask route handlers
│   ├── status.py          # Health, status, root endpoints
│   └── branch.py          # Branch management endpoints
├── core/                   # Business logic (no Flask)
│   ├── utils.py           # Filesystem tracking, port management
│   ├── branch.py          # Branch creation and management
│   ├── docker.py          # Docker container operations
│   ├── git.py             # Git branch operations
│   └── gemini.py          # Gemini API integration
├── app_factory.py         # Flask app factory
├── config.py              # App configuration
├── logging_config.py      # Logging setup
└── middleware.py          # Request/response logging & error handlers
```

### External Template System

Templates are stored externally for easy management:

```
/opt/hovel-templates/
└── app-template/              # External template directory
    ├── app.py                # Flask application
    ├── requirements.txt      # Python dependencies
    ├── Dockerfile            # Container configuration
    └── docker-compose.branch.template.yaml # Docker Compose template
```

## Development Workflow

1. **Create a branch** via API with specific services
2. **Make changes** to the branch app directory
3. **Test the branch** on its assigned port
4. **Start/stop services** as needed during development
5. **Commit changes** to the git branch
6. **Merge back** to main when ready

## Environment Variables

- `HOVEL_PORT`: Port for the main orchestrator (default: 8000)
- `APP_TEMPLATE_PATH`: Path to external template directory (default: `/opt/hovel-templates/app-template`)
- `AUTOSTART`: Whether to automatically start the Flask server in containers

## Testing

Run the test suite to verify functionality:

```bash
# Test Docker functionality
python test_docker_functionality.py

# Test branch system
python test_branch_system.py

# Test template functionality
python test_template_functionality.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
