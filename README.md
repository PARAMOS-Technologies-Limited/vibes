# Hovel

A development environment API that spins up an AI agent-powered workspace, featuring an embeddable web terminal interface for seamless integration into web applications.

## Overview

Hovel is a Flask-based API server that provides a complete development environment management system. It includes advanced branch management capabilities that allow you to create isolated development environments for different features or experiments.

## Features

- **Main API Server**: Flask-based REST API with comprehensive endpoints
- **Branch Management System**: Create isolated development environments for different features
- **Docker Integration**: Full Docker support with automatic containerization
- **Git Integration**: Automatic git branch creation and management
- **Environment Isolation**: Each branch runs on its own port with complete environment isolation
- **Web Terminal Interface**: Embeddable terminal for web applications

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git (optional, for branch management)

### Running with Docker

```bash
# Clone the repository
git clone <repository-url>
cd hovel

# Start the main API server
docker-compose up
```

The API will be available at `http://localhost:8000`

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

## API Endpoints

### Core Endpoints

- `GET /` - Server information and status
- `GET /health` - Health check endpoint
- `GET /api/status` - API status and available endpoints
- `GET /api/data` - Sample data endpoint
- `POST /api/process` - Data processing endpoint

### Branch Management Endpoints

- `POST /api/branch` - Create a new development branch
- `GET /api/branches` - List all created branches

## Documentation

### 📚 [Branch Management System](docs/BRANCH_README.md)

Complete guide to the branch management system, including:
- Creating and managing development branches
- Environment isolation and port management
- Docker integration for branches
- Git workflow integration
- API usage examples

## Project Structure

```
hovel/
├── app/                          # Main application directory
│   ├── app.py                   # Flask application
│   ├── requirements.txt         # Python dependencies
│   └── docker-compose.template.yaml
├── branches/                    # Branch environments (created dynamically)
├── docs/                        # Documentation
│   └── BRANCH_README.md        # Branch management documentation
├── server.py                    # Main API server
├── run_branch.py               # Branch runner script
├── test_branch_system.py       # System test script
├── create_branch_compose.py    # Docker Compose generator
├── docker-compose.yaml         # Main Docker Compose
├── docker-compose.branch.template.yaml
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Development

### Creating a New Branch

```bash
# Create a new development branch
curl -X POST http://localhost:8000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"branch_name": "feature-new-ui"}'

# Run the branch application
python run_branch.py feature-new-ui
```

### Testing

```bash
# Run the test suite
python test_branch_system.py
```

## Configuration

### Environment Variables

- `FLASK_ENV` - Flask environment (development/production)
- `FLASK_APP` - Flask application entry point
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Docker Configuration

The project includes Docker support with:
- Multi-stage builds for optimization
- Git installation for branch management
- Volume mounting for development
- Environment variable configuration

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes: `python test_branch_system.py`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please refer to the documentation in the [docs/](docs/) directory or create an issue in the repository.
