const express = require('express');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 8000;

// Enable CORS
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Hello world route
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to the Node.js API!',
    status: 'running',
    branch: process.env.BRANCH_NAME || 'main'
  });
});

// Health check route
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Start the server
app.listen(3000, '0.0.0.0', () => {
  console.log(`Server is running on port 3000`);
  console.log(`Branch: ${process.env.BRANCH_NAME || 'main'}`);
}); 