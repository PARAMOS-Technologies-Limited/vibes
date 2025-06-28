# Flask Server Startup Guide for Containerized Environments

## Quick Start Checklist

### 1. Pre-Startup Verification
```bash
# Check Python installations
which python3 && python3 --version
ls -la /usr/local/bin/python*

# Verify Flask availability
python3 -c "import flask; print('Flask found')"
/usr/local/bin/python3.11 -c "import flask; print('Flask found')"

# Check if requirements are installed
pip list | grep flask
```

### 2. SSL Support Verification
```bash
# Check if SSL packages are installed
dpkg -l | grep -E "(libssl-dev|python3-openssl|ca-certificates)"

# Install if missing
apt-get update && apt-get install -y libssl-dev python3-openssl ca-certificates
```

### 3. Server Startup Commands

#### Option A: Standard Python (if available)
```bash
python server.py
```

#### Option B: Python3 (if available)
```bash
python3 server.py
```

#### Option C: Specific Python Binary (recommended for containers)
```bash
/usr/local/bin/python3.11 server.py
```

## Troubleshooting Flow

### Step 1: ModuleNotFoundError
**If you get:** `ModuleNotFoundError: No module named 'flask'`

**Try these in order:**
1. `python3 server.py`
2. `/usr/local/bin/python3.11 server.py`
3. Check if Flask is installed: `pip list | grep flask`
4. Install Flask: `pip install flask flask-cors gunicorn requests`

### Step 2: SSL Issues
**If you get:** `WARNING: pip is configured with locations that require TLS/SSL`

**Solution:**
```bash
apt-get update && apt-get install -y libssl-dev python3-openssl ca-certificates
```

### Step 3: External Environment Management
**If you get:** `error: externally-managed-environment`

**Solutions:**
1. Use virtual environment: `python3 -m venv venv && source venv/bin/activate`
2. Use specific Python binary: `/usr/local/bin/python3.11 server.py`
3. Override with flag: `pip install --break-system-packages flask`

## Success Indicators

When the server starts successfully, you should see:
```
Flask found
2025-06-28 09:47:56,989 - __main__ - INFO - Starting server on 0.0.0.0:8000
2025-06-28 09:47:56,989 - __main__ - INFO - Debug mode: True
 * Serving Flask app 'server'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://172.18.0.2:8000
 * Debugger is active!
 * Debugger PIN: 350-616-165
```

## Dockerfile Best Practices

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including SSL support
RUN apt-get update && apt-get install -y \
    git \
    libssl-dev \
    python3-openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application with specific Python binary
CMD ["/usr/local/bin/python3.11", "server.py"]
```

## Environment Variables

```bash
# Optional: Set Flask environment variables
export FLASK_ENV=development
export FLASK_APP=server.py
export PORT=8000
export HOST=0.0.0.0
```

## Health Check Commands

```bash
# Test if server is running
curl -s http://localhost:8000/health

# Check server status
curl -s http://localhost:8000/api/status

# Test main endpoint
curl -s http://localhost:8000/
```

## Common Issues and Solutions

| Issue | Error Message | Solution |
|-------|---------------|----------|
| Flask not found | `ModuleNotFoundError: No module named 'flask'` | Use `/usr/local/bin/python3.11 server.py` |
| SSL not available | `WARNING: pip is configured with locations that require TLS/SSL` | Install SSL packages |
| External environment | `error: externally-managed-environment` | Use specific Python binary or virtual env |
| Port already in use | `Address already in use` | Change port or kill existing process |

## Performance Tips

1. **Use specific Python binary** to avoid path resolution overhead
2. **Run in background** for development: `nohup /usr/local/bin/python3.11 server.py &`
3. **Use gunicorn** for production: `gunicorn -w 4 -b 0.0.0.0:8000 server:app`
4. **Monitor logs** for debugging: `tail -f server.log`

## Security Considerations

1. **Don't run as root** in production
2. **Use HTTPS** for production deployments
3. **Set proper file permissions**
4. **Use environment variables** for sensitive data
5. **Enable CORS** only for necessary origins

## Related Documentation

- [Python Environment Troubleshooting](python-environment-troubleshooting.md)
- [Docker Best Practices](docker-best-practices.md)
- [Flask Application Configuration](flask-configuration.md) 