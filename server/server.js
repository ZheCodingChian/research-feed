const express = require('express');
const db = require('./database/db');
const papersRouter = require('./routes/papers');
const corsMiddleware = require('./middleware/cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(corsMiddleware);
app.use(express.json());

// Routes
app.use('/api/papers', papersRouter);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    success: true, 
    message: 'Research Feed API is running',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// Error handler
app.use((err, req, res) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Start server
async function startServer() {
  try {
    await db.connect();
    
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
      console.log(`API endpoints:`);
      console.log(`   GET /api/health`);
      console.log(`   GET /api/papers`);
      console.log(`   GET /api/papers/metadata`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down server...');
  db.close();
  process.exit(0);
});

startServer();