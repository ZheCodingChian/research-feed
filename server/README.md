# Research Feed Server

## Overview

The Research Feed Server is an Express.js-based REST API that serves academic paper metadata from a SQLite database. It provides advanced filtering, sorting, and pagination capabilities for research papers with AI-generated metadata including topic relevance scores, impact assessments, and author h-index information. The server is designed to be deployed as a containerized application with PM2 process management.

## Table of Contents

1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Database and Data Processing Logic](#database-and-data-processing-logic)
6. [Validation](#validation)
7. [Security](#security)
8. [Dependencies](#dependencies)
9. [Environment Variables](#environment-variables)
10. [Logging](#logging)
11. [Error Handling](#error-handling)
12. [Setup and Deployment](#setup-and-deployment)
13. [Performance Considerations](#performance-considerations)
14. [Troubleshooting](#troubleshooting)

## File Structure

```
server/
├── database/
│   └── db.js                    # SQLite database interface and query logic
├── logs/
│   └── access.log               # Rotating HTTP access logs (auto-generated)
├── middleware/
│   └── cors.js                  # CORS configuration for allowed origins
├── routes/
│   └── papers.js                # Paper endpoints (/api/papers)
├── validation/
│   └── papersValidator.js       # Strict parameter validation for papers endpoint
├── .dockerignore                # Files to exclude from Docker builds
├── Dockerfile                   # Container image definition
├── ecosystem.config.js          # PM2 process manager configuration
├── package.json                 # npm dependencies and scripts
├── package-lock.json            # Locked dependency versions
└── server.js                    # Main application entry point
```

### File Purposes

- **server.js**: Application entry point that configures middleware, mounts routes, and starts the Express server
- **database/db.js**: Database abstraction layer containing all SQLite queries and data transformation logic
- **routes/papers.js**: API route handlers for paper-related endpoints with business logic
- **validation/papersValidator.js**: Comprehensive parameter validation with strict rules (no defaults, all required)
- **middleware/cors.js**: CORS middleware configuration for cross-origin requests
- **ecosystem.config.js**: PM2 configuration for production deployment
- **Dockerfile**: Multi-stage Docker build configuration for containerized deployment

## Architecture

### Request Flow

```
Client Request
    ↓
Helmet Security Headers
    ↓
Morgan Access Logging
    ↓
Global Rate Limiter (100 req/15min)
    ↓
CORS Middleware
    ↓
JSON Body Parser
    ↓
API Rate Limiter (30 req/min)
    ↓
Route Handler (/api/papers)
    ↓
Parameter Validation (papersValidator.js)
    ↓
Database Query (db.js)
    ↓
Data Transformation & Filtering
    ↓
JSON Response
```

### Key Architectural Decisions

1. **Singleton Database Pattern**: Database class is instantiated once and exported as a singleton
2. **Strict Validation**: All query parameters are required with no defaults to prevent ambiguous requests
3. **Parallel Query Execution**: Metadata queries run in parallel using `Promise.all()` for performance
4. **Field-Level Filtering**: Topic fields are nulled-out client-side based on selected topics to reduce payload size
5. **Proxy Trust**: Server trusts the first proxy (configured for Cloudflare/reverse proxy deployments)

## API Endpoints

### 1. GET /api/health

Health check endpoint for monitoring server availability.

**Response:**
```json
{
  "success": true,
  "message": "Research Feed API is running",
  "timestamp": "2025-10-13T12:00:00.000Z"
}
```

### 2. GET /api/papers/metadata

Retrieve metadata about papers grouped by date for landing page display.

**Response:**
```json
{
  "success": true,
  "metadata": {
    "all_dates": {
      "total_count": 1250,
      "must_read_count": 45,
      "should_read_count": 320
    },
    "dates": [
      {
        "date": "2025-10-12",
        "total_count": 25,
        "must_read_count": 2,
        "should_read_count": 8
      }
    ]
  }
}
```

### 3. GET /api/papers/details/:arxivId

Retrieve full details for a single paper by arXiv ID.

**Parameters:**
- `arxivId` (path): arXiv paper ID in format `YYMM.NNNNN` (e.g., `2501.12345`)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "2501.12345",
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "abstract": "Paper abstract...",
    "recommendation_score": "Must Read",
    "novelty_score": "Significant",
    "impact_score": "Substantial",
    "highest_h_index": 85,
    "average_h_index": 42.5
  }
}
```

### 4. GET /api/papers

**Main endpoint** for retrieving papers with advanced filtering, sorting, and pagination.

**All parameters are REQUIRED. No defaults are provided.**

#### Query Parameters

| Parameter | Type | Required | Description | Example Values |
|-----------|------|----------|-------------|----------------|
| `page` | integer | Yes | Page number (≥1) | `1` |
| `limit` | integer | Yes | Results per page (1-100) | `20` |
| `sortBy` | string | Yes | Field to sort by | `recommendation`, `relevance`, `highest_h_index`, `average_h_index`, `arxiv_id`, `title` |
| `sortOrder` | string | Yes | Sort direction | `asc`, `desc` |
| `date` | string | Yes | Date filter | `all` or `YYYY-MM-DD` |
| `topics` | string | Yes | Topic filter (CSV or special) | `all`, `clear`, or CSV: `agentic_ai,reinforcement_learning` |
| `recommendation` | string | Yes | Recommendation filter (CSV or special) | `all`, `clear`, or CSV: `must_read,should_read` |
| `impact` | string | Yes | Impact filter (CSV or special) | `all`, `clear`, or CSV: `transformative,substantial` |
| `novelty` | string | Yes | Novelty filter (CSV or special) | `all`, `clear`, or CSV: `groundbreaking,significant` |
| `relevance` | string | Yes | Relevance filter (CSV or special) | `all`, `clear`, or CSV: `highly,moderately` |
| `scoring` | string | Yes | Scoring status filter (CSV or special) | `all`, `clear`, or CSV: `completed` |
| `h_index_status` | string | Yes | H-index status filter (CSV or special) | `all`, `clear`, or CSV: `found,not_found` |
| `highest_h_index_range` | string | Yes | Highest h-index range | `all` or `min-max` format: `50-100` |
| `average_h_index_range` | string | Yes | Average h-index range | `all` or `min-max` format: `20-50` |

#### Filter Parameter Modes

Each filter parameter supports three modes:

1. **`all`**: No filtering (include all values)
2. **`clear`**: Exclude all values (return empty or impossible match)
3. **CSV**: Comma-separated list of allowed values (no spaces, case-sensitive)

#### Allowed Values

**Topics:**
- `agentic_ai`
- `proximal_policy_optimization`
- `reinforcement_learning`
- `reasoning_models`
- `inference_time_scaling`

**Recommendation:**
- `must_read`
- `should_read`
- `can_skip`
- `can_ignore`

**Impact:**
- `transformative`
- `substantial`
- `moderate`
- `negligible`

**Novelty:**
- `groundbreaking`
- `significant`
- `incremental`
- `minimal`

**Relevance:**
- `highly`
- `moderately`
- `tangentially`
- `not_relevant`

**Scoring:**
- `completed`
- `not_relevant_enough`

**H-Index Status:**
- `found`
- `not_found`

#### Example Request

```
GET /api/papers?page=1&limit=20&sortBy=recommendation&sortOrder=desc&date=2025-10-12&topics=agentic_ai,reinforcement_learning&recommendation=must_read,should_read&impact=all&novelty=all&relevance=highly&scoring=completed&h_index_status=found&highest_h_index_range=50-100&average_h_index_range=all
```

#### Response Format

```json
{
  "success": true,
  "data": {
    "papers": [
      {
        "id": "2501.12345",
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "abstract": "...",
        "published_date": "2025-10-12",
        "recommendation_score": "Must Read",
        "agentic_ai_score": 85,
        "agentic_ai_relevance": "Highly Relevant",
        "highest_h_index": 75,
        "average_h_index": 42.5
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalCount": 100,
      "limit": 20,
      "hasNextPage": true,
      "hasPrevPage": false
    },
    "metadata": {
      "startDate": "2025-10-12",
      "endDate": "2025-10-12",
      "totalPapers": 150,
      "maxHighestHIndex": 120,
      "maxAverageHIndex": 65
    },
    "appliedFilters": {
      "date": "2025-10-12",
      "topics": ["agentic_ai", "reinforcement_learning"],
      "recommendation": ["Must Read", "Should Read"],
      "scoring": ["completed"]
    },
    "sorting": {
      "sortBy": "recommendation",
      "sortOrder": "desc"
    }
  }
}
```

## Database and Data Processing Logic

### Database Schema

The server reads from a pre-populated SQLite database with the following key fields:

**Papers Table:**
- **Identifiers**: `id` (arXiv ID), `title`, `authors` (JSON), `categories` (JSON)
- **Content**: `abstract`, `summary`, `category_enhancement`
- **Publication**: `published_date`, `arxiv_url`, `pdf_url`
- **Status Fields**: `scraper_status`, `intro_status`, `embedding_status`, `llm_validation_status`, `llm_score_status`, `h_index_status`
- **Topic Scores**: `agentic_ai_score`, `proximal_policy_optimization_score`, etc.
- **Topic Relevance**: `agentic_ai_relevance`, `proximal_policy_optimization_relevance`, etc.
- **Topic Justifications**: `agentic_ai_justification`, `proximal_policy_optimization_justification`, etc.
- **Assessment Scores**: `novelty_score`, `impact_score`, `recommendation_score`
- **Assessment Justifications**: `novelty_justification`, `impact_justification`, `recommendation_justification`
- **Author Metrics**: `total_authors`, `authors_found`, `highest_h_index`, `average_h_index`, `notable_authors_count`, `author_h_indexes` (JSON)
- **External Links**: `semantic_scholar_url`

### Query Building

The database layer ([db.js:126-218](database/db.js#L126-L218)) uses a builder pattern for constructing WHERE clauses:

1. **Date Filtering**: Filters by `DATE(published_date)` when not "all"
2. **Status Filters**: Uses `IN` clauses for scoring/h-index status
3. **Assessment Filters**: Uses `IN` clauses for recommendation/impact/novelty scores
4. **Relevance Filtering**: Complex logic that checks selected topic relevance fields with OR conditions
5. **H-Index Range Filters**: Uses `BETWEEN` clauses for numeric ranges

### Sorting Logic

Complex sorting is implemented in [db.js:220-258](database/db.js#L220-L258):

- **Recommendation Sorting**: Uses CASE statement to map text values to numeric order, with tie-breakers (h-index, relevance)
- **Relevance Sorting**: Builds max relevance score across selected topics using CASE statements
- **H-Index Sorting**: Sorts numerically with `NULLS LAST`
- **Title/ID Sorting**: Basic alphabetical or ID-based sorting

### Data Transformations

1. **JSON Parsing**: Authors, categories, and h-index arrays are parsed from JSON strings
2. **Topic Field Nulling**: Unselected topic fields are set to `null` in response to reduce payload size
3. **Value Mapping**: API-friendly values (e.g., `must_read`) are mapped to DB values (e.g., `Must Read`)

### Parallel Query Execution

The main papers endpoint executes 5 queries in parallel ([papers.js:216-222](routes/papers.js#L216-L222)):
1. Get filtered papers (paginated)
2. Get total filtered count
3. Get total papers for date
4. Get date range (earliest/latest)
5. Get max h-index values for date

## Validation

All validation logic is centralized in [validation/papersValidator.js](validation/papersValidator.js).

### Validation Philosophy

- **All parameters required**: No defaults to prevent ambiguous queries
- **No trimming**: Values must be exact (no whitespace tolerance)
- **Case-sensitive**: All values are case-sensitive
- **Strict types**: Integers cannot have decimal points or leading zeros
- **No mixing modes**: Cannot mix "all"/"clear" with CSV values

### Validation Rules

**Page & Limit:**
- Must be positive integers
- Limit capped at 100
- Must not have leading zeros or decimals

**Sort Parameters:**
- `sortBy` must be exact match from allowed list
- `sortOrder` must be lowercase `asc` or `desc`

**Date:**
- Must be `all` or valid `YYYY-MM-DD` format
- Date validity is format-checked but not calendar-validated

**CSV Parameters (topics, recommendation, etc.):**
- Can be `all`, `clear`, or comma-separated values
- Cannot be empty string
- Cannot mix `all`/`clear` with other values
- Cannot have empty parts (e.g., `value1,,value2`)
- All values must be from allowed list (case-sensitive)

**H-Index Ranges:**
- Can be `all` or `min-max` format (e.g., `0-100`)
- Both min and max must be non-negative integers
- Min must be ≤ max

### Validation Response Format

**Success:**
```json
{
  "valid": true,
  "parsed": {
    "page": 1,
    "limit": 20,
    "topics": { "mode": "csv", "value": ["agentic_ai"] }
  }
}
```

**Failure:**
```json
{
  "valid": false,
  "error": "page must be a positive integer",
  "parameter": "page"
}
```

## Security

### Security Layers

1. **Helmet.js** ([server.js:26](server.js#L26))
   - Sets secure HTTP headers (CSP, X-Frame-Options, etc.)
   - Protects against common web vulnerabilities

2. **Rate Limiting** ([server.js:32-47](server.js#L32-L47))
   - **Global Limiter**: 100 requests per 15 minutes per IP
   - **API Limiter**: 30 requests per minute per IP for `/api/papers` endpoints
   - Returns JSON error responses when limits exceeded

3. **CORS Configuration** ([middleware/cors.js](middleware/cors.js))
   - Whitelist of allowed origins (localhost + production domain)
   - Credentials support enabled
   - Additional origins can be added via environment variable

4. **Proxy Trust** ([server.js:16](server.js#L16))
   - Configured to trust only the first proxy in chain
   - Essential for correct IP detection behind Cloudflare/reverse proxies
   - Ensures rate limiting works correctly

5. **Input Validation**
   - All inputs strictly validated before database queries
   - Prevents SQL injection via parameterized queries
   - Type checking and range validation

### Security Best Practices

- No sensitive data in logs (access logs only)
- Environment-based error messages (detailed in dev, generic in production)
- Graceful shutdown handlers for clean process termination
- Database connection properly closed on shutdown

## Dependencies

### Core Dependencies

- **express** (^4.18.2): Web framework
- **sqlite3** (^5.1.6): SQLite database driver
- **cors** (^2.8.5): CORS middleware
- **helmet** (^8.1.0): Security headers middleware
- **express-rate-limit** (^8.1.0): Rate limiting middleware
- **morgan** (^1.10.0): HTTP request logger
- **rotating-file-stream** (^3.2.3): Log file rotation

### Dev Dependencies

- **nodemon** (^3.0.1): Development auto-reload server

### Production Dependencies (Docker)

- **pm2**: Process manager (installed globally in Docker image)

## Environment Variables

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `PORT` | `3001` | Server listen port | `3001` |
| `NODE_ENV` | (none) | Environment mode | `production`, `development` |
| `ADDITIONAL_CORS_ORIGINS` | (none) | Comma-separated additional CORS origins | `https://example.com,https://staging.example.com` |

### Usage

```bash
# Development
export PORT=3001
export NODE_ENV=development
npm start

# Production with Docker
docker run -e NODE_ENV=production -e PORT=3001 -v /path/to/db:/data research-feed-server
```

## Logging

### Morgan HTTP Logs

- **Format**: Combined Apache-style logs
- **Location**: `logs/access.log`
- **Rotation**: Daily rotation via `rotating-file-stream`
- **Retention**: 14 days of logs retained

### Log Format Example

```
::1 - - [13/Oct/2025:12:00:00 +0000] "GET /api/papers?page=1&limit=20... HTTP/1.1" 200 1234 "-" "Mozilla/5.0..."
```

### Error Logging

- Unhandled errors logged to console with stack traces
- Error details exposed only in non-production environments
- 500 errors return generic message in production

## Error Handling

### Error Response Format

All errors follow a consistent JSON format:

```json
{
  "success": false,
  "error": "Error message here",
  "parameter": "field_name"  // (validation errors only)
}
```

### HTTP Status Codes

- **200**: Success
- **400**: Validation error (missing/invalid parameters)
- **404**: Resource not found (invalid paper ID, unknown endpoint)
- **429**: Rate limit exceeded
- **500**: Internal server error

### Error Handling Flow

1. **Validation Errors** ([papers.js:119-124](routes/papers.js#L119-L124)): Return 400 with parameter details
2. **Not Found Errors** ([papers.js:22-26](routes/papers.js#L22-L26)): Return 404 for missing papers
3. **Database Errors**: Caught in route handlers, return 500 with error details
4. **Unhandled Errors** ([server.js:77-87](server.js#L77-L87)): Global error handler catches all, sanitizes stack traces in production

## Setup and Deployment

### Local Setup

#### Prerequisites
- Node.js 24.x or higher
- SQLite database file at `/data/database.sqlite`

#### Installation

```bash
# Clone repository
git clone <repository-url>
cd research-feed/server

# Install dependencies
npm install

# Run development server (with auto-reload)
npm run dev

# Run production server
npm start
```

Server will be available at `http://localhost:3001`

### Docker Deployment

#### Build Image

```bash
cd server
docker build -t research-feed-server .
```

#### Run Container

```bash
docker run -d \
  --name research-feed-server \
  -p 3001:3001 \
  -v /path/to/database:/data \
  -e NODE_ENV=production \
  research-feed-server
```

#### Docker Compose Example

```yaml
version: '3.8'
services:
  server:
    build: ./server
    ports:
      - "3001:3001"
    volumes:
      - ./data:/data
    environment:
      - NODE_ENV=production
      - ADDITIONAL_CORS_ORIGINS=https://yourdomain.com
    restart: unless-stopped
```

### PM2 Deployment (Non-Docker)

#### Install PM2

```bash
npm install -g pm2
```

#### Start Server

```bash
cd server
pm2 start ecosystem.config.js
```

#### PM2 Management

```bash
# View logs
pm2 logs research-feed-server

# Restart server
pm2 restart research-feed-server

# Stop server
pm2 stop research-feed-server

# View status
pm2 status
```

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Ensure database file is mounted at `/data/database.sqlite`
- [ ] Configure reverse proxy (Nginx/Cloudflare) if needed
- [ ] Set `trust proxy` to correct hop count
- [ ] Configure CORS origins for production domain
- [ ] Set up log rotation and monitoring
- [ ] Configure firewall rules for port 3001
- [ ] Set appropriate rate limits for your use case
