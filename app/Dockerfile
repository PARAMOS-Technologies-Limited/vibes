FROM node:18-alpine

WORKDIR /app

# Install system dependencies including git
RUN apk add --no-cache git

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

# Expose port
EXPOSE 8000

# Run the application
CMD ["npm", "start"] 