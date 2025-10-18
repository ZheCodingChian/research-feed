const cors = require('cors');

const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = [
      'https://researchfeed.pages.dev',
      ...(process.env.ADDITIONAL_CORS_ORIGINS
        ? process.env.ADDITIONAL_CORS_ORIGINS.split(',').map(url => url.trim())
        : [])
    ];

    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(null, true);
    }
  },
  credentials: true,
  optionsSuccessStatus: 200
};

module.exports = cors(corsOptions);