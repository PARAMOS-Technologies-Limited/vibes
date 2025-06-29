# Gemini Session Management

## Overview

The Gemini Session feature allows you to start interactive terminal sessions with the Gemini CLI (`gemini-cli`) inside branch containers. This is implemented using `ttyd` (a web-based terminal) to provide web-accessible terminal sessions.

## Features

- **Web-based Terminal**: Access Gemini CLI through a web browser
- **Branch Isolation**: Each branch gets its own terminal session
- **Automatic Port Assignment**: TTYD ports are automatically assigned (branch_port + 1000)
- **Session Persistence**: Session details are saved in branch metadata
- **Container Integration**: Sessions run inside the branch's Docker container

## API Endpoint

### Start Gemini Session

**Endpoint:** `POST /api/branch/{branch_name}/gemini-session`

**Description:** Starts a ttyd session with gemini-cli in the specified branch container.

**Prerequisites:**
- Branch must exist
- Branch container must be running

**Request:**
```bash
curl -X POST http://localhost:8000/api/branch/my-branch/gemini-session
```

**Response (Success - 200):**
```json
{
  "message": "Gemini session started successfully for branch my-branch",
  "branch_name": "my-branch",
  "ttyd_port": 9001,
  "ttyd_url": "http://localhost:9001",
  "gemini_command": "ttyd -o -W gemini",
  "access_url": "http://localhost:9001",
  "instructions": "Open the access_url in your browser to access the Gemini CLI terminal",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Response (Error - 400):**
```json
{
  "error": "Branch my-branch container is not running",
  "container_status": "stopped",
  "message": "Please start the branch container first using /api/branch/my-branch/start"
}
```

**Response (Error - 404):**
```json
{
  "error": "Branch my-branch not found"
}
```

## Usage Workflow

### 1. Create and Start a Branch

```bash
# Create a new branch
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{
    "branch_name": "feature-gemini-test",
    "gemini_api_key": "your-gemini-api-key",
    "auto_start": true
  }'

# Wait for branch to be ready (check status)
curl http://localhost:8000/api/branch/feature-gemini-test/status
```

### 2. Start Gemini Session

```bash
# Start the Gemini session
curl -X POST http://localhost:8000/api/branch/feature-gemini-test/gemini-session
```

### 3. Access the Terminal

Open the returned `access_url` in your web browser to access the Gemini CLI terminal.

## Technical Implementation

### Port Assignment

TTYD ports are automatically assigned using the formula:
```
ttyd_port = branch_port + 1000
```

**Examples:**
- Branch on port 8001 → TTYD on port 9001
- Branch on port 8002 → TTYD on port 9002
- Branch on port 8003 → TTYD on port 9003

### Container Commands

The session starts the following command inside the branch container:
```bash
ttyd -o -W -p {port} gemini
```

**Command Options:**
- `-o`: Enable once-only mode (session ends when client disconnects)
- `-W`: Enable websocket support
- `-p {port}`: Specify the port to listen on
- `gemini`: The command to run (gemini-cli)

### Session Metadata

Session information is automatically saved to the branch's `.branch` file:

```json
{
  "branch_name": "feature-gemini-test",
  "port": 8001,
  "ttyd_session": {
    "port": 9001,
    "url": "http://localhost:9001",
    "started_at": "2024-01-15T10:30:00.000Z",
    "command": "ttyd -o -W gemini"
  }
}
```

## Error Handling

### Common Error Scenarios

1. **Branch Not Found (404)**
   - Branch doesn't exist
   - Solution: Create the branch first

2. **Container Not Running (400)**
   - Branch container is stopped or failed to start
   - Solution: Start the branch container first

3. **TTYD Start Failure (500)**
   - Port conflict or ttyd installation issue
   - Solution: Check container logs and port availability

### Troubleshooting

**Check Container Status:**
```bash
curl http://localhost:8000/api/branch/{branch_name}/status
```

**Check Container Logs:**
```bash
curl http://localhost:8000/api/branch/{branch_name}/logs
```

**Restart Branch Container:**
```bash
curl -X POST http://localhost:8000/api/branch/{branch_name}/restart
```

## Security Considerations

- **Port Isolation**: Each branch gets its own isolated port
- **Container Isolation**: Sessions run inside the branch's Docker container
- **Once-only Mode**: Sessions end when the client disconnects
- **No Authentication**: TTYD sessions are accessible to anyone with the URL

## Dependencies

### Required Software

- **ttyd**: Web-based terminal (installed in Dockerfile)
- **gemini-cli**: Google Gemini CLI tool (installed via npm)
- **Docker**: Container runtime for isolation

### Installation

Both `ttyd` and `gemini-cli` are automatically installed in the Docker image:

```dockerfile
# Install ttyd from source
RUN apt-get update && \
    apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev && \
    git clone https://github.com/tsl0922/ttyd.git && \
    cd ttyd && mkdir build && cd build && \
    cmake .. && \
    make && make install

# Install gemini-cli globally
RUN npm install -g @google/gemini-cli
```

## Testing

Use the provided test script to verify the feature:

```bash
python test_gemini_session.py
```

The test script will:
1. Create a test branch
2. Wait for the container to be ready
3. Start a Gemini session
4. Verify the session details
5. Test error cases
6. Clean up the test branch

## Future Enhancements

Potential improvements for the Gemini session feature:

1. **Session Authentication**: Add authentication to TTYD sessions
2. **Session Management**: Add endpoints to list and stop sessions
3. **Custom Commands**: Allow custom commands instead of just `gemini`
4. **Session History**: Track session usage and history
5. **Multiple Sessions**: Support multiple concurrent sessions per branch
6. **Session Templates**: Pre-configured session templates for different use cases 