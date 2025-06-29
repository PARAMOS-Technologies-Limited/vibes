FROM node:18-alpine

WORKDIR /app

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