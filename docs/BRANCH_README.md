# Branch Management System

This system allows you to create isolated branches of your Flask application, each running on its own port with a separate copy of the app directory and complete environment configuration.

## Features

- Create new branches via API endpoint
- Automatic git branch creation
- Complete duplicate environment of the `./app` directory
- Branch-specific environment variables (`.env` files)
- Branch-specific Docker Compose files
- Assign unique ports to each branch
- Track branch configurations

## API Endpoints

### Create a New Branch

**POST** `/api/branch`

**Request Body:**
```json
{
    "branch_name": "feature-new-ui"
}
```

**Response:**
```json
{
    "message": "Branch feature-new-ui created successfully",
    "branch_name": "feature-new-ui",
    "port": 8001,
    "app_directory": "branches/feature-new-ui",
    "git_branch": "feature-new-ui",
    "status": "created",
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
            "status": "created"
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

### 2. Create a New Branch

```bash
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "feature-new-ui"}'
```

This will:
- Create a new git branch called `feature-new-ui`
- Duplicate the entire `app/` directory to `branches/feature-new-ui/`
- Create a branch-specific `.env` file with environment variables
- Create a branch-specific `docker-compose.yaml` file
- Assign a unique port (starting from 8001)

### 3. Run the Branch App

#### Option A: Direct Python Execution

```bash
python run_branch.py feature-new-ui
```

#### Option B: Docker Compose

```bash
cd branches/feature-new-ui
docker-compose up
```

### 4. Access the Branch App

The branch app will be available on its assigned port (e.g., `http://localhost:8001`).

## Directory Structure

After creating a branch, your directory structure will look like:

```
hovel/
├── app/                          # Original app
│   ├── app.py
│   ├── requirements.txt
│   └── docker-compose.template.yaml
├── branches/
│   └── feature-new-ui/          # Complete branch environment
│       ├── app.py               # Duplicated from original
│       ├── requirements.txt     # Duplicated from original
│       ├── .env                 # Branch-specific environment
│       ├── docker-compose.yaml  # Branch-specific Docker Compose
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

Each branch gets a custom Docker Compose file:

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
```

### Branch Configuration

Each branch has a configuration file:

```json
{
    "branch_name": "feature-new-ui",
    "port": 8001,
    "app_directory": "branches/feature-new-ui",
    "created_at": "2024-01-01T12:00:00Z",
    "status": "created"
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
- **Docker configuration**: Branch-specific `docker-compose.yaml`
- **Port isolation**: Each branch runs on its own port
- **Container isolation**: Each branch has its own Docker container

## Error Handling

The API includes comprehensive error handling for:
- Invalid branch names
- Duplicate branch names
- Git repository issues
- File system errors
- Port conflicts
- Environment file creation issues

## Development Workflow

1. Create a new branch via API
2. Make changes to the branch app directory
3. Test the branch app on its assigned port
4. Commit changes to the git branch
5. Merge back to main when ready

## Scripts

- `run_branch.py`: Run a specific branch's Flask app with environment loading
- `create_branch_compose.py`: Generate Docker Compose file for a branch
- `server.py`: Main API server with branch management endpoints

## Environment Variables

The system automatically sets these environment variables for each branch:
- `FLASK_APP=app.py`
- `FLASK_ENV=development`
- `PORT=8000` (internal container port)
- `BRANCH_NAME={branch_name}`

The external port is automatically assigned and configured in the Docker Compose file. 