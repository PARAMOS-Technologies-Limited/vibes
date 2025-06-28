FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including git and Docker
RUN apt-get update && apt-get install -y \
    git \
    libssl-dev \
    python3-openssl \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update && apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose v2
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Create docker group and add user to it
RUN groupadd -r docker || true

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a script to start Docker daemon and then the application
RUN echo '#!/bin/bash\n\
# Start Docker daemon in background\n\
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 &\n\
\n\
# Wait for Docker daemon to be ready\n\
until docker info > /dev/null 2>&1; do\n\
  echo "Waiting for Docker daemon..."\n\
  sleep 1\n\
done\n\
\n\
echo "Docker daemon is ready"\n\
\n\
# Start the Flask application\n\
exec python server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Run the start script instead of directly running the app
CMD ["/app/start.sh"] 