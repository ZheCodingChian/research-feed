const cors = require('cors');

const corsOptions = {
  origin: [
    'http://localhost:3000',  // React dev server
    'http://localhost:3001',  // Alternative React port
    'http://localhost:5173',  // Vite dev server
    'http://localhost:5174',  // Vite dev server (alternative)
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:5174',
    ...(process.env.ADDITIONAL_CORS_ORIGINS
      ? process.env.ADDITIONAL_CORS_ORIGINS.split(',').map(url => url.trim())
      : [])
  ],
  credentials: true,
  optionsSuccessStatus: 200
};

module.exports = cors(corsOptions);