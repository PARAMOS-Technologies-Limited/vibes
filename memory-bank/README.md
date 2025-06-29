# Memory Bank - AI Agent Knowledge Base

This directory contains comprehensive documentation and lessons learned for AI agents working on the Hovel project. Use these resources to understand the project architecture, troubleshoot issues, and follow best practices.

## 📚 Available Resources

### 🛠️ Technical Guides
- **[Python Environment Troubleshooting](python-environment-troubleshooting.md)** - Complete guide to resolving Python environment and Flask installation issues in containerized environments
- **[Flask Server Startup Guide](flask-server-startup-guide.md)** - Step-by-step instructions for starting Flask servers with troubleshooting flows

### 📋 Project Planning
- **[Comprehensive Project Plan](project-plan-comprehensive.md)** - Complete project roadmap covering architecture, API specs, Docker setup, development workflow, and future enhancements

## 🎯 Quick Reference for AI Agents

### When Starting the Server
1. Check [Flask Server Startup Guide](flask-server-startup-guide.md) for the correct startup sequence
2. If you encounter ModuleNotFoundError, refer to [Python Environment Troubleshooting](python-environment-troubleshooting.md)
3. Use `/usr/local/bin/python3.11 server.py` as the recommended startup command

### When Troubleshooting Issues
1. **ModuleNotFoundError**: Check Python installations and use specific binary paths
2. **SSL Issues**: Install system SSL packages (libssl-dev, python3-openssl, ca-certificates)
3. **External Environment Management**: Use virtual environments or specific Python binaries
4. **Port Conflicts**: Verify unique port assignment in branch .env files
5. **Docker Issues**: Check Docker daemon status and socket permissions

### When Planning Development
1. Review [Comprehensive Project Plan](project-plan-comprehensive.md) for architecture and API specifications
2. Follow the documented directory structure and development workflow
3. Reference the future enhancements roadmap for feature planning

### When Managing Branches (NEW)
1. **Create branches** using the API: `POST /api/branch`
2. **Verify unique ports** are assigned to each branch
3. **Check .env files** for correct PORT assignments
4. **Test branch isolation** by running multiple branches simultaneously
5. **Check .branch files** for complete branch metadata and persistence
6. **Restart server** to verify branch persistence across restarts

### When Managing Docker Containers (NEW)
1. **Auto-start containers** by setting `auto_start: true` in branch creation
2. **Monitor containers** using `/api/branch/{name}/status` endpoint
3. **Access logs** using `/api/branch/{name}/logs` endpoint
4. **Start/stop containers** using dedicated endpoints
5. **Verify Docker-in-Docker** is working properly

### When Managing Filesystem-Based Tracking (NEW)
1. **Check .branch files** in each branch directory for metadata
2. **Verify persistence** by restarting the server and checking if branches are still listed
3. **Monitor branch status** updates in .branch files when containers start/stop
4. **Use filesystem scanning** to discover existing branches on server startup
5. **Test branch cleanup** ensures .branch files are properly removed

### When Working with Modular Architecture (NEW)
1. **Add new API endpoints**: Create new blueprints in `hovel_server/api/`
2. **Add business logic**: Create new modules in `hovel_server/core/`
3. **Update configuration**: Modify `hovel_server/config.py`
4. **Add middleware**: Extend `hovel_server/middleware.py`
5. **Test individual modules**: Use pytest for core logic, integration tests for API
6. **Register blueprints**: Update `hovel_server/api/__init__.py` for new endpoints

## 🔍 Search Keywords

Use these keywords to quickly find relevant information:

- **Python environment**: Environment setup, SSL issues, virtual environments
- **Flask server**: Startup commands, troubleshooting, configuration
- **Docker**: Container setup, SSL dependencies, environment isolation, Docker-in-Docker
- **API endpoints**: REST API, branch management, health checks, container management
- **Development workflow**: Cursor.dev integration, testing, deployment
- **Architecture**: System design, directory structure, technology stack
- **Port conflicts**: Branch management, unique port assignment, environment isolation
- **Container management**: Docker containers, auto-start, monitoring, logs
- **Filesystem tracking**: .branch files, persistence, server restart, branch metadata
- **Branch persistence**: Filesystem-based tracking, .branch files, startup scanning
- **Modular architecture**: Package structure, separation of concerns, blueprints, core modules
- **Module development**: API layer, core layer, business logic, Flask blueprints

## 📖 How to Use This Knowledge Base

### For New AI Agents
1. Start with the [Comprehensive Project Plan](project-plan-comprehensive.md) to understand the project scope
2. Review the [Flask Server Startup Guide](flask-server-startup-guide.md) for operational procedures
3. Keep the [Python Environment Troubleshooting](python-environment-troubleshooting.md) guide handy for common issues

### For Ongoing Development
1. Reference the project plan for API specifications and architecture decisions
2. Use the troubleshooting guides when encountering environment issues
3. Update the knowledge base with new lessons learned

### For Problem Solving
1. Identify the issue category (environment, server, API, Docker, etc.)
2. Search the relevant guide for similar problems
3. Follow the documented troubleshooting sequence
4. Document any new solutions discovered

### For Branch Management (NEW)
1. **Port Conflict Resolution**: ✅ **COMPLETED** - Unique ports are automatically assigned
2. **Environment Isolation**: Each branch runs on its own port (8001, 8002, 8003, etc.)
3. **Verification**: Check .env files and Docker Compose configurations
4. **Testing**: Create multiple branches to verify isolation

### For Docker Container Management (NEW)
1. **Docker-in-Docker Setup**: ✅ **COMPLETED** - Orchestrator can manage other containers
2. **Auto-start Functionality**: ✅ **COMPLETED** - Containers start automatically when requested
3. **Container Monitoring**: ✅ **COMPLETED** - Status and logs available via API
4. **Container Lifecycle**: ✅ **COMPLETED** - Start, stop, restart operations available

### For Modular Development (NEW)
1. **API Layer Development**: Create blueprints in `hovel_server/api/` for new endpoints
2. **Core Logic Development**: Add business logic in `hovel_server/core/` (no Flask dependencies)
3. **Testing Strategy**: Test core logic independently, then integration tests for API
4. **Blueprint Registration**: Always register new blueprints in `hovel_server/api/__init__.py`
5. **Configuration Management**: Use `hovel_server/config.py` for app-wide settings
6. **Middleware Extension**: Add request/response processing in `hovel_server/middleware.py`

## 🎉 Recent Achievements

### Server Modularization - COMPLETED ✅
**Problem Solved:** The server was a single large file (`server.py`) with 749 lines, making it difficult to maintain, test, and extend.

**Solution Implemented:**
1. **Created modular package structure**: Split into `hovel_server/` package with clear separation of concerns
2. **API Layer**: Moved all Flask routes to blueprints in `hovel_server/api/`
3. **Core Layer**: Extracted business logic to `hovel_server/core/` (no Flask dependencies)
4. **Infrastructure**: Separated config, logging, middleware, and app factory
5. **Simplified entry point**: New `server.py` is only 40 lines and focuses on startup

**New Structure:**
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

**Benefits:**
- 🧩 **Modular**: Each module has a single responsibility
- 🧪 **Testable**: Core logic can be tested without Flask
- 🔧 **Maintainable**: Easier to locate and fix issues
- 📈 **Scalable**: Easy to add new features and endpoints
- 🧠 **Reduced context**: Smaller files are easier to understand
- 👥 **Team-friendly**: Multiple developers can work on different modules

**Testing:**
- ✅ All existing functionality preserved
- ✅ API endpoints work identically
- ✅ Filesystem-based tracking functional
- ✅ Docker integration working
- ✅ Git operations operational
- ✅ Gemini API integration intact

### Filesystem-Based Branch Tracking - COMPLETED ✅
**Problem Solved:** Branch tracking was using in-memory variables (`BRANCH_PORTS`), which meant branch information was lost when the server restarted.

**Solution Implemented:**
1. **Removed in-memory tracking**: Eliminated the `BRANCH_PORTS` variable
2. **Added .branch files**: Each branch directory now contains a `.branch` file with complete branch information
3. **Filesystem scanning**: System scans the filesystem on startup to discover existing branches
4. **Persistent storage**: Branch information persists across server restarts
5. **Complete branch metadata**: .branch files contain port, status, creation time, and other details

**Code Changes:**
```python
# Before: In-memory tracking
BRANCH_PORTS = {}  # Lost on server restart

# After: Filesystem-based tracking
def get_branch_info(branch_name):
    branch_file = f'branches/{branch_name}/.branch'
    if os.path.exists(branch_file):
        with open(branch_file, 'r') as f:
            return json.load(f)
    return None

def save_branch_info(branch_name, branch_info):
    branch_file = f'branches/{branch_name}/.branch'
    with open(branch_file, 'w') as f:
        json.dump(branch_info, f, indent=2)
```

**Benefits:**
- 🚀 **Persistent across restarts**: Branch information survives server restarts
- 🔍 **Self-discovering**: System automatically finds existing branches on startup
- 📊 **Complete metadata**: Each .branch file contains comprehensive branch information
- 🛡️ **Reliable**: No data loss due to memory issues or crashes
- 🔄 **Scalable**: Works with any number of branches without memory constraints

**Testing:**
- ✅ Created `test_filesystem_tracking.py` to verify functionality
- ✅ Tested branch creation, listing, status updates, and deletion
- ✅ Verified persistence across server restart simulation
- ✅ Confirmed .branch files are properly created and removed

### Port Conflict Resolution - COMPLETED ✅
**Problem Solved:** Multiple branches were being created with the same port (8000), causing conflicts.

**Solution:** Updated branch creation functions to use unique ports:
- ✅ Each branch gets unique port in .env file
- ✅ Docker Compose uses unique external ports
- ✅ Automatic port increment (8001, 8002, 8003, etc.)
- ✅ No conflicts between running branches

**Impact:**
- 🚀 Multiple branches can run simultaneously
- 🔧 Full environment isolation achieved
- 📊 Scalable branch management for teams

### Docker Integration - COMPLETED ✅
**Problem Solved:** Need to automatically start cloned dev environments using Docker.

**Solution:** Implemented full Docker-in-Docker (DinD) support:
- ✅ Docker installed in orchestrator container
- ✅ Docker socket mounted for container management
- ✅ Auto-start functionality for new branches
- ✅ Container monitoring and lifecycle management
- ✅ Comprehensive API endpoints for container operations

**Impact:**
- 🐳 Full containerization of development environments
- 🔄 Automatic container startup and management
- 📊 Real-time container status and log monitoring
- 🚀 Scalable development environment orchestration

## 🔄 Maintenance

This knowledge base should be updated whenever:
- New issues are encountered and resolved
- Architecture changes are made
- New features are implemented
- Best practices are discovered
- Major problems are solved (like port conflicts and Docker integration)

## 📞 Related Resources

- **Main README**: [../README.md](../README.md) - Project overview and quick start
- **Branch Documentation**: [../docs/BRANCH_README.md](../docs/BRANCH_README.md) - Branch management system
- **API Server**: [../server.py](../server.py) - Main Flask application with Docker integration
- **Docker Configuration**: [../Dockerfile](../Dockerfile) - Container setup with Docker-in-Docker
- **Docker Test Script**: [../test_docker_functionality.py](../test_docker_functionality.py) - Docker functionality testing

---

*This memory bank serves as a comprehensive knowledge base for AI agents working on the Hovel project, ensuring consistent problem-solving approaches and best practices. The recent Docker integration demonstrates the value of this knowledge base in solving complex development challenges.* 