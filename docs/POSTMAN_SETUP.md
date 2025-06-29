# Hovel API Postman Collection

This document provides instructions for importing and using the Postman collection for the Hovel project APIs.

## Collection Overview

The Hovel API Collection includes endpoints for both:
1. **Main Server API** - Primary server for managing branches and system operations
2. **Branch App API** - Individual branch applications (Node.js Express apps)

## Import Instructions

### Step 1: Import the Collection
1. Open Postman
2. Click "Import" button
3. Select the `Hovel_API_Collection.json` file
4. The collection will be imported with all endpoints organized in folders

### Step 2: Set Up Environment Variables
The collection uses environment variables for flexible URL management:

1. In Postman, click on the collection name "Hovel API Collection"
2. Go to the "Variables" tab
3. Update the following variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `server_base_url` | `http://localhost:8000` | Base URL for the main server API |
| `branch_base_url` | `http://localhost:8001` | Base URL for branch app APIs (port varies by branch) |
| `branch_name` | `feature-branch` | Name of the branch to test |

## API Endpoints

### Main Server API

#### Basic Endpoints
- **GET /** - Get server information and status
- **GET /health** - Check if the server is healthy
- **GET /api/status** - Get API status and list of available endpoints
- **GET /api/data** - Get sample data from the server
- **POST /api/process** - Process incoming data

#### Branch Management Endpoints
- **POST /api/branch** - Create a new branch
- **GET /api/branches** - List all created branches
- **POST /api/branch/{branch_name}/start** - Start a branch container
- **POST /api/branch/{branch_name}/stop** - Stop a branch container
- **GET /api/branch/{branch_name}/status** - Get branch container status
- **GET /api/branch/{branch_name}/logs** - Get branch container logs
- **POST /api/branch/{branch_name}/restart** - Restart a branch container
- **DELETE /api/branch/{branch_name}** - Delete a branch completely

### Branch App API

#### Basic Endpoints
- **GET /** - Get branch app information and status
- **GET /health** - Check if the branch app is healthy

## Usage Examples

### 1. Create a New Branch
1. Select "Create Branch" from the Branch Management folder
2. Update the request body if needed:
```json
{
  "branch_name": "my-feature-branch",
  "auto_start": true
}
```
3. Send the request
4. Note the returned port number for the new branch

### 2. Test Branch App API
1. After creating a branch, update the `branch_base_url` variable with the correct port
   - Example: If the branch was created on port 8001, set `branch_base_url` to `http://localhost:8001`
2. Use the "Branch Root" or "Branch Health Check" endpoints to test the branch app

### 3. Manage Branch Lifecycle
1. **Start Branch**: Use "Start Branch" endpoint (update `branch_name` variable first)
2. **Check Status**: Use "Get Branch Status" to verify the container is running
3. **View Logs**: Use "Get Branch Logs" to see container logs
4. **Stop Branch**: Use "Stop Branch" when done testing
5. **Delete Branch**: Use "Delete Branch" to completely remove the branch

## Request Examples

### Create Branch Request
```json
POST {{server_base_url}}/api/branch
Content-Type: application/json

{
  "branch_name": "test-feature",
  "auto_start": true
}
```

### Process Data Request
```json
POST {{server_base_url}}/api/process
Content-Type: application/json

{
  "name": "test data",
  "value": 123,
  "description": "Sample data for processing"
}
```

### Get Branch Logs Request
```
GET {{server_base_url}}/api/branch/{{branch_name}}/logs?lines=50
```

## Environment Setup

### Prerequisites
1. Ensure the main server is running on port 8000
2. Docker and Docker Compose should be installed and running
3. The shared network `hovel-shared` should exist

### Starting the Main Server
```bash
# From the project root
python server.py
```

### Creating the Shared Network
```bash
docker network create hovel-shared
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the main server is running on the correct port
   - Check if the port is not blocked by firewall

2. **Branch Not Found**
   - Verify the branch name in the `branch_name` variable
   - Check if the branch was created successfully

3. **Container Not Starting**
   - Check Docker is running
   - Verify the shared network exists
   - Check container logs for errors

4. **Wrong Port for Branch**
   - After creating a branch, note the returned port number
   - Update the `branch_base_url` variable accordingly

### Debugging Tips

1. **Check Server Logs**: The main server logs all requests and responses
2. **Check Branch Logs**: Use the "Get Branch Logs" endpoint to see branch container logs
3. **Verify Network**: Ensure the `hovel-shared` Docker network exists
4. **Check Ports**: Verify no port conflicts by checking what's running on the ports

## Collection Features

- **Organized Structure**: Endpoints are grouped logically
- **Environment Variables**: Flexible URL management
- **Request Examples**: Pre-filled request bodies where applicable
- **Descriptions**: Each endpoint has a clear description
- **Query Parameters**: Properly configured for endpoints that need them

## Support

If you encounter issues with the API or Postman collection:
1. Check the server logs for error messages
2. Verify all prerequisites are met
3. Test with the basic health check endpoints first
4. Ensure Docker containers are running properly 