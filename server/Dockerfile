FROM node:24-slim

WORKDIR /app

# Install PM2 globally
RUN npm install -g pm2

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy server source code
COPY . .

# Expose port
EXPOSE 3001

# Start with PM2
CMD ["pm2-runtime", "start", "ecosystem.config.js"]
