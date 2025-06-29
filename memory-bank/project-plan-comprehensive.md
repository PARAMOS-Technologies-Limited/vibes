# Hovel Project - Comprehensive Development Plan

## 🏗️ Architecture Overview

### Core Components
- **Main API Server**: Flask-based REST API with comprehensive endpoints
- **Modular Package Structure**: Well-organized `hovel_server/` package with separation of concerns
- **Branch Management System**: Isolated development environments for different features
- **Docker Integration**: Full containerization with automatic environment isolation
- **Git Integration**: Automatic branch creation and management
- **External Template System**: Configurable template directories for app duplication
- **Web Terminal Interface**: Embeddable terminal for web applications

### Technology Stack
- **Backend**: Python 3.11, Flask 2.3.3, Flask-CORS 4.0.0
- **Containerization**: Docker, Docker Compose
- **Process Management**: Gunicorn 21.2.0
- **HTTP Client**: Requests 2.31.0
- **Version Control**: Git integration
- **Development**: Cursor.dev IDE integration

### Modular Architecture (NEW)
The server has been refactored into a modular package structure for improved maintainability:

```
hovel_server/
├── api/                    # Flask route handlers (blueprints)
│   ├── status.py          # Health, status, root endpoints
│   └── branch.py          # Branch management endpoints
├── core/                   # Business logic (no Flask dependencies)
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

**Benefits of Modular Architecture:**
- **Separation of Concerns**: API layer handles HTTP, core layer handles business logic
- **Testability**: Core logic can be tested without Flask dependencies
- **Maintainability**: Each module has a single responsibility
- **Scalability**: Easy to add new features and endpoints
- **Team Development**: Multiple developers can work on different modules
- **Reduced Context**: Smaller files are easier to understand and navigate

### External Template System (NEW)
The system now supports external template directories for better separation of concerns:

```
/opt/hovel-templates/
├── app-template/              # Default Node.js/Express template
│   ├── app.js                # Express.js application
│   ├── package.json          # Node.js dependencies
│   ├── Dockerfile            # Container configuration
│   └── docker-compose.branch.template.yaml # Docker Compose template
├── python-flask-template/     # Python/Flask template (future)
└── react-frontend-template/   # React frontend template (future)
```

**Benefits of External Templates:**
- **Clean Separation**: Templates are independent of the orchestrator repository
- **Easy Updates**: Update templates without touching the main repo
- **Multiple Templates**: Support different app types and frameworks
- **Version Control**: Templates can be in their own repositories
- **Team Collaboration**: Multiple developers can contribute to templates
- **Testable**: Comprehensive test suite for template functionality

## 📁 Directory Structure

```
hovel/
├── server.py                    # Entry point (simplified, 40 lines)
├── server_old.py               # Original monolithic server (backup)
├── hovel_server/               # New modular package
│   ├── __init__.py
│   ├── app_factory.py          # Flask app factory
│   ├── config.py               # App configuration
│   ├── logging_config.py       # Logging setup
│   ├── middleware.py           # Request/response logging & error handlers
│   ├── api/                    # Flask route handlers
│   │   ├── __init__.py
│   │   ├── status.py           # Health, status, root endpoints
│   │   └── branch.py           # Branch management endpoints
│   └── core/                   # Business logic (no Flask dependencies)
│       ├── __init__.py
│       ├── utils.py            # Filesystem tracking, port management
│       ├── branch.py           # Branch creation and management
│       ├── docker.py           # Docker container operations
│       ├── git.py              # Git branch operations
│       └── gemini.py           # Gemini API integration
├── app/                        # Main application directory (can be removed after setup)
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── docker-compose.template.yaml
├── branches/                   # Branch environments (created dynamically)
├── docs/                       # Documentation
│   └── BRANCH_README.md       # Branch management documentation
├── memory-bank/                # AI Agent Knowledge Base
│   ├── python-environment-troubleshooting.md
│   ├── flask-server-startup-guide.md
│   └── project-plan-comprehensive.md
├── setup_template_directory.py # Template setup script
├── test_template_functionality.py # Template functionality test script
├── run_branch.py              # Branch runner script
├── test_branch_system.py      # System test script
├── test_filesystem_tracking.py # Filesystem tracking test script
├── create_branch_compose.py   # Docker Compose generator
├── docker-compose.yaml        # Main Docker Compose
├── docker-compose.branch.template.yaml
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
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

## 🔌 API Specifications

### Core Endpoints

#### Health & Status
- `GET /` - Server information and status
- `GET /health` - Health check endpoint
- `GET /api/status` - API status and available endpoints

#### Branch Management
- `POST /api/branch` - Create a new development branch
  ```json
  {
    "branch_name": "feature-new-ui",
    "description": "Optional branch description"
  }
  ```
- `GET /api/branches` - List all created branches
- `DELETE /api/branch/{branch_name}` - Delete a branch
- `GET /api/branch/{branch_name}/status` - Get branch status

#### Environment Management
- `POST /api/branch/{branch_name}/start` - Start branch environment
- `POST /api/branch/{branch_name}/stop` - Stop branch environment
- `GET /api/branch/{branch_name}/logs` - Get branch logs

### Response Formats

#### Success Response
```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully"
}
```

#### Error Response
```json
{
  "status": "error",
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## 🐳 Docker Compose Setup

### Main Application
```yaml
version: '3.8'
services:
  hovel-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=development
      - FLASK_APP=server.py
    volumes:
      - .:/app
      - ./branches:/app/branches
    networks:
      - hovel-network

networks:
  hovel-network:
    driver: bridge
```

### Branch Environment Template
```yaml
version: '3.8'
services:
  branch-{branch_name}:
    build: .
    ports:
      - "{port}:8000"
    environment:
      - FLASK_ENV=development
      - BRANCH_NAME={branch_name}
    volumes:
      - ./branches/{branch_name}:/app
    networks:
      - hovel-network
```

## 🛠️ Development Workflow with Cursor.dev

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd hovel

# Install dependencies
pip install -r requirements.txt

# Start development server
python server.py
```

### 2. Cursor.dev Integration
- **AI-Powered Development**: Leverage Cursor's AI for code generation and debugging
- **Real-time Collaboration**: Multi-user development environment
- **Integrated Terminal**: Built-in terminal for running commands
- **Git Integration**: Seamless version control workflow

### 3. Development Commands
```bash
# Create new feature branch
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "feature-new-ui"}'

# Run branch application
python run_branch.py feature-new-ui

# Test system
python test_branch_system.py
```

### 4. Code Quality
- **Linting**: Python flake8, black formatting
- **Testing**: pytest for unit and integration tests
- **Documentation**: Auto-generated API docs
- **Type Checking**: mypy for type safety

### 5. Modular Development Workflow (NEW)
With the new modular architecture, development follows these patterns:

#### Adding New API Endpoints
```bash
# 1. Create new blueprint in hovel_server/api/
# Example: hovel_server/api/new_feature.py

# 2. Register blueprint in hovel_server/api/__init__.py
from .new_feature import new_feature_bp
app.register_blueprint(new_feature_bp)
```

#### Adding New Business Logic
```bash
# 1. Create new module in hovel_server/core/
# Example: hovel_server/core/new_service.py

# 2. Import in API layer
from ..core import new_service
```

#### Testing Individual Modules
```bash
# Test core logic without Flask
python -m pytest hovel_server/core/

# Test API endpoints
python -m pytest hovel_server/api/

# Test full integration
python test_filesystem_tracking.py
```

#### Module Responsibilities
- **API Layer** (`hovel_server/api/`): Only HTTP request/response handling
- **Core Layer** (`hovel_server/core/`): Pure business logic, no Flask dependencies
- **Infrastructure**: Configuration, logging, middleware, app factory

## 🚀 Future Enhancements

### Phase 1: Core Features (Current)
- [x] Basic Flask API server
- [x] Branch management system
- [x] Docker integration
- [x] Git workflow integration
- [x] Environment isolation
- [x] **Port conflict resolution** ✅ **COMPLETED**
- [x] **Server modularization** ✅ **COMPLETED**
- [x] **External template system** ✅ **COMPLETED**

### Phase 2: Advanced Features
- [ ] **Web Terminal Interface**
  - Embeddable terminal component
  - Real-time command execution
  - Session management
  - File system integration

- [ ] **Enhanced Branch Management**
  - Branch templates and presets
  - Environment variable management
  - Resource monitoring and limits
  - Automatic cleanup policies

- [ ] **Multiple Template Types**
  - Python/Flask template
  - React frontend template
  - Vue.js template
  - Go microservice template
  - Template selection API

- [ ] **API Enhancements**
  - Authentication and authorization
  - Rate limiting
  - API versioning
  - OpenAPI/Swagger documentation

### Phase 3: Production Features
- [ ] **Monitoring & Observability**
  - Prometheus metrics
  - Grafana dashboards
  - Centralized logging (ELK stack)
  - Health checks and alerts

- [ ] **Security Enhancements**
  - HTTPS/TLS support
  - JWT authentication
  - Role-based access control
  - Audit logging

- [ ] **Scalability**
  - Load balancing
  - Auto-scaling
  - Database integration
  - Caching layer (Redis)

### Phase 4: Advanced Integrations
- [ ] **CI/CD Pipeline**
  - GitHub Actions integration
  - Automated testing
  - Deployment automation
  - Environment promotion

- [ ] **External Integrations**
  - IDE plugins (VS Code, IntelliJ)
  - Slack/Discord notifications
  - Jira/Trello integration
  - Cloud provider APIs

## 🔧 Configuration Management

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_APP=server.py
FLASK_DEBUG=true

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Branch Management
BRANCH_BASE_PORT=8001
BRANCH_MAX_COUNT=10
BRANCH_TIMEOUT=3600

# Docker Configuration
DOCKER_NETWORK=hovel-network
DOCKER_REGISTRY=localhost:5000
```

### Configuration Files
- `config.py` - Application configuration
- `docker-compose.yaml` - Main application setup
- `docker-compose.branch.template.yaml` - Branch template
- `.env` - Environment variables
- `.gitignore` - Version control exclusions

## 🎯 Recent Achievements (NEW)

### External Template System - COMPLETED ✅
**Problem Solved:** The app directory was embedded in the main repository, making template management difficult and requiring repo changes for template updates.

**Solution Implemented:**
1. **External template directories**: Templates are now stored outside the main repo at `/opt/hovel-templates/app-template`
2. **Environment variable configuration**: `APP_TEMPLATE_PATH` controls template location
3. **Docker volume mounting**: Template directory is mounted into the container
4. **Setup automation**: `setup_template_directory.py` script for easy template setup
5. **Comprehensive testing**: `test_template_functionality.py` verifies template system works
6. **Clean separation**: Templates are independent of the orchestrator repository

**Code Changes:**
```python
# Before: Hardcoded app directory
def duplicate_app_directory(branch_name, port, api_key=None):
    source_dir = 'app'  # ❌ Embedded in repo

# After: Configurable external template
def duplicate_app_directory(branch_name, port, api_key=None):
    template_dir = os.getenv('APP_TEMPLATE_PATH', '/opt/hovel-templates/app-template')  # ✅ External configurable
```

**Benefits:**
- 🧹 **Clean separation**: Templates are independent of the orchestrator repo
- 🔄 **Easy updates**: Update templates without touching the main repo
- 📁 **Multiple templates**: Support different app types and frameworks
- 🏷️ **Version control**: Templates can be in their own repositories
- 👥 **Team collaboration**: Multiple developers can contribute to templates
- 🧪 **Testable**: Comprehensive test suite for template functionality

**Setup Process:**
1. Run `python setup_template_directory.py` to copy app to external location
2. Restart Docker container to pick up new template path
3. Test with `python test_template_functionality.py`
4. Optionally remove local app directory with `--remove-local` flag

**Testing:**
- ✅ Template directory creation and file copying
- ✅ Environment variable configuration
- ✅ Docker volume mounting
- ✅ Branch creation using external templates
- ✅ Template file validation and placeholder replacement
- ✅ Cleanup and error handling

### Port Conflict Resolution - COMPLETED ✅
**Problem Solved:** Multiple branches were being created with the same port (8000), causing conflicts when trying to run multiple branch environments simultaneously.

**Solution Implemented:**
1. **Updated function signatures** to accept unique port parameters
2. **Modified .env file generation** to use unique ports instead of hardcoded 8000
3. **Updated Docker Compose generation** to use unique external ports
4. **Implemented port tracking** to prevent conflicts

**Code Changes:**
```python
# Before: Hardcoded PORT=8000
def create_branch_env_file(branch_name, target_dir):
    env_content = f"""PORT=8000"""  # ❌ Always same port

# After: Unique port assignment
def create_branch_env_file(branch_name, target_dir, port):
    env_content = f"""PORT={port}"""  # ✅ Unique port per branch
```

**Verification Results:**
- ✅ Branch `test-unique-port`: PORT=8001
- ✅ Branch `test-port-8002`: PORT=8002
- ✅ Docker Compose files use correct external ports
- ✅ No port conflicts between branches
- ✅ Automatic port increment (8001, 8002, 8003, etc.)

**Testing Commands:**
```bash
# Create branches with unique ports
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "feature-1"}'

curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "feature-2"}'

# Verify unique port assignment
curl -s http://localhost:8000/api/branches | jq '.branches[].port'
# Output: [8001, 8002]
```

**Impact:**
- 🚀 **Multiple branches can now run simultaneously** without port conflicts
- 🔧 **Environment isolation** is now fully functional
- 📊 **Scalable branch management** for development teams
- 🛡️ **Prevented deployment conflicts** in production scenarios

## 📊 Performance Considerations

### Optimization Strategies
1. **Container Optimization**
   - Multi-stage Docker builds
   - Layer caching optimization
   - Minimal base images

2. **API Performance**
   - Response caching
   - Database connection pooling
   - Async request handling

3. **Resource Management**
   - Memory usage monitoring
   - CPU utilization tracking
   - Disk space management

### Monitoring Metrics
- Request/response times
- Error rates
- Resource utilization
- Branch environment status
- API endpoint usage

## 🔒 Security Considerations

### Current Security Measures
- Environment isolation
- Container security
- Input validation
- Error handling

### Planned Security Enhancements
- Authentication system
- Authorization controls
- Data encryption
- Audit logging
- Security scanning

## 📈 Deployment Strategy

### Development Environment
- Local Docker Compose
- Hot reloading
- Debug mode enabled
- Direct file access

### Staging Environment
- Cloud deployment
- Load balancing
- Monitoring enabled
- Automated testing

### Production Environment
- High availability
- Auto-scaling
- Backup strategies
- Disaster recovery

## 🧪 Testing Strategy

### Test Types
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **System Tests**: End-to-end workflow testing
4. **Performance Tests**: Load and stress testing

### Test Automation
- Automated test execution
- Continuous integration
- Test coverage reporting
- Performance benchmarking

## 📚 Documentation Strategy

### Documentation Types
- **API Documentation**: OpenAPI/Swagger specs
- **User Guides**: Step-by-step instructions
- **Developer Guides**: Technical implementation details
- **Architecture Docs**: System design and decisions

### Documentation Tools
- Sphinx for technical docs
- Swagger UI for API docs
- Markdown for README files
- Diagrams for architecture

## 🎯 Success Metrics

### Technical Metrics
- API response time < 200ms
- 99.9% uptime
- Zero security vulnerabilities
- 90% test coverage

### Business Metrics
- Developer productivity increase
- Reduced environment setup time
- Improved collaboration efficiency
- Cost savings in infrastructure

## 🔄 Maintenance Plan

### Regular Maintenance
- Dependency updates
- Security patches
- Performance monitoring
- Backup verification

### Long-term Maintenance
- Architecture reviews
- Technology stack updates
- Documentation updates
- User feedback integration

---

*This comprehensive plan serves as a roadmap for the Hovel project development, providing clear guidance for current and future development efforts.* 