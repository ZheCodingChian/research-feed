# Research Feed Frontend

A React-based web application for browsing and exploring curated research papers with advanced filtering, sorting, and scoring capabilities.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [File Structure](#file-structure)
- [Features](#features)
- [Pages](#pages)
- [Components](#components)
- [Hooks](#hooks)
- [State Management](#state-management)
- [Routing](#routing)
- [Setup and Deployment](#setup-and-deployment)

## Overview

The Research Feed frontend is a single-page application (SPA) built with React 19, TypeScript, and Vite. It provides an interface for browsing research papers from arXiv with AI-powered scoring, relevance ratings, and author h-index information.

**Tech Stack:**
- React 19 with TypeScript
- React Router v7 for routing
- TanStack Query (React Query) for data fetching and caching
- Tailwind CSS for styling
- Vite for build tooling
- Deployed on Cloudflare Pages

## Architecture

### Design Principles

**URL as Source of Truth:**
The application uses URL search parameters as the single source of truth for all filter and sort state. This design enables:
- Shareable filtered views (users can bookmark or share URLs)
- Browser back/forward navigation
- Persistent state across page refreshes

**Challenges and Solutions:**
- **Scroll Position:** Since filters trigger new data fetches and URL changes, scroll position is preserved using `sessionStorage` when navigating between pages and during "Load More" operations
- **Default Parameters:** Missing URL parameters are automatically initialized with defaults on mount to ensure consistent API calls

### Data Flow

```
User Interaction → URL Params Update → React Query → API Call → UI Update
                                            ↓
                                       Cache Layer (2hr TTL)
```

1. User interactions (filters, sorts) update URL search parameters
2. React Query observes URL changes via query keys
3. API calls are made with URL parameters
4. Response data is cached for 2 hours
5. Components render based on cached/fresh data

### Responsive Design

The app uses a mobile-first approach with custom breakpoints:
- **Mobile (<1050px):** Single-column stack layout with modals for filters/sort
- **Desktop (≥1050px):** Multi-column layout with inline filters and scrollable sections

## File Structure

```
frontend/
├── public/                          # Static assets
├── src/
│   ├── assets/
│   │   └── fonts/                   # Space Grotesk & Space Mono fonts
│   ├── components/
│   │   ├── common/                  # Reusable UI components
│   │   │   ├── Checkbox.tsx
│   │   │   ├── LaTeXText.tsx        # KaTeX math rendering
│   │   │   ├── LeftArrow.tsx
│   │   │   ├── RightArrow.tsx
│   │   │   └── TensorplexLogo.tsx
│   │   ├── date/                    # Landing page date cards
│   │   │   ├── AllTimeCard.tsx
│   │   │   ├── DateCard.tsx
│   │   │   ├── DateCardList.tsx
│   │   │   └── SkeletonDateCard.tsx
│   │   ├── error/                   # Error state components
│   │   │   ├── ExplorerPageError.tsx
│   │   │   └── LandingPageError.tsx
│   │   ├── filter/                  # Filter components
│   │   │   ├── FilterActionButton.tsx
│   │   │   ├── FilterColumn.tsx
│   │   │   ├── FilterHeader.tsx
│   │   │   ├── FilterSection.tsx
│   │   │   ├── HIndexRangeSlider.tsx
│   │   │   ├── MobileFilterModal.tsx
│   │   │   ├── MobileFilterSortButtons.tsx
│   │   │   └── PaperCountDisplay.tsx
│   │   ├── layout/                  # Layout/header components
│   │   │   ├── BrandHeader.tsx
│   │   │   ├── ExplorerHeader.tsx
│   │   │   └── PaperDetailsHeader.tsx
│   │   ├── paperCard/               # Paper list components
│   │   │   ├── ErrorPaperList.tsx
│   │   │   ├── PaperCard.tsx
│   │   │   ├── PaperCardList.tsx
│   │   │   └── SkeletonPaperCard.tsx
│   │   ├── paperDetails/            # Paper detail sections
│   │   │   ├── AbstractSection.tsx
│   │   │   ├── DesktopPaperMetadataSection.tsx
│   │   │   ├── MobilePaperMetadataSection.tsx
│   │   │   ├── PaperDetailsRightColumn.tsx
│   │   │   ├── PaperHIndexSection.tsx
│   │   │   ├── PaperIndividualAuthorHIndexSection.tsx
│   │   │   ├── PaperScoringSection.tsx
│   │   │   ├── PaperSimilarityScoresSection.tsx
│   │   │   ├── PaperTopicRelevanceSection.tsx
│   │   │   └── SummarySection.tsx
│   │   └── sort/                    # Sort components
│   │       ├── MobileSortModal.tsx
│   │       └── SortDropdown.tsx
│   ├── config/
│   │   └── api.ts                   # API base URL and endpoints
│   ├── constants/
│   │   ├── filterOptions.ts         # Filter option definitions
│   │   └── sortOptions.ts           # Sort option definitions
│   ├── hooks/
│   │   ├── useExplorerPapers.ts     # Infinite query for paper list
│   │   ├── useFilterReset.ts        # Filter reset logic
│   │   ├── usePaperDetails.ts       # Single paper query
│   │   ├── usePapersMetadata.ts     # Landing page metadata
│   │   └── useSortSelection.ts      # Sort state from URL
│   ├── pages/
│   │   ├── ExplorerPage.tsx         # Main paper browsing page
│   │   ├── LandingPage.tsx          # Date-based entry page
│   │   └── PaperDetails.tsx         # Individual paper view
│   ├── types/
│   │   └── api.ts                   # TypeScript type definitions
│   ├── utils/
│   │   ├── dateUtils.ts             # Date formatting utilities
│   │   ├── relevanceColors.ts       # Color mapping for relevance
│   │   └── scoreColors.ts           # Color mapping for scores
│   ├── App.tsx                      # Root component with routing
│   ├── main.tsx                     # Entry point with providers
│   └── index.css                    # Global styles and Tailwind
├── index.html
├── package.json
├── tailwind.config.js               # Tailwind configuration
├── tsconfig.json
├── vite.config.ts                   # Vite configuration
└── wrangler.toml                    # Cloudflare Pages config
```

## Features

### Core Functionality

1. **Paper Browsing:** Infinite scroll with pagination for browsing research papers
2. **Advanced Filtering:** Multi-dimensional filters for topics, scores, dates, and h-index
3. **Flexible Sorting:** Sort by recommendation, date, impact, novelty, or h-index metrics
4. **Paper Details:** Deep-dive view with summaries, abstracts, scoring breakdowns, and author h-indexes
5. **LaTeX Rendering:** Mathematical expressions rendered using KaTeX
6. **Responsive Design:** Optimized layouts for mobile and desktop

### Filter Categories

- **Date:** Filter by publication date or view all papers
- **Topics:** Agentic AI, PPO, Reinforcement Learning, Reasoning Models, Inference Time Scaling
- **Recommendation:** Must Read, Should Read, Can Skip
- **Impact Score:** Transformative, Substantial, Moderate, Negligible
- **Novelty Score:** Groundbreaking, Significant, Incremental, Minimal
- **Relevance:** Highly Relevant, Moderately Relevant, Tangentially Relevant, Not Relevant
- **Scoring Status:** Tracking AI validation status
- **H-Index Status:** Papers with validated author h-indexes
- **H-Index Ranges:** Min/max sliders for highest and average author h-indexes

### Sort Options

- Recommendation (default)
- Published Date
- Impact Score
- Novelty Score
- Highest H-Index
- Average H-Index

## Pages

### Landing Page (`/`)

**Purpose:** Entry point displaying paper counts organized by date

**Layout:**
- **Desktop:** Two-column layout with sticky branding header and scrollable date cards
- **Mobile:** Stacked layout with fixed header and scrollable date cards

**Components:**
- `BrandHeader`: Logo and title
- `DateCardList`: Collection of date cards showing paper counts
- `DateCard`: Individual date with paper statistics (Must Read, Should Read counts)
- `AllTimeCard`: Special card for viewing all papers

**Data:** Fetched via `usePapersMetadata()` hook from `/papers/metadata` endpoint

### Explorer Page (`/explorer`)

**Purpose:** Main browsing interface with filters, sorting, and infinite scroll

**Layout:**
- **Desktop:** Three-column layout
  - Left: Back arrow (fixed, 64px)
  - Middle: Filters with header (400px, scrollable)
  - Right: Sort dropdown + paper cards (flex, scrollable)
- **Mobile:** Single column with modals for filters/sort

**URL Parameters:**
All filter and sort state is stored in URL search params:
```
?date=2024-01-15
&topics=agentic_ai,reinforcement_learning
&recommendation=must_read,should_read
&impact=high
&novelty=all
&relevance=all
&scoring=all
&h_index_status=all
&highest_h_index_range=50-100
&average_h_index_range=all
&sortBy=recommendation
&sortOrder=desc
&limit=30
```

**Key Features:**
- Infinite scroll with "Load More" button
- Scroll position preservation during pagination
- Critical vs. non-critical error handling
- Shimmer loading states

**Data Flow:**
1. URL params are initialized with defaults on mount
2. `useExplorerPapers()` hook observes URL changes
3. Infinite query fetches paginated results
4. Pages are flattened into a single array for rendering

### Paper Details Page (`/paper/:id`)

**Purpose:** Detailed view of a single research paper

**Layout:**
- **Desktop:** Three-column layout
  - Left: Back arrow (fixed, 64px)
  - Middle: Title, summary, abstract (flex, scrollable)
  - Right: Metadata and scoring details (450px, scrollable)
- **Mobile:** Single column with all sections stacked

**Sections:**
1. **Header:** Title, authors, categories, publication date, arXiv/PDF links
2. **Summary:** AI-generated summary (if available)
3. **Abstract:** Full paper abstract with LaTeX rendering
4. **Scoring:** Recommendation, impact, novelty scores with justifications
5. **Topic Relevance:** Relevance levels and justifications for each topic
6. **Similarity Scores:** Numeric similarity scores per topic
7. **H-Index:** Aggregate statistics (highest, average, notable authors)
8. **Individual Author H-Indexes:** Per-author h-index values with Semantic Scholar links

**Navigation:**
- Back button returns to previous page (or landing page if no history)
- State preservation for scroll position via `sessionStorage`

**Data:** Fetched via `usePaperDetails(id)` hook from `/papers/details/:id` endpoint

## Components

### Common Components

#### `Checkbox`
Reusable checkbox with custom styling using Tailwind. Used throughout filters.

#### `LaTeXText`
Renders text with inline LaTeX math expressions using KaTeX. Automatically detects `$...$` and `$$...$$` patterns.

#### `LeftArrow` / `RightArrow`
Navigation arrow icons with hover states. Used for back navigation.

#### `TensorplexLogo`
SVG logo component displayed in the brand header.

### Filter Components

#### `FilterColumn`
Desktop filter sidebar containing all filter sections, paper count display, and action buttons.

#### `FilterSection`
Reusable checkbox group for a single filter category (e.g., Topics, Recommendation).

**Props:**
- `title`: Section heading
- `options`: Array of `{ label, value }` options
- `selectedValues`: Currently selected values
- `onSelectionChange`: Callback for selection changes

**URL Integration:** Reads from and writes to URL search params via `useSearchParams()`.

#### `HIndexRangeSlider`
Dual-handle range slider built with `rc-slider`. Allows users to filter papers by h-index ranges.

**Features:**
- Min/max handles
- Dynamic range based on API metadata
- Debounced URL updates
- Custom styling to match design system

#### `MobileFilterModal`
Full-screen modal for filters on mobile. Contains all filter sections in a scrollable container.

#### `PaperCountDisplay`
Shows filtered count vs. total count (e.g., "Showing 42 of 150 papers").

### Sort Components

#### `SortDropdown`
Desktop dropdown for sort options. Reads current sort from URL and updates on selection.

**Features:**
- Keyboard navigation (Escape to close, Enter/Space to toggle)
- Click-outside detection
- Animated arrow icon

#### `MobileSortModal`
Mobile modal with radio buttons for sort options.

### Paper Card Components

#### `PaperCard`
Card component for displaying a paper in the list view.

**Content:**
- Title (with LaTeX rendering)
- Authors (truncated with ellipsis)
- Published date
- Categories
- Recommendation badge
- Click-through to paper details

**State Preservation:**
On click, saves scroll position to `sessionStorage` for restoration when navigating back.

#### `PaperCardList`
Container for paper cards with infinite scroll logic.

**Props:**
- `papers`: Array of paper objects
- `isLoading`: Shows skeleton cards
- `onLoadMore`: Callback for pagination
- `hasMore`: Whether more pages exist
- `isLoadingMore`: Loading state for pagination
- `scrollRef`: Ref to scroll container
- `onBeforeLoadMore`: Callback to save scroll position

#### `SkeletonPaperCard`
Loading placeholder with shimmer animation using Tailwind CSS.

### Paper Details Components

#### `PaperDetailsHeader`
Paper title with LaTeX rendering, authors, categories, date, and external links.

#### `AbstractSection` / `SummarySection`
Collapsible sections for paper abstract and AI-generated summary.

#### `PaperScoringSection`
Displays recommendation, impact, and novelty scores with color-coded badges and justifications.

#### `PaperTopicRelevanceSection`
Grid of topic relevance levels with color-coded badges and expandable justifications.

#### `PaperSimilarityScoresSection`
Numeric similarity scores for each topic.

#### `PaperHIndexSection`
Aggregate h-index statistics (highest, average, total authors, authors found, notable authors).

#### `PaperIndividualAuthorHIndexSection`
Table of individual author h-indexes with links to Semantic Scholar profiles.

## Hooks

### `useExplorerPapers(filters, sortOptions, limit)`

Infinite query hook for fetching paginated papers.

**Parameters:**
- `filters`: Object containing all filter values from URL
- `sortOptions`: `{ sortBy, sortOrder }` from URL
- `limit`: Papers per page (default: 30)

**Returns:**
- `data`: Array of pages, each containing `{ papers, pagination, metadata }`
- `isLoading`: Initial loading state
- `isFetching`: Refetch loading state
- `fetchNextPage`: Function to load next page
- `hasNextPage`: Boolean indicating more pages
- `isFetchingNextPage`: Loading state for pagination
- `error`: Error object
- `refetch`: Manual refetch function

**Query Key:** `['papers', 'list', filters, sortOptions, limit]`
- Changes to any dependency trigger a refetch

**Cache Configuration:**
- `staleTime`: 2 hours
- `gcTime`: 2.5 hours
- `refetchOnWindowFocus`: false

### `usePapersMetadata()`

Fetches landing page metadata (paper counts by date).

**Returns:**
- `data`: `{ all_dates, dates }` with counts
- `isLoading`: Loading state
- `error`: Error object
- `refetch`: Manual refetch function

**Query Key:** `['papers', 'metadata']`

**Endpoint:** `GET /papers/metadata`

### `usePaperDetails(id)`

Fetches detailed information for a single paper.

**Parameters:**
- `id`: Paper ID from URL params

**Returns:**
- `data`: Full `Paper` object
- `isLoading`: Loading state
- `error`: Error object

**Query Key:** `['papers', 'details', id]`

**Endpoint:** `GET /papers/details/:id`

### `useSortSelection()`

Custom hook for managing sort state from URL.

**Returns:**
- `currentSort`: Current sort option key
- `handleSortChange`: Function to update sort in URL

**Implementation:**
- Reads `sortBy` and `sortOrder` from URL search params
- Updates both params when sort changes
- Constructs compound sort key (e.g., `recommendation_desc`)

### `useFilterReset()`

Hook for resetting all filters to defaults.

**Returns:**
- `handleReset`: Function to reset URL params to defaults

**Default Values:**
```javascript
{
  date: 'all',
  topics: 'all',
  recommendation: 'all',
  impact: 'all',
  novelty: 'all',
  relevance: 'all',
  scoring: 'all',
  h_index_status: 'all',
  highest_h_index_range: 'all',
  average_h_index_range: 'all',
}
```

## State Management

### Global State (React Query)

**Query Client Configuration:**
```javascript
{
  staleTime: 2 hours,
  gcTime: 2.5 hours,
  refetchOnWindowFocus: false,
  refetchOnMount: false
}
```

**Why React Query?**
- Automatic caching and cache invalidation
- Background refetching
- Optimistic updates
- Request deduplication
- Built-in loading and error states

### Local State (URL Search Params)

**All filter and sort state lives in the URL:**
- Single source of truth
- No need for global state management library
- Shareable, bookmarkable state
- Browser navigation works out of the box

**URL State Flow:**
```
User Action → setSearchParams() → URL Update → Query Key Change → Refetch
```

### Session Storage

**Used for scroll position preservation:**
- Key: `explorerScrollPosition`
- Value: `{ path, scrollTop, timestamp }`
- TTL: 5 minutes
- Cleared after successful restoration

## Routing

**Router:** React Router v7 with `BrowserRouter`

**Routes:**
```javascript
/ → LandingPage
/explorer → ExplorerPage
/paper/:id → PaperDetails
```

**Navigation Features:**
- State passing via `location.state` for back navigation
- URL-based state for filters/sort
- Programmatic navigation with `useNavigate()`
- Dynamic route params with `useParams()`

**Navigation Flow Example:**
1. User clicks date card on landing page → Navigate to `/explorer?date=2024-01-15`
2. User applies filters → URL updates with filter params
3. User clicks paper card → Navigate to `/paper/:id` with `state: { from: currentPath }`
4. User clicks back → Navigate to stored `from` path with scroll restoration

## Setup and Deployment

### Local Development

```bash
# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Deployment

The frontend is deployed to Cloudflare Pages using Wrangler.

```bash
# Deploy to preview environment
npm run deploy

# Deploy to production (main branch)
npm run deploy:production
```

**Configuration:** See [wrangler.toml](wrangler.toml)

### Environment

No environment variables required. API URL is hardcoded in [src/config/api.ts](src/config/api.ts).

To change the API endpoint, edit:
```typescript
const API_BASE_URL = 'https://yourDomain.com/api';
```

---

## Additional Notes

### Custom Scrollbars

The app uses `overlayscrollbars-react` for custom scrollbars on desktop:
- Auto-hide behavior (1.3s delay)
- Dark theme
- Smooth scrolling

### Typography

- **Headers:** Space Grotesk (variable weight)
- **Body:** Space Mono (monospace)
- Both fonts are self-hosted in `src/assets/fonts/`

### Color System

Custom neutral palette defined in Tailwind config:
- `neutral-100` to `neutral-900` (beige to black)
- Color-coded badges for scores (green, blue, orange, red)

### Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support in dropdowns
- Focus management in modals
