# Python Environment Troubleshooting - Lessons Learned

## Problem Summary
When trying to run a Flask application (`server.py`), encountered multiple issues with Python environment management and SSL support in a containerized environment.

## Issues Encountered

### 1. ModuleNotFoundError: No module named 'flask'
**Symptoms:**
- `python server.py` fails with import error
- `python3 server.py` fails with import error
- Flask appears to be installed but not found by Python

**Root Cause:**
- Python environment has external management restrictions (PEP 668)
- Multiple Python installations with different package locations
- SSL module not available for secure pip installations

### 2. SSL Module Not Available
**Symptoms:**
- `WARNING: pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available`
- All pip install attempts fail with SSL connection errors
- Cannot download packages from PyPI

**Root Cause:**
- Missing system SSL libraries in container environment
- Python built without SSL support

### 3. External Environment Management
**Symptoms:**
- `error: externally-managed-environment`
- Cannot install packages system-wide
- Virtual environment creation fails due to SSL issues

### 4. Port Conflicts in Branch Management
**Symptoms:**
- Multiple branches created with same port (8000)
- Environment files (.env) hardcoded to PORT=8000
- Docker Compose files using conflicting ports

**Root Cause:**
- `create_branch_env_file` function hardcoded PORT=8000
- `duplicate_app_directory` function not passing unique port
- `create_branch_docker_compose` function using hardcoded port

## Solutions Discovered

### 1. Use Specific Python Binary
**Solution:** Use the exact Python binary that has Flask installed
```bash
/usr/local/bin/python3.11 server.py
```

**Why it works:**
- Different Python installations may have different package locations
- The specific binary `/usr/local/bin/python3.11` has Flask in its site-packages
- Avoids environment path conflicts

### 2. Dockerfile SSL Dependencies
**Solution:** Add SSL libraries to Dockerfile
```dockerfile
RUN apt-get update && apt-get install -y \
    git \
    libssl-dev \
    python3-openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

**Why it's needed:**
- Enables secure HTTPS connections for pip
- Required for downloading packages from PyPI
- Essential for containerized Python environments

### 3. Environment Detection Strategy
**Best Practice:** Always check multiple Python installations
```bash
# Check available Python versions
which python3
python3 --version
ls -la /usr/local/bin/python*

# Test Flask availability
python3 -c "import flask; print('Flask found')"
/usr/local/bin/python3.11 -c "import flask; print('Flask found')"
```

### 4. Port Conflict Resolution (NEW)
**Solution:** Updated branch creation functions to use unique ports

**Code Changes Made:**

1. **Updated `create_branch_env_file` function:**
```python
def create_branch_env_file(branch_name, target_dir, port):
    """Create environment file for the branch"""
    try:
        env_content = f"""# Environment variables for branch: {branch_name}
FLASK_APP=app.py
FLASK_ENV=development
PORT={port}  # Now uses unique port instead of hardcoded 8000
BRANCH_NAME={branch_name}
"""
```

2. **Updated `duplicate_app_directory` function:**
```python
def duplicate_app_directory(branch_name, port):  # Added port parameter
    # ... existing code ...
    create_branch_env_file(branch_name, target_dir, port)  # Pass port
    create_branch_docker_compose(branch_name, target_dir, port)  # Pass port
```

3. **Updated `create_branch_docker_compose` function:**
```python
def create_branch_docker_compose(branch_name, target_dir, port):  # Added port parameter
    compose_content = f"""services:
  app-{branch_name}:
    build: .
    ports:
      - "{port}:8000"  # External port uses unique port
    environment:
      - PORT={port}  # Environment variable uses unique port
      - BRANCH_NAME={branch_name}
"""
```

4. **Updated main `create_branch` function:**
```python
# Get next available port and store it first
port = get_next_available_port()
BRANCH_PORTS[branch_name] = port

# Pass port to all helper functions
app_dir = duplicate_app_directory(branch_name, port)
```

**Verification Results:**
- ✅ Branch `test-unique-port`: PORT=8001 in .env file
- ✅ Branch `test-port-8002`: PORT=8002 in .env file
- ✅ Docker Compose files use correct external ports
- ✅ No port conflicts between branches

## Key Lessons for AI Agents

### 1. Container Environment Awareness
- **Always check for multiple Python installations** in containerized environments
- **Verify SSL support** before attempting pip installations
- **Use specific binary paths** when standard commands fail

### 2. Troubleshooting Sequence
1. Try standard `python server.py`
2. If ModuleNotFoundError, check `which python` and `python --version`
3. Test Flask import: `python -c "import flask; print('Flask found')"`
4. Try alternative Python binaries: `/usr/local/bin/python3.11 server.py`
5. Check for SSL issues if pip install fails
6. Install system SSL packages if needed

### 3. Docker Best Practices
- **Always include SSL libraries** in Python Docker images
- **Use multi-stage builds** to reduce image size
- **Test package installations** during build process
- **Document specific Python binary paths** that work

### 4. Error Pattern Recognition
- **ModuleNotFoundError** → Check Python path and installations
- **SSL warnings** → Install system SSL packages
- **Externally managed environment** → Use virtual environments or specific binaries
- **Connection errors** → Verify network and SSL support

### 5. Branch Management Best Practices (NEW)
- **Always pass unique ports** to environment file creation functions
- **Update function signatures** to accept port parameters
- **Verify port assignments** in both .env and Docker Compose files
- **Test port uniqueness** by creating multiple branches
- **Use port tracking** (BRANCH_PORTS dictionary) to avoid conflicts

## Quick Reference Commands

```bash
# Check Python installations
which python3 && python3 --version
ls -la /usr/local/bin/python*

# Test Flask availability
python3 -c "import flask; print('Flask found')"
/usr/local/bin/python3.11 -c "import flask; print('Flask found')"

# Install SSL support (if needed)
apt-get update && apt-get install -y libssl-dev python3-openssl ca-certificates

# Run server with specific Python binary
/usr/local/bin/python3.11 server.py

# Test branch creation with unique ports
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "test-branch"}'

# Verify port assignments
curl -s http://localhost:8000/api/branches
cat branches/test-branch/.env
```

## Prevention Strategies

1. **Always include SSL dependencies** in Dockerfiles for Python applications
2. **Test package imports** during container build process
3. **Document working Python binary paths** in project documentation
4. **Use virtual environments** when possible to avoid system conflicts
5. **Include troubleshooting steps** in README files
6. **Pass unique ports** to all branch creation helper functions
7. **Verify port assignments** in generated configuration files
8. **Test branch isolation** by running multiple branches simultaneously

## Related Files
- `Dockerfile` - Updated with SSL dependencies
- `requirements.txt` - Python package dependencies
- `server.py` - Flask application with port conflict resolution
- `branches/*/.env` - Branch-specific environment files with unique ports
- `branches/*/docker-compose.yaml` - Branch-specific Docker Compose files

## Lessons Learned - Gemini CLI Integration and API Key Management

### 1. Branch Creation with Gemini CLI Support
- When a new branch is created via the API, the `.gemini` settings directory is copied into the new branch's directory.
- The `settings.template.json` file is used to generate a branch-specific `.gemini/settings.json` file.
- The API key provided in the branch creation request is injected into the config file, replacing both `YOUR_GEMINI_API_KEY_HERE` and `{{ GEMINI_API_KEY }}` placeholders.
- This ensures each branch is ready for Gemini CLI usage with the correct API key.

### 2. API Key Validation
- The server validates the Gemini API key before proceeding with branch creation.
- For development/testing, a special test key can be allowed to bypass real API validation.

### 3. Postman and Documentation Sync
- The Postman collection is kept in sync with the server endpoints and required request formats.
- All documentation and usage examples are updated to reflect the current API, including the requirement for the Gemini API key in the request body.

### 4. Error Handling and Security
- If the API key is missing or invalid, branch creation is rejected with a clear error message.
- The `.gemini/settings.json` file is gitignored to prevent accidental exposure of API keys.

### 5. Best Practices
- Always use a template config and inject secrets at runtime or branch creation.
- Keep API documentation, Postman collections, and server logic in sync to avoid confusion for users and developers.
- Automate as much of the environment setup as possible for new branches to ensure consistency and developer productivity. 