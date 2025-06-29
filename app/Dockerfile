FROM node:18

WORKDIR /app

# Install system dependencies and build ttyd from source
RUN apt-get update && \
    apt-get install -y build-essential cmake git libjson-c-dev libwebsockets-dev && \
    git clone https://github.com/tsl0922/ttyd.git && \
    cd ttyd && mkdir build && cd build && \
    cmake .. && \
    make && make install && \
    cd /app && \
    rm -rf ttyd && \
    apt-get remove -y build-essential cmake && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set git configuration with environment variables
ARG GIT_USER_NAME="Hovel Developer"
ARG GIT_USER_EMAIL="developer@hovel.dev"

# Configure git with the provided or default values
RUN git config --global user.name "${GIT_USER_NAME}" && \
    git config --global user.email "${GIT_USER_EMAIL}"

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Install gemini-cli globally
RUN npm install -g @google/gemini-cli

# Copy application code
COPY . .
COPY .gemini .gemini

# Run the application
CMD ["npm", "start"] 