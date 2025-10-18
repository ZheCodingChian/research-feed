const cors = require('cors');

const corsOptions = {
  origin: [
    'https://researchfeed.pages.dev',
    ...(process.env.ADDITIONAL_CORS_ORIGINS
      ? process.env.ADDITIONAL_CORS_ORIGINS.split(',').map(url => url.trim())
      : [])
  ],
  credentials: true,
  optionsSuccessStatus: 200
};

module.exports = cors(corsOptions);