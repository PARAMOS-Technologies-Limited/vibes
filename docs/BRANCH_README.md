# Branch Management System

This system allows you to create isolated branches of your Flask application, each running on its own port with a separate copy of the app directory and complete environment configuration. The system now supports selective service management, allowing you to choose which Docker services to include and start.

## Features

- Create new branches via API endpoint
- Automatic git branch creation
- Complete duplicate environment of the `./app` directory
- Branch-specific environment variables (`.env` files)
- Branch-specific Docker Compose files
- Assign unique ports to each branch
- Track branch configurations
- **Service Selection**: Choose which Docker services to include and start
- **Flexible Container Management**: Start specific services or all services

## API Endpoints

### Create a New Branch

**POST** `/api/branch`

**Request Body:**
```json
{
    "branch_name": "feature-new-ui",
    "auto_start": true,
    "services": ["app", "database", "cache"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
}
```

**Services Parameter:**
- `services` (optional): Array of service names to include in the branch
- If not specified, defaults to `["app"]` for backward compatibility
- Only the specified services will be included in the branch's Docker Compose file

**Response:**
```json
{
    "message": "Branch feature-new-ui created successfully",
    "branch_name": "feature-new-ui",
    "port": 8001,
    "app_directory": "branches/feature-new-ui",
    "git_branch": "feature-new-ui",
    "status": "created",
    "auto_start": true,
    "services": ["app", "database", "cache"],
    "container_started": true,
    "gemini_api_validated": true,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Start Branch Services

**POST** `/api/branch/{branch_name}/start`

**Request Body (optional):**
```json
{
    "services": ["app", "database"]
}
```

**Services Parameter:**
- `services` (optional): Array of service names to start
- If not provided, starts all services defined in the branch's Docker Compose file
- Only services that exist in the branch's Docker Compose file can be started

**Response:**
```json
{
    "message": "Branch feature-new-ui started successfully",
    "branch_name": "feature-new-ui",
    "status": "started",
    "services_started": ["app", "database"],
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### List All Branches

**GET** `/api/branches`

**Response:**
```json
{
    "branches": [
        {
            "branch_name": "feature-new-ui",
            "port": 8001,
            "app_directory": "branches/feature-new-ui",
            "created_at": "2024-01-01T12:00:00Z",
            "status": "created",
            "services": ["app", "database", "cache"]
        }
    ],
    "count": 1,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Usage

### 1. Start the Main Server

```bash
python server.py
```

The main server runs on port 8000.

### 2. Create a New Branch with Specific Services

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

This will:
- Validate the provided Gemini API key
- Create a new git branch called `feature-new-ui`
- Duplicate the entire `app/` directory to `branches/feature-new-ui/`
- Create a branch-specific `.env` file with environment variables
- Create a branch-specific `docker-compose.yaml` file with only the specified services
- Assign a unique port (starting from 8001)
- Optionally start the Docker container if `auto_start` is true

### 3. Start Specific Services

```bash
# Start only the app service
curl -X POST http://localhost:8000/api/branch/feature-new-ui/start \
  -H "Content-Type: application/json" \
  -d '{"services": ["app"]}'

# Start multiple services
curl -X POST http://localhost:8000/api/branch/feature-new-ui/start \
  -H "Content-Type: application/json" \
  -d '{"services": ["app", "database"]}'

# Start all services in the branch
curl -X POST http://localhost:8000/api/branch/feature-new-ui/start
```

### 4. Run the Branch App

#### Option A: Direct Python Execution

```bash
python run_branch.py feature-new-ui
```

#### Option B: Docker Compose

```bash
cd branches/feature-new-ui
docker-compose up
```

### 5. Access the Branch App

The branch app will be available on its assigned port (e.g., `http://localhost:8001`).

## Service Selection Examples

### Full-Stack Application

```bash
# Create branch with all services
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "full-stack-feature",
    "services": ["app", "database", "redis", "nginx"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'

# Start only backend services for development
curl -X POST http://localhost:8000/api/branch/full-stack-feature/start \
  -H "Content-Type: application/json" \
  -d '{"services": ["app", "database"]}'
```

### Frontend-Only Development

```bash
# Create branch with only frontend services
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "frontend-feature",
    "services": ["app", "nginx"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'
```

### Backend-Only Development

```bash
# Create branch with only backend services
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "backend-feature",
    "services": ["app", "database", "redis"],
    "gemini_api_key": "YOUR_GEMINI_API_KEY"
  }'
```

## Directory Structure

After creating a branch, your directory structure will look like:

```
hovel/
├── app/                          # Original app
│   ├── app.py
│   ├── requirements.txt
│   └── docker-compose.branch.template.yaml
├── branches/
│   └── feature-new-ui/          # Complete branch environment
│       ├── app.py               # Duplicated from original
│       ├── requirements.txt     # Duplicated from original
│       ├── .env                 # Branch-specific environment
│       ├── docker-compose.yaml  # Branch-specific Docker Compose (filtered)
│       └── branch_config.json   # Branch configuration
├── server.py                    # Main API server
├── run_branch.py               # Branch runner script
└── docker-compose.branch.template.yaml
```

## Environment Configuration

### Branch .env File

Each branch gets its own environment file:

```env
# Environment variables for branch: feature-new-ui
FLASK_APP=app.py
FLASK_ENV=development
PORT=8000
BRANCH_NAME=feature-new-ui
```

### Branch Docker Compose

Each branch gets a custom Docker Compose file with only the specified services:

```yaml
services:
  app-feature-new-ui:
    build: .
    ports:
      - "8001:8000"
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=development
      - PORT=8000
      - BRANCH_NAME=feature-new-ui
    restart: unless-stopped
    container_name: hovel-app-feature-new-ui

  database-feature-new-ui:
    image: postgres:13
    environment:
      - POSTGRES_DB=hovel_feature_new_ui
      - POSTGRES_USER=hovel
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    restart: unless-stopped
    container_name: hovel-database-feature-new-ui
```

### Branch Configuration

Each branch has a configuration file:

```json
{
    "branch_name": "feature-new-ui",
    "port": 8001,
    "app_directory": "branches/feature-new-ui",
    "created_at": "2024-01-01T12:00:00Z",
    "status": "created",
    "services": ["app", "database", "cache"]
}
```

## Port Assignment

- Main server: Port 8000
- Branch apps: Ports 8001, 8002, 8003, etc. (automatically assigned)

## Git Integration

The system automatically:
- Creates a new git branch with the specified name
- Checks out the new branch
- All changes to the branch app directory will be on the new branch

## Environment Isolation

Each branch environment includes:
- **Complete app directory copy**: All files from the original `app/` directory
- **Environment variables**: Branch-specific `.env` file
- **Docker configuration**: Branch-specific `docker-compose.yaml` with filtered services
- **Port isolation**: Each branch runs on its own port
- **Container isolation**: Each branch has its own Docker container
- **Service isolation**: Only specified services are included and started

## Error Handling

The API includes comprehensive error handling for:
- Invalid branch names
- Duplicate branch names
- Git repository issues
- File system errors
- Port conflicts
- Environment file creation issues
- Invalid service names
- Service filtering errors

## Development Workflow

1. Create a new branch via API with specific services
2. Make changes to the branch app directory
3. Start/stop specific services as needed during development
4. Test the branch app on its assigned port
5. Commit changes to the git branch
6. Merge back to main when ready

## Scripts

- `run_branch.py`: Run a specific branch's Flask app with environment loading
- `create_branch_compose.py`: Generate Docker Compose file for a branch
- `server.py`: Main API server with branch management endpoints

## Environment Variables

- `APP_TEMPLATE_PATH`: Path to external template directory (default: `/opt/hovel-templates/app-template`)
- `HOVEL_PORT`: Port for the main orchestrator (default: 8000)
- `AUTOSTART`: Whether to automatically start the Flask server in containers

## Service Management Best Practices

### Service Naming
- Use descriptive service names: `app`, `database`, `redis`, `nginx`, etc.
- Keep service names consistent across branches
- Document service dependencies in your template

### Service Selection Strategy
- **Development**: Start with minimal services needed for development
- **Testing**: Include all services for comprehensive testing
- **Production**: Use all services for full functionality

### Performance Considerations
- Only start services you need for current development
- Use service filtering to reduce resource usage
- Monitor container resource usage with `docker stats`

## Related Documentation

- [Main README](../README.md) - Project overview and quick start
- [Gemini Session Management](GEMINI_SESSION_README.md) - Terminal session management
- [API Server](../server.py) - Main Flask application with Docker integration
- [Docker Configuration](../Dockerfile) - Container setup with Docker-in-Docker
- [Docker Test Script](../test_docker_functionality.py) - Docker functionality testing 