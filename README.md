# Research Feed

A full-stack application for scraping, analyzing and displaying AI research papers from arXiv.

Website at https://researchfeed.pages.dev/

## Architecture Overview

Research Feed consists of three main components that work together to deliver a complete research discovery experience:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Research Feed                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│    Pipeline      │───────> │  SQLite Database │ <────── │     Server       │
│   (Python)       │ writes  │ (database.sqlite)|  reads  │   (Node.js)      │
│                  │         │                  │         │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
   Daily Cron Job              Shared Storage                       │
   VPS Hosted                  VPS Volume                           │
                                                                    │
                                                              REST API
                                                                    │
                                                                    ▼
                                                          ┌──────────────────┐
                                                          │                  │
                                                          │    Frontend      │
                                                          │   (React SPA)    │
                                                          │                  │
                                                          └──────────────────┘
                                                           Cloudflare Pages
```

## System Components

### Pipeline
- **Purpose:** Automated data collection and AI-powered analysis
- **Technology:** Python
- **Hosting:** VPS (scheduled daily via cron)

The pipeline discovers new research papers from arXiv, extracts content, computes semantic similarity scores across 5 AI research topics, validates relevance using LLMs, scores papers on novelty and impact, and enriches data with author h-index information. All results are stored in a SQLite database.

See [pipeline/README.md](pipeline/README.md) for detailed documentation.

### Server
- **Purpose:** REST API for paper data
- **Technology:** Node.js (Express)
- **Hosting:** VPS (containerized with Docker + PM2)

The server provides a REST API with advanced filtering, sorting, and pagination capabilities. It reads from the shared SQLite database and serves paper metadata to the frontend with features like topic filtering, relevance scoring, and author impact metrics.

See [server/README.md](server/README.md) for detailed documentation.

### Frontend
- **Purpose:** Web interface for browsing papers
- **Technology:** React 19 (TypeScript + Vite)
- **Hosting:** Cloudflare Pages

The frontend is a single-page application that provides an intuitive interface for exploring research papers with real-time filtering, infinite scroll pagination, and detailed paper views. All filter state is stored in URL parameters for shareability.

See [frontend/README.md](frontend/README.md) for detailed documentation.

## Data Flow

```
1. Pipeline runs daily (automated cron job)
   ├─ Scrapes new papers from arXiv
   ├─ Analyzes content 
   └─ Writes to database.sqlite

2. Server reads from database.sqlite
   ├─ Provides REST API endpoints
   ├─ Handles filtering and sorting
   └─ Returns paginated results

3. Frontend fetches from Server API
   ├─ Displays papers in browsable interface
   ├─ Uses REST API endpoints from server
   └─ Shows detailed paper analysis
```

## Project Structure

```
research-feed/
├── pipeline/              # Python data processing pipeline
│   ├── src/
│   │   ├── main.py       # Pipeline orchestrator
│   │   ├── modules/      # Processing modules
│   │   └── config.py     # Configuration
│   └── database.sqlite   # Generated SQLite database
│
├── server/               # Node.js REST API
│   ├── server.js         # Express application entry point
│   ├── routes/           # API endpoints
│   ├── database/         # Database interface
│   ├── validation/       # Parameter validation
│   └── Dockerfile        # Container configuration
│
└── frontend/             # React web application
    ├── src/
    │   ├── pages/        # Route components
    │   ├── components/   # UI components
    │   ├── hooks/        # React Query hooks
    │   └── config/       # API configuration
    └── wrangler.toml     # Cloudflare Pages config
```

For detailed documentation on each component:
- [Pipeline Documentation](pipeline/README.md)
- [Server Documentation](server/README.md)
- [Frontend Documentation](frontend/README.md)
