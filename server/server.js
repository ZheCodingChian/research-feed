const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const db = require('./database/db');
const papersRouter = require('./routes/papers');
const corsMiddleware = require('./middleware/cors');

const app = express();
const PORT = process.env.PORT || 3001;

// Security: Helmet - Set secure HTTP headers
app.use(helmet());

// Security: Global rate limiter (100 requests per 15 minutes per IP)
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { success: false, error: 'Too many requests, please try again later' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Security: Strict rate limiter for API endpoints (30 requests per minute per IP)
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000,
  max: 30,
  message: { success: false, error: 'Too many API requests, please slow down' },
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply global rate limiter to all requests
app.use(globalLimiter);

// Middleware
app.use(corsMiddleware);
app.use(express.json());

// Routes (with stricter rate limiting for API endpoints)
app.use('/api/papers', apiLimiter, papersRouter);

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
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err.stack);

  const isDevelopment = process.env.NODE_ENV !== 'production';

  res.status(err.status || 500).json({
    success: false,
    error: isDevelopment ? err.message : 'Internal server error',
    ...(isDevelopment && { stack: err.stack })
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