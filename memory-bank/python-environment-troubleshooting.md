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

## Key Lessons for AI Agents

### 1. Container Environment Awareness
- **Always check for multiple Python installations** in containerized environments
- **Verify SSL support** before attempting pip installations
- **Use specific binary paths** when standard commands fail

### 2. Troubleshooting Sequence
1. Try standard `python server.py`
2. If ModuleNotFoundError, check `which python` and `python --version`
3. Test Flask import: `python -c "import flask; print('Flask found')"`
4. Try alternative Python binaries: `/usr/local/bin/python3.11`
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
```

## Prevention Strategies

1. **Always include SSL dependencies** in Dockerfiles for Python applications
2. **Test package imports** during container build process
3. **Document working Python binary paths** in project documentation
4. **Use virtual environments** when possible to avoid system conflicts
5. **Include troubleshooting steps** in README files

## Related Files
- `Dockerfile` - Updated with SSL dependencies
- `requirements.txt` - Python package dependencies
- `server.py` - Flask application that was failing to start 