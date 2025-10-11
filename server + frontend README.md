# Research Feed

A full-stack web application for browsing and filtering research papers with AI-powered scoring, topic relevance analysis, author h-index data, and LaTeX rendering capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Frontend Documentation](#frontend-documentation)
  - [Pages](#pages)
  - [Components](#components)
  - [Hooks](#hooks)
  - [State Management](#state-management)
  - [Routing](#routing)
- [Backend Documentation](#backend-documentation)
  - [API Endpoints](#api-endpoints)
  - [Database Schema](#database-schema)
  - [Server Architecture](#server-architecture)
- [Key Features Deep Dive](#key-features-deep-dive)
  - [Infinite Scroll with Position Restoration](#infinite-scroll-with-position-restoration)
  - [LaTeX Rendering](#latex-rendering)
  - [H-Index Range Sliders](#h-index-range-sliders)
  - [Advanced Filtering System](#advanced-filtering-system)
  - [Responsive Design](#responsive-design)
  - [URL-Driven State](#url-driven-state)
- [Data Flow](#data-flow)
- [Development Guide](#development-guide)
- [Configuration](#configuration)

---

## Overview

Research Feed is a modern web application designed for researchers, academics, and students who need to efficiently browse, filter, and discover relevant research papers. The application combines AI-powered paper scoring with advanced filtering capabilities to help users quickly identify must-read papers in their field.

### Who Is This For?

- **Researchers** looking to stay updated with the latest papers in specific topics
- **Academic institutions** wanting to track research trends
- **Students** exploring literature for their research
- **Anyone** interested in AI/ML research papers with intelligent filtering

### What Makes It Special?

- **AI-Powered Scoring**: Papers are automatically scored for recommendation level, novelty, and impact
- **Topic Relevance Analysis**: Multi-dimensional relevance scoring across 5 research topics
- **Author Metrics**: Automatic h-index fetching and analysis for all paper authors
- **LaTeX Support**: Full LaTeX rendering in titles, summaries, and abstracts
- **Advanced Filtering**: 9 different filter types with URL-based state management
- **Scroll Position Restoration**: Returns to exact scroll position when navigating back from paper details (supports both OverlayScrollbars and native scroll)
- **Responsive Design**: Optimized for both mobile and desktop viewing

---

## Features

### Core Features

1. **Daily Paper Statistics**
   - Aggregated view of papers by publication date
   - Must Read and Should Read counts per day
   - Date range overview

2. **Advanced Paper Explorer**
   - Filter by 9 different criteria
   - 6 sorting options (recommendation, relevance, h-index, ArXiv ID, title)
   - "Load More" pagination with scroll position preservation
   - Scroll position restoration when navigating back from paper details
   - Works seamlessly with both desktop (OverlayScrollbars) and mobile scroll

3. **Comprehensive Paper Details**
   - Full abstract with LaTeX rendering
   - AI-generated summary and justifications
   - Topic relevance scores with explanations
   - Author h-index data with profile links
   - Scoring metrics (recommendation, novelty, impact)
   - Direct links to ArXiv and PDF

4. **LaTeX Rendering**
   - KaTeX-powered rendering in titles, summaries, and abstracts
   - Inline and block-level equations
   - Fallback to raw LaTeX on errors

5. **Author H-Index Analysis**
   - Highest h-index among authors
   - Average h-index calculation
   - Per-author h-index data
   - Notable authors identification
   - Google Scholar profile links

### Advanced Features

1. **Intelligent Caching**
   - React Query with 2-hour cache
   - Eliminates duplicate API calls
   - Background refetching
   - Optimistic updates

2. **URL-Driven State Management**
   - All filters and sort options in URL
   - Shareable and bookmarkable views
   - Browser back/forward support
   - Deep linking to specific filtered views

3. **Mobile-First Design**
   - Responsive breakpoints (1050px for all pages)
   - Mobile modals for filters and sorting
   - Desktop filter columns and dropdowns
   - Touch-optimized interactions

4. **Custom Scrollbars**
   - OverlayScrollbars for desktop
   - Native scrollbars on mobile
   - Smooth scrolling experience

5. **Dual-Handle Range Sliders**
   - rc-slider for h-index filtering
   - Min and max range selection
   - Infinity support for unbounded ranges
   - Real-time value display

6. **Error Handling**
   - Critical vs non-critical error classification
   - Graceful degradation
   - User-friendly error messages
   - Retry mechanisms

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  React Application (Vite)                                  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Pages                                               │  │  │
│  │  │  - LandingPage (/)                                   │  │  │
│  │  │  - ExplorerPage (/explorer)                          │  │  │
│  │  │  - PaperDetails (/paper/:id)                         │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  State Management (React Query)                      │  │  │
│  │  │  - 2-hour cache                                      │  │  │
│  │  │  - Automatic refetching                              │  │  │
│  │  │  - Query deduplication                               │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Routing (React Router)                              │  │  │
│  │  │  - URL-driven state                                  │  │  │
│  │  │  - Query parameters for filters/sort                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      SERVER (Node.js/Express)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  API Routes                                                │  │
│  │  - GET /api/health                                         │  │
│  │  - GET /api/papers/metadata                                │  │
│  │  - GET /api/papers/details/:arxivId                        │  │
│  │  - GET /api/papers?[filters]                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Middleware                                                │  │
│  │  - CORS configuration                                      │  │
│  │  - JSON body parser                                        │  │
│  │  - Error handler                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Validation Layer                                          │  │
│  │  - Strict parameter validation (16 required params)        │  │
│  │  - CSV parsing and validation                              │  │
│  │  - H-index range validation                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Database Layer (SQLite)                                   │  │
│  │  - Dynamic query building                                  │  │
│  │  - Parameterized statements                                │  │
│  │  - Parallel query execution                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (SQLite)                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  papers table                                              │  │
│  │  - Core fields (id, title, authors, abstract, etc.)       │  │
│  │  - AI scoring (recommendation, novelty, impact)            │  │
│  │  - Topic relevance (5 topics × 3 fields each)             │  │
│  │  - H-index data (highest, average, per-author)            │  │
│  │  - Status fields (scraper, llm_score, llm_validation)     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Action → URL Update → React Query Cache Check → API Request
                                    │                      │
                                    │                      │
                              Cache Hit              Cache Miss
                                    │                      │
                                    │                      │
                              Instant Return      Server Validation
                                                          │
                                                          │
                                                   Dynamic SQL Build
                                                          │
                                                          │
                                                   Database Query
                                                          │
                                                          │
                                                   JSON Response
                                                          │
                                                          │
                                                   React Query Cache
                                                          │
                                                          │
                                                   Component Render
```

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1.1 | UI framework |
| **TypeScript** | 5.x | Type safety |
| **Vite** | Latest | Build tool and dev server |
| **TailwindCSS** | Latest | Utility-first styling |
| **React Query** | 5.90.2 | Server state management |
| **React Router** | 7.9.3 | Client-side routing |
| **KaTeX** | Latest | LaTeX rendering |
| **OverlayScrollbars** | Latest | Custom scrollbars (desktop) |
| **rc-slider** | Latest | Dual-handle range sliders |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | Latest LTS | Runtime environment |
| **Express** | 4.18.2 | Web framework |
| **SQLite3** | 5.1.6 | Database |
| **CORS** | Latest | Cross-origin resource sharing |

### Development Tools

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Git** - Version control

---

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher
- SQLite3

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/researchfeed-website.git
   cd researchfeed-website
   ```

2. **Install backend dependencies**
   ```bash
   cd server
   npm install
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd server
   npm start
   ```
   Server runs on `http://localhost:3000`

2. **Start the frontend dev server** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

3. **Access the application**

   Open your browser to `http://localhost:5173`

### Building for Production

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Preview production build**
   ```bash
   npm run preview
   ```

---

## Project Structure

```
researchfeed-website/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── AllTimeCard.tsx
│   │   │       ├── BrandHeader.tsx
│   │   │       ├── DateCard.tsx
│   │   │       ├── DateCardList.tsx
│   │   │       ├── ErrorLandingPage.tsx
│   │   │       ├── ExplorerHeader.tsx
│   │   │       ├── FilterColumn.tsx
│   │   │       ├── FilterSection.tsx
│   │   │       ├── HIndexRangeSlider.tsx
│   │   │       ├── HIndexRangeSlider.css
│   │   │       ├── LaTeXText.tsx
│   │   │       ├── LeftArrow.tsx
│   │   │       ├── MobileFilterModal.tsx
│   │   │       ├── MobileSortModal.tsx
│   │   │       ├── PaperCard.tsx
│   │   │       ├── PaperCardList.tsx
│   │   │       ├── PaperDetailsHeader.tsx
│   │   │       ├── RightArrow.tsx
│   │   │       ├── SkeletonDateCard.tsx
│   │   │       ├── SortDropdown.tsx
│   │   │       └── [40+ more components]
│   │   ├── hooks/
│   │   │   ├── useExplorerPapers.ts
│   │   │   ├── useFilterReset.ts
│   │   │   ├── usePaperDetails.ts
│   │   │   ├── usePapersMetadata.ts
│   │   │   └── useSortSelection.ts
│   │   ├── pages/
│   │   │   ├── ExplorerPage.tsx
│   │   │   ├── LandingPage.tsx
│   │   │   └── PaperDetails.tsx
│   │   ├── types/
│   │   │   └── api.ts
│   │   ├── config/
│   │   │   └── apiConfig.ts
│   │   ├── constants/
│   │   │   └── filterConstants.ts
│   │   ├── utils/
│   │   │   ├── dateUtils.ts
│   │   │   └── urlUtils.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── server/
│   ├── database/
│   │   ├── db.js
│   │   └── researchfeed.db
│   ├── routes/
│   │   └── papers.js
│   ├── middleware/
│   │   └── cors.js
│   ├── validation/
│   │   └── papersValidator.js
│   ├── server.js
│   ├── package.json
│   └── package-lock.json
└── README.md
```

---

## Frontend Documentation

### Pages

#### 1. LandingPage (`/`)

**File:** `frontend/src/pages/LandingPage.tsx`

**Purpose:** Entry point showing daily paper statistics with navigation to the explorer.

**Features:**
- Displays aggregated statistics across all dates
- Shows individual date cards with daily paper counts
- Responsive layout (mobile: vertical stack, desktop: two columns)
- Skeleton loading states
- Error handling with retry

**Data Flow:**
1. Component mounts
2. `usePapersMetadata()` hook fetches data
3. React Query checks cache (2-hour TTL)
4. Renders date cards or loading/error states

**Layout Structure:**

**Mobile:**
```
┌─────────────────────────┐
│   Brand Header          │
├─────────────────────────┤
│   All Time Card         │
├─────────────────────────┤
│   Date Card 1           │
├─────────────────────────┤
│   Date Card 2           │
├─────────────────────────┤
│   ...                   │
└─────────────────────────┘
```

**Desktop:**
```
┌──────────────┬──────────────────────────┐
│              │   All Time Card          │
│  Brand       ├──────────────────────────┤
│  Header      │   Date Card 1            │
│  (Sticky)    ├──────────────────────────┤
│              │   Date Card 2            │
│              ├──────────────────────────┤
│              │   ...                    │
└──────────────┴──────────────────────────┘
```

**Components Used:**
- `BrandHeader` - Logo and title
- `DateCardList` - Container for date cards
  - `AllTimeCard` - "View All Dates" card
  - `DateCard` - Individual date cards
  - `SkeletonDateCard` - Loading state
- `ErrorLandingPage` - Error state with retry

---

#### 2. ExplorerPage (`/explorer`)

**File:** `frontend/src/pages/ExplorerPage.tsx`

**Purpose:** Advanced filtering, sorting, and browsing of research papers.

**URL Parameters:**
```
/explorer?date=2025-03-17&sortBy=recommendation&sortOrder=desc&topics=agentic_ai&...
```

All state is in URL - no local state needed!

**Features:**
- Infinite scroll with automatic loading
- Scroll position restoration on back navigation
- 9 filter types (scoring, recommendation, impact, novelty, topics, relevance, h_index_status, highest_h_index_range, average_h_index_range)
- 6 sort options
- Mobile modals for filters and sort
- Desktop filter column and sort dropdown
- Real-time URL updates

**Responsive Behavior:**

**Mobile (< 1050px):**
- Header with date
- Filter button (opens modal)
- Sort button (opens modal)
- Scrollable paper list
- Modals overlay entire screen

**Desktop (>= 1050px):**
- Fixed filter column (left)
- Header with date
- Sort dropdown (top right)
- Scrollable paper list
- Custom overlay scrollbars

**Layout Structure:**

**Mobile:**
```
┌─────────────────────────────┐
│ [←] Date                     │
│ [Filter Button] [Sort Button]│
├─────────────────────────────┤
│                              │
│   Paper Card 1               │
│   Paper Card 2               │
│   Paper Card 3               │
│   ...                        │
│   [Loading Spinner]          │
│                              │
└─────────────────────────────┘
```

**Desktop:**
```
┌──────────┬──────────────────────────┐
│          │ [←] Date    [Sort ▼]     │
│ Filter   ├──────────────────────────┤
│ Column   │                           │
│          │   Paper Card 1            │
│ - Topics │   Paper Card 2            │
│ - H-Index│   Paper Card 3            │
│ - Scoring│   ...                     │
│ - Impact │   [Loading Spinner]       │
│ - ...    │                           │
│          │                           │
└──────────┴──────────────────────────┘
```

**Data Flow:**
1. Component reads URL parameters
2. Constructs filter object
3. `useExplorerPapers()` fetches data
4. React Query caches by full param set
5. URL change triggers automatic refetch
6. Infinite scroll appends pages

**Infinite Scroll Implementation:**
- Uses `useInfiniteQuery` from React Query
- Loads 20 papers per page
- Automatically fetches next page when user scrolls to bottom
- Stores scroll position before navigation
- Restores scroll position on back navigation

---

#### 3. PaperDetails (`/paper/:id`)

**File:** `frontend/src/pages/PaperDetails.tsx`

**Purpose:** Comprehensive view of a single research paper.

**Features:**
- Full paper metadata display
- LaTeX rendering in title, summary, and abstract
- AI-generated summary and justifications
- Topic relevance scores with explanations
- Author h-index data with profile links
- Scoring metrics (recommendation, novelty, impact)
- Links to ArXiv abstract and PDF
- Responsive layout (1050px breakpoint)

**Responsive Breakpoint:** 1050px (same as all pages)

**Layout Structure:**

**Mobile (< 1050px):**
```
┌─────────────────────────────┐
│ [←] Back to Explorer         │
├─────────────────────────────┤
│ Paper Title (LaTeX)          │
│ Authors                      │
│ Published Date               │
├─────────────────────────────┤
│ Recommendation Badge         │
│ Novelty Badge                │
│ Impact Badge                 │
├─────────────────────────────┤
│ H-Index Section              │
│ - Highest: 42                │
│ - Average: 28.5              │
│ - Per-Author Data            │
├─────────────────────────────┤
│ Summary Section              │
│ (AI-generated, LaTeX)        │
├─────────────────────────────┤
│ Abstract Section             │
│ (Full abstract, LaTeX)       │
├─────────────────────────────┤
│ Topic Relevance Section      │
│ - RLHF: Highly Relevant      │
│   Score: 0.89                │
│   Justification...           │
├─────────────────────────────┤
│ [View on ArXiv] [PDF]        │
└─────────────────────────────┘
```

**Desktop (>= 1050px):**
```
┌──────────────────────────────────────────┐
│ [←] Back to Explorer                      │
├──────────────────────────────────────────┤
│ Paper Title (LaTeX)                       │
│ Authors • Published Date                  │
├──────────────────────────────────────────┤
│ [Recommendation] [Novelty] [Impact]       │
├──────────────────────────────────────────┤
│ ┌──────────────┬─────────────────────────┤
│ │ H-Index      │ Summary (LaTeX)         │
│ │ - Highest    │ AI-generated summary... │
│ │ - Average    │                         │
│ │ - Authors    │                         │
│ └──────────────┴─────────────────────────┤
│                                           │
│ Abstract (LaTeX)                          │
│ Full abstract text...                     │
│                                           │
├──────────────────────────────────────────┤
│ Topic Relevance                           │
│ - RLHF: Highly Relevant (0.89)            │
│   Justification...                        │
├──────────────────────────────────────────┤
│ [View on ArXiv] [Download PDF]            │
└──────────────────────────────────────────┘
```

**Components Used:**
- `PaperDetailsHeader` - Title, authors, dates
- `ScoringSection` - Recommendation, novelty, impact badges
- `HIndexSection` - H-index statistics and author data
- `SummarySection` - AI-generated summary with LaTeX
- `AbstractSection` - Full abstract with LaTeX
- `TopicRelevanceSection` - Per-topic relevance scores
- `LaTeXText` - Renders LaTeX content

---

### Components

The application contains 50+ components organized in `frontend/src/components/ui/`. Below are the key components:

#### Navigation Components

##### `BrandHeader`
**File:** `frontend/src/components/ui/BrandHeader.tsx`

**Purpose:** Displays application logo and title.

**Props:** None

**Usage:**
```tsx
<BrandHeader />
```

---

##### `LeftArrow`
**File:** `frontend/src/components/ui/LeftArrow.tsx`

**Purpose:** Clickable back arrow for navigation.

**Props:**
```tsx
interface LeftArrowProps {
  className?: string;
}
```

**Behavior:**
- Navigates to previous page
- Hover effect (color transition)
- Responsive sizing

---

##### `RightArrow`
**File:** `frontend/src/components/ui/RightArrow.tsx`

**Purpose:** Right arrow icon used in cards.

**Props:** None

---

#### Header Components

##### `ExplorerHeader`
**File:** `frontend/src/components/ui/ExplorerHeader.tsx`

**Purpose:** Header for explorer page showing date and optional range.

**Props:**
```tsx
interface ExplorerHeaderProps {
  date: string;        // "all" or "YYYY-MM-DD"
  dateRange?: string;  // "17 March 2025 - 17 August 2025"
}
```

**Rendering Logic:**
- If `date === "all"`: Shows "All Dates" + date range
- If specific date: Shows formatted date (e.g., "Thursday, 17 March 2025")

---

##### `PaperDetailsHeader`
**File:** `frontend/src/components/ui/PaperDetailsHeader.tsx`

**Purpose:** Header for paper details page with title, authors, and metadata.

**Props:**
```tsx
interface PaperDetailsHeaderProps {
  paper: Paper;
}
```

**Features:**
- LaTeX rendering in title
- Author list
- Publication date
- ArXiv ID
- Categories

---

#### Card Components

##### `DateCard`
**File:** `frontend/src/components/ui/DateCard.tsx`

**Purpose:** Card showing daily paper statistics.

**Props:**
```tsx
interface DateCardProps {
  dateMetadata: {
    date: string;           // "2025-08-30"
    total_count: number;
    must_read_count: number;
    should_read_count: number;
  };
}
```

**Behavior:**
- Wraps in `<Link to="/explorer?date={date}">`
- Hover effect (background color change)
- Displays formatted date and counts

---

##### `AllTimeCard`
**File:** `frontend/src/components/ui/AllTimeCard.tsx`

**Purpose:** Card for "View All Dates" with aggregate statistics.

**Props:**
```tsx
interface AllTimeCardProps {
  allTimeMetadata: {
    total_count: number;
    must_read_count: number;
    should_read_count: number;
  };
  dateRange: {
    start: string;  // "2025-03-17"
    end: string;    // "2025-08-30"
  };
}
```

---

##### `PaperCard`
**File:** `frontend/src/components/ui/PaperCard.tsx`

**Purpose:** Displays individual paper with metadata and relevance indicators.

**Props:**
```tsx
interface PaperCardProps {
  paper: Paper;
}
```

**Visual Structure:**
```
┌─────────────────────────────────────────┐
│ 2509.00640          [Must Read Badge]   │
│                                          │
│ Paper Title (LaTeX Rendered)            │
│                                          │
│ Author 1, Author 2, Author 3            │
│                                          │
│ Abstract preview (truncated to 3 lines) │
│                                          │
│ [RLHF] [Weak Supervision] [Datasets]    │
└─────────────────────────────────────────┘
```

**Features:**
- LaTeX rendering in title and abstract
- Recommendation badge (Must Read = green, Should Read = blue)
- Topic tags (only shows Highly/Moderately/Tangentially Relevant)
- Hover effect (scales to 102%)
- Click navigates to paper details

**Topic Display Logic:**
Only displays topics where relevance is:
- "Highly Relevant"
- "Moderately Relevant"
- "Tangentially Relevant"

Filters out:
- "Not Relevant"
- "not_validated"
- "below_threshold"

---

##### `SkeletonDateCard`
**File:** `frontend/src/components/ui/SkeletonDateCard.tsx`

**Purpose:** Animated loading skeleton for date cards.

**Props:** None

**Usage:** Shown while metadata is loading.

---

#### Filter Components

##### `FilterColumn`
**File:** `frontend/src/components/ui/FilterColumn.tsx`

**Purpose:** Desktop-only filter sidebar with all filter sections.

**Props:** None (reads/writes URL params)

**Contains:**
- Topic filter checkboxes
- H-index range sliders
- Scoring status filter
- Recommendation filter
- Impact filter
- Novelty filter
- Relevance filter
- Reset filters button

**Behavior:**
- Fixed position on desktop
- Hidden on mobile (< 1050px)
- All changes update URL parameters
- URL changes trigger automatic data refetch

---

##### `FilterSection`
**File:** `frontend/src/components/ui/FilterSection.tsx`

**Purpose:** Collapsible section within filter column.

**Props:**
```tsx
interface FilterSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}
```

**Features:**
- Collapsible with arrow indicator
- Smooth animation
- Persists state in localStorage

---

##### `HIndexRangeSlider`
**File:** `frontend/src/components/ui/HIndexRangeSlider.tsx`

**Purpose:** Dual-handle range slider for h-index filtering.

**Props:**
```tsx
interface HIndexRangeSliderProps {
  label: string;           // "Highest H-Index" or "Average H-Index"
  min: number;             // Minimum value (e.g., 0)
  max: number;             // Maximum value (e.g., 200)
  currentMin: number | "inf";
  currentMax: number | "inf";
  onChange: (min: number | "inf", max: number | "inf") => void;
}
```

**Features:**
- rc-slider based implementation
- Dual handles (min and max)
- Infinity support ("inf" for unbounded)
- Real-time value display
- Custom styling (see `HIndexRangeSlider.css`)
- Debounced onChange to avoid excessive API calls

**Usage:**
```tsx
<HIndexRangeSlider
  label="Highest H-Index"
  min={0}
  max={200}
  currentMin={urlParams.get('highest_h_index_min')}
  currentMax={urlParams.get('highest_h_index_max')}
  onChange={(min, max) => {
    setUrlParams({
      highest_h_index_min: min,
      highest_h_index_max: max
    });
  }}
/>
```

---

##### `MobileFilterModal`
**File:** `frontend/src/components/ui/MobileFilterModal.tsx`

**Purpose:** Full-screen modal for filters on mobile.

**Props:**
```tsx
interface MobileFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Features:**
- Full-screen overlay
- All filter sections
- Apply/Cancel buttons
- Smooth slide-in animation
- Locks body scroll when open

---

##### `MobileSortModal`
**File:** `frontend/src/components/ui/MobileSortModal.tsx`

**Purpose:** Modal for sort options on mobile.

**Props:**
```tsx
interface MobileSortModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Features:**
- Bottom sheet style
- All 6 sort options with asc/desc
- Radio button selection
- Smooth slide-up animation

---

#### Sort Components

##### `SortDropdown`
**File:** `frontend/src/components/ui/SortDropdown.tsx`

**Purpose:** Desktop dropdown for sorting papers.

**Props:** None (reads/writes URL params)

**Features:**
- Click outside to close
- Arrow rotation animation
- Keyboard navigation (Space/Enter/Escape)
- ARIA accessibility
- Auto-width based on longest option

**Sort Options:**
1. Recommendation (Best First / Worst First)
2. Relevance (Highest to Lowest / Lowest to Highest)
3. Highest H-Index (Descending / Ascending)
4. Average H-Index (Descending / Ascending)
5. ArXiv ID (Descending / Ascending)
6. Title (A-Z / Z-A)

**State Management:**
- Reads `sortBy` and `sortOrder` from URL
- Updates URL on selection
- React Query automatically refetches

---

#### List Components

##### `DateCardList`
**File:** `frontend/src/components/ui/DateCardList.tsx`

**Purpose:** Renders list of date cards with loading/error states.

**Props:**
```tsx
interface DateCardListProps {
  data: PapersMetadataResponse | null;
  isLoading: boolean;
  refetch: () => void;
}
```

**Rendering Logic:**
1. If loading: Shows 10 skeleton cards
2. If no data: Shows error message
3. If data: Renders `AllTimeCard` + `DateCard[]`

---

##### `PaperCardList`
**File:** `frontend/src/components/ui/PaperCardList.tsx`

**Purpose:** Renders list of paper cards.

**Props:**
```tsx
interface PaperCardListProps {
  papers: Paper[];
}
```

**Rendering:**
- Vertical stack with gaps
- Maps over papers array
- Renders `PaperCard` for each

---

#### LaTeX Components

##### `LaTeXText`
**File:** `frontend/src/components/ui/LaTeXText.tsx`

**Purpose:** Renders text with LaTeX math expressions using KaTeX.

**Props:**
```tsx
interface LaTeXTextProps {
  text: string;
  className?: string;
  displayMode?: boolean;  // true for block equations, false for inline
}
```

**Features:**
- Detects LaTeX delimiters: `$...$`, `$$...$$`, `\(...\)`, `\[...\]`
- Renders math expressions with KaTeX
- Falls back to raw LaTeX on errors
- Supports both inline and display mode
- Handles escaped delimiters
- Error boundary for graceful degradation

**Usage:**
```tsx
<LaTeXText text="The equation $E = mc^2$ is famous." />
<LaTeXText text="$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$" displayMode={true} />
```

**Implementation:**
1. Parses text to find LaTeX delimiters
2. Splits into text and math segments
3. Renders text segments as-is
4. Renders math segments with KaTeX
5. Catches errors and displays raw LaTeX

---

#### Error Components

##### `ErrorLandingPage`
**File:** `frontend/src/components/ui/ErrorLandingPage.tsx`

**Purpose:** Error state display for landing page.

**Props:**
```tsx
interface ErrorLandingPageProps {
  error: string | null;
  refetch: () => void;
}
```

**Features:**
- Error message display
- Retry button
- Friendly error text

---

### Hooks

#### `usePapersMetadata`

**File:** `frontend/src/hooks/usePapersMetadata.ts`

**Purpose:** Fetch landing page metadata (dates + statistics).

**API Call:** `GET /api/papers/metadata`

**Returns:**
```tsx
{
  data: PapersMetadataResponse | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
  // ... other React Query properties
}
```

**Type Definition:**
```tsx
interface PapersMetadataResponse {
  success: boolean;
  metadata: {
    all_dates: {
      total_count: number;
      must_read_count: number;
      should_read_count: number;
    };
    dates: Array<{
      date: string;           // "2025-08-30"
      total_count: number;
      must_read_count: number;
      should_read_count: number;
    }>;
  };
}
```

**Caching:**
- Query Key: `['papers', 'metadata']`
- Stale Time: 2 hours
- Cache Time: 2.5 hours

**Usage:**
```tsx
const { data, isLoading, error, refetch } = usePapersMetadata();
```

---

#### `useExplorerPapers`

**File:** `frontend/src/hooks/useExplorerPapers.ts`

**Purpose:** Fetch filtered/sorted papers for explorer page.

**API Call:** `GET /api/papers?[filters]`

**Parameters:**
```tsx
interface ExplorerFilters {
  date: string;                           // "all" or "YYYY-MM-DD"
  topics: string;                         // "all", "clear", or CSV
  recommendation: string;                 // "all", "clear", or CSV
  impact: string;                         // "all", "clear", or CSV
  novelty: string;                        // "all", "clear", or CSV
  relevance: string;                      // "all", "clear", or CSV
  scoring: string;                        // "all", "clear", or CSV
  h_index_status: string;                 // "all", "clear", or CSV
  highest_h_index_min: number | "inf";
  highest_h_index_max: number | "inf";
  average_h_index_min: number | "inf";
  average_h_index_max: number | "inf";
}

interface SortOptions {
  sortBy: string;      // "recommendation", "relevance", etc.
  sortOrder: string;   // "asc" or "desc"
}
```

**Returns:**
```tsx
{
  data: {
    papers: Paper[];
    pagination: {
      currentPage: number;
      totalPages: number;
      totalCount: number;
      limit: number;
      hasNextPage: boolean;
      hasPrevPage: boolean;
    };
    appliedFilters: object;
    sorting: object;
  } | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  fetchNextPage: () => void;        // For infinite scroll
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
}
```

**Caching:**
- Query Key: `['papers', 'list', filters, sortOptions, page, limit]`
- Each unique combination is cached separately
- Stale Time: 2 hours
- Cache Time: 2.5 hours

**Usage:**
```tsx
const { data, isLoading, fetchNextPage, hasNextPage } = useExplorerPapers({
  filters: {
    date: "2025-03-17",
    topics: "agentic_ai,reinforcement_learning",
    recommendation: "must_read",
    // ... other filters
  },
  sortOptions: {
    sortBy: "recommendation",
    sortOrder: "desc"
  },
  page: 1,
  limit: 20
});
```

---

#### `usePaperDetails`

**File:** `frontend/src/hooks/usePaperDetails.ts`

**Purpose:** Fetch single paper details by ArXiv ID.

**API Call:** `GET /api/papers/details/:arxivId`

**Parameters:**
```tsx
arxivId: string  // e.g., "2509.00640"
```

**Returns:**
```tsx
{
  data: Paper | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
}
```

**Caching:**
- Query Key: `['paper', arxivId]`
- Stale Time: 2 hours
- Cache Time: 2.5 hours

**Usage:**
```tsx
const { id } = useParams();
const { data: paper, isLoading } = usePaperDetails(id);
```

---

#### `useFilterReset`

**File:** `frontend/src/hooks/useFilterReset.ts`

**Purpose:** Reset all filters to default values.

**Returns:**
```tsx
{
  resetFilters: () => void;
}
```

**Behavior:**
- Resets all URL parameters to defaults
- Preserves `date` and `sortBy`/`sortOrder`
- Clears all filter selections

**Usage:**
```tsx
const { resetFilters } = useFilterReset();

<button onClick={resetFilters}>Reset All Filters</button>
```

---

#### `useSortSelection`

**File:** `frontend/src/hooks/useSortSelection.ts`

**Purpose:** Manage sort state with URL synchronization.

**Returns:**
```tsx
{
  currentSort: {
    sortBy: string;
    sortOrder: string;
  };
  setSort: (sortBy: string, sortOrder: string) => void;
}
```

**Usage:**
```tsx
const { currentSort, setSort } = useSortSelection();

<SortDropdown
  current={currentSort}
  onChange={(by, order) => setSort(by, order)}
/>
```

---

### State Management

**Strategy:** React Query for server state, URL for client state.

#### Why React Query?

1. **Automatic Caching**
   - Eliminates duplicate API calls
   - Instant data on cache hits
   - Background refetching when stale

2. **Smart Cache Keys**
   - Each unique filter/sort combination cached separately
   - Automatic cache invalidation on parameter changes

3. **Built-in Loading/Error States**
   - No manual state management needed
   - Consistent patterns across components

4. **Query Deduplication**
   - Multiple components can call same hook
   - Only one API call made
   - All components receive same data

5. **Background Refetching**
   - Keeps data fresh without user action
   - Configurable stale time

#### Cache Configuration

**File:** `frontend/src/main.tsx`

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 60 * 2,      // 2 hours
      cacheTime: 1000 * 60 * 60 * 2.5,    // 2.5 hours
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    },
  },
});
```

**Cache Behavior:**

| Time | Behavior |
|------|----------|
| 0-2 hours | Data is fresh, uses cache (no API call) |
| 2-2.5 hours | Data is stale, uses cache + refetches in background |
| > 2.5 hours | Cache cleared, fresh API call on next request |

#### URL-Driven State

All client state (filters, sort) lives in URL parameters:

```
/explorer?date=2025-03-17&sortBy=recommendation&sortOrder=desc&topics=agentic_ai,reinforcement_learning&recommendation=must_read
```

**Benefits:**
1. **Shareable** - Copy URL to share exact view
2. **Bookmarkable** - Save specific filtered views
3. **Browser Navigation** - Back/forward buttons work perfectly
4. **No Prop Drilling** - Components read directly from URL
5. **Automatic Refetch** - URL change → cache key change → refetch

**Implementation:**

```tsx
// Read from URL
const [searchParams, setSearchParams] = useSearchParams();
const date = searchParams.get('date') || 'all';
const sortBy = searchParams.get('sortBy') || 'recommendation';

// Update URL (triggers automatic refetch)
setSearchParams({
  ...Object.fromEntries(searchParams),
  sortBy: 'title',
  sortOrder: 'asc'
});
```

---

### Routing

**Router:** React Router v7.9.3 (BrowserRouter)

**File:** `frontend/src/App.tsx`

**Routes:**

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `LandingPage` | Daily statistics and date cards |
| `/explorer` | `ExplorerPage` | Filtered paper browsing |
| `/paper/:id` | `PaperDetails` | Single paper view |

**Query Parameters (ExplorerPage):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | string | "all" | Date filter ("YYYY-MM-DD" or "all") |
| `sortBy` | string | "recommendation" | Sort field |
| `sortOrder` | string | "desc" | Sort direction |
| `topics` | string | "all" | Topic filter (CSV, "all", or "clear") |
| `recommendation` | string | "all" | Recommendation filter |
| `impact` | string | "all" | Impact filter |
| `novelty` | string | "all" | Novelty filter |
| `relevance` | string | "all" | Relevance filter |
| `scoring` | string | "all" | Scoring status filter |
| `h_index_status` | string | "all" | H-index status filter |
| `highest_h_index_min` | number/string | "0" | Min highest h-index |
| `highest_h_index_max` | number/string | "inf" | Max highest h-index |
| `average_h_index_min` | number/string | "0" | Min average h-index |
| `average_h_index_max` | number/string | "inf" | Max average h-index |

**Navigation Examples:**

```tsx
// Navigate to specific date
<Link to="/explorer?date=2025-03-17">View Papers</Link>

// Navigate to all dates
<Link to="/explorer?date=all">View All</Link>

// Navigate to paper details
<Link to={`/paper/${paper.id}`}>View Details</Link>

// Navigate back
navigate(-1);
```

---

## Backend Documentation

### API Endpoints

#### 1. Health Check

```
GET /api/health
```

**Purpose:** Verify API is running.

**Response:**
```json
{
  "success": true,
  "message": "Research Feed API is running",
  "timestamp": "2025-10-10T10:30:00.000Z"
}
```

**Status Codes:**
- `200` - Success

---

#### 2. Get Papers Metadata

```
GET /api/papers/metadata
```

**Purpose:** Get aggregated statistics for landing page.

**Response:**
```json
{
  "success": true,
  "metadata": {
    "all_dates": {
      "total_count": 2611,
      "must_read_count": 1,
      "should_read_count": 367
    },
    "dates": [
      {
        "date": "2025-08-30",
        "total_count": 102,
        "must_read_count": 0,
        "should_read_count": 15
      },
      {
        "date": "2025-08-29",
        "total_count": 98,
        "must_read_count": 1,
        "should_read_count": 12
      }
    ]
  }
}
```

**Fields:**
- `all_dates` - Aggregated stats across all papers
- `dates` - Array of daily statistics (sorted DESC by date)

**Status Codes:**
- `200` - Success
- `500` - Server error

---

#### 3. Get Paper Details

```
GET /api/papers/details/:arxivId
```

**Purpose:** Get complete details for a single paper.

**Parameters:**
- `arxivId` (path) - ArXiv paper ID (e.g., "2509.00640")

**Example:**
```
GET /api/papers/details/2509.00640
```

**Response:**
```json
{
  "success": true,
  "paper": {
    "id": "2509.00640",
    "title": "Paper Title with $\\LaTeX$ Math",
    "authors": ["Author 1", "Author 2"],
    "categories": ["cs.AI", "cs.LG"],
    "abstract": "Full abstract with $\\LaTeX$ equations...",
    "published_date": "2025-08-30T23:59:12+00:00",
    "arxiv_url": "http://arxiv.org/abs/2509.00640v1",
    "pdf_url": "http://arxiv.org/pdf/2509.00640v1",
    "recommendation_score": "Must Read",
    "novelty_score": "High",
    "impact_score": "Moderate",
    "summary": "AI-generated summary...",
    "recommendation_justification": "This paper...",
    "novelty_justification": "The approach...",
    "impact_justification": "This work...",
    "agentic_ai_score": 0.89,
    "agentic_ai_relevance": "Highly Relevant",
    "agentic_ai_justification": "This paper directly addresses...",
    "reinforcement_learning_score": 0.45,
    "reinforcement_learning_relevance": "Moderately Relevant",
    "reinforcement_learning_justification": "While not the primary focus...",
    "highest_h_index": 42,
    "average_h_index": 28.5,
    "total_authors": 5,
    "authors_found": 4,
    "notable_authors_count": 2,
    "author_h_indexes": [
      {
        "name": "Author 1",
        "h_index": 42,
        "profile_url": "https://scholar.google.com/citations?user=..."
      },
      {
        "name": "Author 2",
        "h_index": 35,
        "profile_url": "https://scholar.google.com/citations?user=..."
      }
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Paper not found
- `500` - Server error

---

#### 4. Get Filtered Papers

```
GET /api/papers?[filters]&[sorting]&[pagination]
```

**Purpose:** Get papers with advanced filtering, sorting, and pagination.

**IMPORTANT:** All 16 parameters are **required**. Missing parameters will return 400 error.

**Query Parameters:**

| Category | Parameter | Type | Required | Description |
|----------|-----------|------|----------|-------------|
| **Pagination** | `page` | integer | ✅ | Page number (1+) |
| | `limit` | integer | ✅ | Items per page (1-100) |
| **Sorting** | `sortBy` | string | ✅ | Sort field |
| | `sortOrder` | string | ✅ | Sort direction ("asc" or "desc") |
| **Filters** | `date` | string | ✅ | Date filter ("all" or "YYYY-MM-DD") |
| | `topics` | string | ✅ | Topic filter (CSV, "all", or "clear") |
| | `recommendation` | string | ✅ | Recommendation filter |
| | `impact` | string | ✅ | Impact filter |
| | `novelty` | string | ✅ | Novelty filter |
| | `relevance` | string | ✅ | Relevance filter |
| | `scoring` | string | ✅ | Scoring status filter |
| | `h_index_status` | string | ✅ | H-index status filter |
| | `highest_h_index_min` | number/string | ✅ | Min highest h-index (number or "inf") |
| | `highest_h_index_max` | number/string | ✅ | Max highest h-index (number or "inf") |
| | `average_h_index_min` | number/string | ✅ | Min average h-index (number or "inf") |
| | `average_h_index_max` | number/string | ✅ | Max average h-index (number or "inf") |

**Sort Options (sortBy):**

| Value | Description | Tie-Breakers |
|-------|-------------|--------------|
| `recommendation` | Recommendation level (Must Read first when desc) | 1. Highest H-Index<br>2. Average H-Index<br>3. Max Topic Relevance |
| `relevance` | Topic relevance score (checks selected topics) | 1. Recommendation<br>2. Highest H-Index<br>3. Average H-Index |
| `highest_h_index` | Highest author h-index | None (NULLs last) |
| `average_h_index` | Average author h-index | None (NULLs last) |
| `arxiv_id` | ArXiv ID (chronological) | None |
| `title` | Alphabetical by title (case-insensitive) | None |

**Filter Value Formats:**

All filter parameters accept:
1. **`"all"`** - No filtering (include all)
2. **`"clear"`** - Exclude all (empty results)
3. **CSV values** - Comma-separated list (case-sensitive, no spaces!)

**Valid CSV Values:**

| Parameter | Valid Values |
|-----------|--------------|
| `topics` | `agentic_ai`, `proximal_policy_optimization`, `reinforcement_learning`, `reasoning_models`, `inference_time_scaling` |
| `recommendation` | `must_read`, `should_read`, `can_skip`, `can_ignore` |
| `impact` | `high`, `moderate`, `low`, `negligible` |
| `novelty` | `high`, `moderate`, `low`, `none` |
| `relevance` | `highly`, `moderately`, `tangentially`, `not_relevant` |
| `scoring` | `completed`, `not_relevant_enough` |
| `h_index_status` | `found`, `not_found` |

**H-Index Range Rules:**
- Both min and max are required
- Accept numbers or `"inf"` (infinity)
- Min must be ≤ max
- Cannot both be `"inf"` (validation error)

**Example Requests:**

```bash
# Get all papers from a specific date, sorted by recommendation
GET /api/papers?date=2025-03-17&page=1&limit=20&sortBy=recommendation&sortOrder=desc&topics=all&recommendation=all&impact=all&novelty=all&relevance=all&scoring=all&h_index_status=all&highest_h_index_min=0&highest_h_index_max=inf&average_h_index_min=0&average_h_index_max=inf

# Filter for Must Read papers about Agentic AI with high h-index authors
GET /api/papers?date=all&page=1&limit=20&sortBy=recommendation&sortOrder=desc&topics=agentic_ai&recommendation=must_read&impact=all&novelty=all&relevance=highly&scoring=all&h_index_status=found&highest_h_index_min=50&highest_h_index_max=inf&average_h_index_min=0&average_h_index_max=inf

# Get papers sorted by h-index
GET /api/papers?date=all&page=1&limit=20&sortBy=highest_h_index&sortOrder=desc&topics=all&recommendation=all&impact=all&novelty=all&relevance=all&scoring=all&h_index_status=all&highest_h_index_min=0&highest_h_index_max=inf&average_h_index_min=0&average_h_index_max=inf
```

**Response:**
```json
{
  "success": true,
  "data": {
    "papers": [
      {
        "id": "2509.00640",
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "categories": ["cs.AI", "cs.LG"],
        "abstract": "Paper abstract...",
        "published_date": "2025-08-30T23:59:12+00:00",
        "arxiv_url": "http://arxiv.org/abs/2509.00640v1",
        "pdf_url": "http://arxiv.org/pdf/2509.00640v1",
        "recommendation_score": "Must Read",
        "novelty_score": "High",
        "impact_score": "Moderate",
        "summary": "LLM-generated summary",
        "agentic_ai_score": 0.89,
        "agentic_ai_relevance": "Highly Relevant",
        "agentic_ai_justification": "This paper...",
        "highest_h_index": 42,
        "average_h_index": 28.5,
        "author_h_indexes": [...]
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 15,
      "totalCount": 289,
      "limit": 20,
      "hasNextPage": true,
      "hasPrevPage": false
    },
    "appliedFilters": {
      "date": "2025-03-17",
      "topics": ["agentic_ai"],
      "recommendation": ["must_read"]
    },
    "sorting": {
      "sortBy": "recommendation",
      "sortOrder": "desc"
    }
  }
}
```

**Topics Filter - Special Behavior:**

Unlike other filters, `topics` has unique behavior:

1. **Does NOT filter papers out** - returns all papers matching other filters
2. **Controls response fields:**
   - `topics=all`: All topic fields included
   - `topics=clear`: All topic fields included, relevance filter skipped
   - `topics=agentic_ai,reinforcement_learning`: Only selected topic fields have values, others are `null`

3. **Affects relevance filtering:**
   - `topics=all` + `relevance=highly`: Checks all 5 topics
   - `topics=agentic_ai` + `relevance=highly`: Only checks Agentic AI relevance
   - `topics=clear` + `relevance=highly`: **Ignores relevance filter**

**Error Response:**
```json
{
  "success": false,
  "error": "Missing required parameter: topics",
  "parameter": "topics"
}
```

**Status Codes:**
- `200` - Success
- `400` - Validation error (missing/invalid parameters)
- `500` - Server error

---

### Database Schema

**Database:** SQLite3

**File:** `server/database/researchfeed.db`

**Table:** `papers`

#### Core Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | TEXT | ArXiv paper ID (PRIMARY KEY) | "2509.00640" |
| `title` | TEXT | Paper title (may contain LaTeX) | "Diffusion Models for $\\mathbb{R}^n$" |
| `authors` | TEXT | JSON array of author names | `["Author 1", "Author 2"]` |
| `categories` | TEXT | JSON array of ArXiv categories | `["cs.AI", "cs.LG"]` |
| `abstract` | TEXT | Full abstract (may contain LaTeX) | "We propose..." |
| `published_date` | TEXT | ISO datetime of publication | "2025-08-30T23:59:12+00:00" |
| `arxiv_url` | TEXT | ArXiv abstract URL | "http://arxiv.org/abs/2509.00640v1" |
| `pdf_url` | TEXT | PDF download URL | "http://arxiv.org/pdf/2509.00640v1" |

#### AI Scoring Fields

| Field | Type | Values |
|-------|------|--------|
| `recommendation_score` | TEXT | "Must Read", "Should Read", "Can Skip", "Ignore", NULL |
| `novelty_score` | TEXT | "High", "Moderate", "Low", "None", NULL |
| `impact_score` | TEXT | "High", "Moderate", "Low", "Negligible", NULL |
| `summary` | TEXT | AI-generated summary or NULL |
| `recommendation_justification` | TEXT | Explanation for recommendation or NULL |
| `novelty_justification` | TEXT | Explanation for novelty or NULL |
| `impact_justification` | TEXT | Explanation for impact or NULL |

#### Topic Relevance Fields

For each of 5 topics, there are 3 fields:

**Topics:**
1. `agentic_ai` - Agentic AI
2. `proximal_policy_optimization` - Proximal Policy Optimization (PPO)
3. `reinforcement_learning` - Reinforcement Learning
4. `reasoning_models` - Reasoning Models
5. `inference_time_scaling` - Inference Time Scaling

**Fields per topic:**

| Field Pattern | Type | Description |
|---------------|------|-------------|
| `{topic}_score` | REAL | Similarity score (0.0-1.0) |
| `{topic}_relevance` | TEXT | "Highly Relevant", "Moderately Relevant", "Tangentially Relevant", "Not Relevant", "not_validated", "below_threshold" |
| `{topic}_justification` | TEXT | AI explanation of relevance |

**Example:**
```
agentic_ai_score = 0.89
agentic_ai_relevance = "Highly Relevant"
agentic_ai_justification = "This paper directly addresses agentic AI by proposing..."
```

#### H-Index Fields

| Field | Type | Description |
|-------|------|-------------|
| `h_index_status` | TEXT | "not_fetched", "completed", "failed" |
| `highest_h_index` | INTEGER | Highest h-index among all authors |
| `average_h_index` | REAL | Average h-index of all authors |
| `total_authors` | INTEGER | Total number of authors on paper |
| `authors_found` | INTEGER | Number of authors found in Google Scholar |
| `notable_authors_count` | INTEGER | Number of authors with h-index > threshold |
| `author_h_indexes` | TEXT | JSON array of per-author data |

**`author_h_indexes` JSON structure:**
```json
[
  {
    "name": "Author 1",
    "h_index": 42,
    "profile_url": "https://scholar.google.com/citations?user=ABC123"
  },
  {
    "name": "Author 2",
    "h_index": 35,
    "profile_url": "https://scholar.google.com/citations?user=DEF456"
  }
]
```

#### Status Fields

| Field | Type | Values |
|-------|------|--------|
| `scraper_status` | TEXT | "initial", "successfully_scraped", "scraping_failed" |
| `llm_score_status` | TEXT | "not_scored", "completed", "failed", "not_relevant_enough" |
| `llm_validation_status` | TEXT | "not_validated", "completed", "failed" |

#### Database Schema SQL

```sql
CREATE TABLE papers (
  id TEXT PRIMARY KEY,
  title TEXT,
  authors TEXT,
  categories TEXT,
  abstract TEXT,
  published_date TEXT,
  arxiv_url TEXT,
  pdf_url TEXT,

  -- AI Scoring
  recommendation_score TEXT,
  novelty_score TEXT,
  impact_score TEXT,
  summary TEXT,
  recommendation_justification TEXT,
  novelty_justification TEXT,
  impact_justification TEXT,

  -- Topic Relevance (5 topics × 3 fields = 15 fields)
  agentic_ai_score REAL,
  agentic_ai_relevance TEXT,
  agentic_ai_justification TEXT,
  proximal_policy_optimization_score REAL,
  proximal_policy_optimization_relevance TEXT,
  proximal_policy_optimization_justification TEXT,
  reinforcement_learning_score REAL,
  reinforcement_learning_relevance TEXT,
  reinforcement_learning_justification TEXT,
  reasoning_models_score REAL,
  reasoning_models_relevance TEXT,
  reasoning_models_justification TEXT,
  inference_time_scaling_score REAL,
  inference_time_scaling_relevance TEXT,
  inference_time_scaling_justification TEXT,

  -- H-Index
  h_index_status TEXT,
  highest_h_index INTEGER,
  average_h_index REAL,
  total_authors INTEGER,
  authors_found INTEGER,
  notable_authors_count INTEGER,
  author_h_indexes TEXT,

  -- Status
  scraper_status TEXT,
  llm_score_status TEXT,
  llm_validation_status TEXT
);
```

---

### Server Architecture

**File Structure:**
```
server/
├── server.js              # Express app entry point
├── package.json           # Dependencies & scripts
├── database/
│   ├── db.js              # Database class with query methods
│   └── researchfeed.db    # SQLite database file
├── routes/
│   └── papers.js          # API route handlers
├── middleware/
│   └── cors.js            # CORS configuration
└── validation/
    └── papersValidator.js # Parameter validation
```

#### `server.js` - Main Entry Point

**File:** `server/server.js`

**Responsibilities:**
- Initialize Express app
- Load middleware (CORS, JSON parser)
- Mount API routes
- Provide health check endpoint
- Handle 404s and errors
- Connect to database on startup
- Graceful shutdown handler

**Structure:**
```javascript
const express = require('express');
const cors = require('./middleware/cors');
const papersRouter = require('./routes/papers');
const Database = require('./database/db');

const app = express();

// Middleware
app.use(cors);
app.use(express.json());

// Routes
app.use('/api/papers', papersRouter);
app.get('/api/health', (req, res) => { ... });

// Error handlers
app.use((req, res) => { /* 404 */ });
app.use((err, req, res, next) => { /* 500 */ });

// Startup
Database.getInstance().connect()
  .then(() => {
    app.listen(PORT, () => console.log(`Server running on ${PORT}`));
  });

// Graceful shutdown
process.on('SIGTERM', () => { ... });
```

---

#### `database/db.js` - Database Layer

**File:** `server/database/db.js`

**Pattern:** Singleton class managing SQLite connection.

**Public Methods:**

##### `connect()`
Establishes SQLite connection.

```javascript
await db.connect();
```

##### `getDateMetadata()`
Get paper counts per date for landing page.

**Returns:**
```javascript
[
  { date: "2025-08-30", total_count: 102, must_read_count: 0, should_read_count: 15 },
  { date: "2025-08-29", total_count: 98, must_read_count: 1, should_read_count: 12 }
]
```

##### `getAllDatesMetadata()`
Get aggregated counts across all dates.

**Returns:**
```javascript
{
  total_count: 2611,
  must_read_count: 1,
  should_read_count: 367
}
```

##### `getDateRange()`
Get min/max published dates.

**Returns:**
```javascript
{
  earliest: "2025-03-17",
  latest: "2025-08-30"
}
```

##### `getPapersWithFilters(filters, sortOptions, pagination)`
Main query with dynamic filtering and sorting.

**Parameters:**
```javascript
{
  filters: {
    date: "2025-03-17",
    topics: ["agentic_ai", "reinforcement_learning"],
    recommendation: ["Must Read"],
    // ... other filters
  },
  sortOptions: {
    sortBy: "recommendation",
    sortOrder: "desc"
  },
  pagination: {
    page: 1,
    limit: 20
  }
}
```

**Returns:**
```javascript
{
  papers: [...],
  pagination: {
    currentPage: 1,
    totalPages: 15,
    totalCount: 289,
    // ...
  }
}
```

##### `getFilteredCount(filters)`
Count papers matching filters (for pagination).

**Returns:** `number`

##### `close()`
Close database connection.

**Private Helper Methods:**

##### `_buildWhereClause(filters)`
Builds dynamic WHERE clause with parameterized values.

**Features:**
- Handles date filtering
- Handles all filter types
- Special handling for `topics=null` (clear mode - skips relevance)
- H-index range filtering with Infinity support
- Returns `{ whereClause, params }` for safe query building

**Example:**
```javascript
const { whereClause, params } = this._buildWhereClause({
  date: "2025-03-17",
  recommendation: ["Must Read", "Should Read"],
  highest_h_index_min: 50,
  highest_h_index_max: Infinity
});

// whereClause = "WHERE DATE(published_date) = ? AND recommendation_score IN (?, ?) AND highest_h_index >= ?"
// params = ["2025-03-17", "Must Read", "Should Read", 50]
```

##### `_buildOrderByClause(sortBy, sortOrder, topics)`
Builds ORDER BY clause with special logic.

**Features:**
- Special handling for recommendation (flips order - "Must Read" = best)
- Delegates to `_buildRelevanceOrderBy` for relevance sorting
- Handles h-index, arxiv_id, title sorting

**Example:**
```javascript
const orderBy = this._buildOrderByClause("recommendation", "desc", undefined);
// Returns: "ORDER BY CASE recommendation_score WHEN 'Must Read' THEN 1 WHEN 'Should Read' THEN 2 ... END ASC"
```

##### `_buildRelevanceOrderBy(topics, order)`
Builds relevance-based ORDER BY with CASE statement.

**Features:**
- Creates CASE statement checking topic relevance fields
- Only checks selected topics (or all if `topics=undefined`)
- Returns highest relevance rank across checked topics

**Example:**
```javascript
const orderBy = this._buildRelevanceOrderBy(["agentic_ai", "reinforcement_learning"], "desc");
// Returns: "ORDER BY CASE WHEN agentic_ai_relevance = 'Highly Relevant' OR reinforcement_learning_relevance = 'Highly Relevant' THEN 4 ... END DESC, [recommendation tie-breaker], [h-index tie-breakers]"
```

**Key Features:**
- **Parameterized queries** - All queries use `?` placeholders for SQL injection protection
- **Parallel execution** - Papers + count queries run simultaneously
- **JSON parsing** - Automatically parses authors, categories, author_h_indexes
- **Infinity handling** - Skips bounds if value is `Infinity`

---

#### `routes/papers.js` - API Route Handlers

**File:** `server/routes/papers.js`

**Endpoints:**
1. `GET /api/papers` - Main filtering/sorting/pagination endpoint
2. `GET /api/papers/metadata` - Landing page metadata
3. `GET /api/papers/details/:arxivId` - Single paper details

**Helper Functions:**

##### `mapFilterValues(filterType, values)`
Maps API values to database values.

**Mappings:**

| API Value | Database Value |
|-----------|----------------|
| `must_read` | "Must Read" |
| `should_read` | "Should Read" |
| `can_skip` | "Can Skip" |
| `can_ignore` | "Ignore" |
| `high` | "High" |
| `moderate` | "Moderate" |
| `low` | "Low" |
| `negligible` | "Negligible" (impact) |
| `none` | "None" (novelty) |
| `highly` | "Highly Relevant" |
| `moderately` | "Moderately Relevant" |
| `tangentially` | "Tangentially Relevant" |
| `not_relevant` | "Not Relevant" |
| `found` | "completed" (h_index_status) |
| `not_found` | ["not_fetched", "failed"] |

##### `filterTopicFields(papers, topicsMode, topicsValues)`
Nulls unselected topic fields in response.

**Logic:**
- If `mode=all` or `mode=clear`: Returns all fields
- If `mode=csv`: Nulls out unselected topic fields

**Example:**
```javascript
// User selects: topics=agentic_ai,reinforcement_learning
filterTopicFields(papers, "csv", ["agentic_ai", "reinforcement_learning"]);

// Result: proximal_policy_optimization_*, reasoning_models_*, inference_time_scaling_* are set to null
```

**Request Flow:**

```
1. Request arrives
   ↓
2. validateAllParameters(queryParams)
   - Returns 400 if invalid
   ↓
3. Parse parameters into filters object
   ↓
4. Handle "all"/"clear"/"csv" modes
   - "all" → undefined (no filtering)
   - "clear" → ['__IMPOSSIBLE_VALUE__'] OR null (topics)
   - CSV → Map to DB values
   ↓
5. Execute parallel DB queries
   - getPapersWithFilters()
   - getFilteredCount()
   ↓
6. Filter topic fields based on topics mode
   ↓
7. Return formatted response
```

**Special Handling:**
- `topics=clear` sets `filters.topics = null` to skip relevance filtering
- H-index `Infinity` values passed directly to DB layer

---

#### `middleware/cors.js` - CORS Configuration

**File:** `server/middleware/cors.js`

**Purpose:** Configure Cross-Origin Resource Sharing for frontend access.

**Allowed Origins:**
- `http://localhost:3000` (React dev server)
- `http://localhost:3001` (Alternative)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174` (Vite alternative)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`
- Additional origins via `ADDITIONAL_CORS_ORIGINS` env var (comma-separated)

**Settings:**
```javascript
{
  origin: function (origin, callback) { ... },
  credentials: true,
  optionsSuccessStatus: 200
}
```

---

#### `validation/papersValidator.js` - Strict Validation

**File:** `server/validation/papersValidator.js`

**Purpose:** Comprehensive parameter validation enforcing strict API rules.

**Validation Rules:**
- **All 16 parameters required** - No defaults
- **Case-sensitive** - Exact matches only
- **No trimming** - Spaces matter
- **No mixing** - Cannot mix "all"/"clear" with CSV

**Functions:**

##### `validateAllParameters(queryParams)`
Main validation entry point.

**Returns:**
```javascript
// Success
{ valid: true, parsed: { ... } }

// Failure
{ valid: false, error: "...", parameter: "..." }
```

##### `validateRequired(queryParams)`
Checks all required params present.

##### `validatePage(page)`
Positive integer validation.

##### `validateLimit(limit)`
Integer 1-100 validation.

##### `validateSortBy(sortBy)`
Checks against allowed sort fields.

##### `validateSortOrder(sortOrder)`
Must be "asc" or "desc".

##### `validateDate(date)`
Must be "all" or "YYYY-MM-DD".

##### `validateCSVField(fieldName, value, allowedValues)`
CSV/all/clear validation.

**Returns:**
```javascript
{
  valid: true,
  mode: "all" | "clear" | "csv",
  values: ["agentic_ai", "reinforcement_learning"]  // Only for CSV mode
}
```

**Detects:**
- Empty strings
- Mixing "all"/"clear" with values
- Invalid values
- Case mismatches

##### `validateHIndexRange(minValue, maxValue, fieldPrefix)`
H-index range validation.

**Features:**
- Accepts numbers or "inf"
- Validates min ≤ max
- **Rejects both being "inf"**
- Returns parsed `Infinity` for "inf"

**Returns:**
```javascript
{
  valid: true,
  min: 50,           // or Infinity
  max: Infinity
}
```

**Allowed Values Constants:**
```javascript
const ALLOWED_VALUES = {
  sortBy: ['recommendation', 'relevance', 'highest_h_index', 'average_h_index', 'arxiv_id', 'title'],
  sortOrder: ['asc', 'desc'],
  topics: ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'],
  recommendation: ['must_read', 'should_read', 'can_skip', 'can_ignore'],
  impact: ['high', 'moderate', 'low', 'negligible'],
  novelty: ['high', 'moderate', 'low', 'none'],
  relevance: ['highly', 'moderately', 'tangentially', 'not_relevant'],
  scoring: ['completed', 'not_relevant_enough'],
  h_index_status: ['found', 'not_found']
};
```

**Security:**
- All queries use parameterized statements
- No user input interpolated into SQL
- Validation prevents SQL injection
- Type checking prevents type confusion

---

## Key Features Deep Dive

### Infinite Scroll with Position Restoration

**Implementation:** React Query's `useInfiniteQuery` + custom scroll restoration with OverlayScrollbars support.

**How It Works:**

1. **Infinite Query Setup**
   ```tsx
   const {
     data,
     fetchNextPage,
     hasNextPage,
     isFetchingNextPage
   } = useInfiniteQuery({
     queryKey: ['papers', 'list', filters, sortOptions],
     queryFn: ({ pageParam = 1 }) => fetchPapers(filters, sortOptions, pageParam),
     getNextPageParam: (lastPage) =>
       lastPage.pagination.hasNextPage
         ? lastPage.pagination.currentPage + 1
         : undefined,
     staleTime: 1000 * 60 * 60 * 2,
   });
   ```

2. **Load More Button** (instead of scroll detection)
   - User clicks "Load More Papers" button to fetch next page
   - Scroll position is preserved during pagination updates
   - Prevents unintended auto-loading

3. **Position Capture** (before navigation to paper details)
   ```tsx
   // In PaperCard component
   const handleClick = () => {
     let scrollTop = 0;

     if (scrollRef?.current) {
       // Desktop: OverlayScrollbars
       if ('osInstance' in scrollRef.current) {
         const osInstance = scrollRef.current.osInstance();
         if (osInstance) {
           const { viewport } = osInstance.elements();
           scrollTop = viewport.scrollTop;
         }
       }
       // Mobile: Native scroll
       else if ('scrollTop' in scrollRef.current) {
         scrollTop = scrollRef.current.scrollTop;
       }
     }

     const scrollData = {
       path: location.pathname + location.search,
       scrollTop: scrollTop,
       timestamp: Date.now()
     };

     sessionStorage.setItem('explorerScrollPosition', JSON.stringify(scrollData));
   };
   ```

4. **Position Restoration** (on return from paper details)
   ```tsx
   // In ExplorerPage component
   useLayoutEffect(() => {
     const savedScrollData = sessionStorage.getItem('explorerScrollPosition');

     if (savedScrollData && !isLoading && papers.length > 0) {
       const scrollData = JSON.parse(savedScrollData);
       const currentPath = location.pathname + location.search;

       // Validate: path matches, data is recent (within 5 minutes)
       if (scrollData.path === currentPath &&
           Date.now() - scrollData.timestamp < 5 * 60 * 1000 &&
           scrollData.scrollTop > 0) {

         // Retry mechanism for OverlayScrollbars initialization
         const attemptRestore = (attempt = 0) => {
           if (rightScrollRef.current) {
             const osInstance = rightScrollRef.current.osInstance();
             if (osInstance) {
               const { viewport } = osInstance.elements();
               viewport.scrollTop = scrollData.scrollTop;
               sessionStorage.removeItem('explorerScrollPosition');
             } else if (attempt < 10) {
               setTimeout(() => attemptRestore(attempt + 1), 50);
             }
           } else if (mobileScrollRef.current) {
             mobileScrollRef.current.scrollTop = scrollData.scrollTop;
             sessionStorage.removeItem('explorerScrollPosition');
           }
         };

         setTimeout(() => attemptRestore(0), 100);
       }
     }
   }, [isLoading, papers.length, location.pathname, location.search]);
   ```

**Key Technical Details:**

- **Scroll Refs Passed Down**: `ExplorerPage` → `PaperCardList` → `PaperCard`
- **OverlayScrollbars Support**: Handles custom scrollbar viewport on desktop
- **Native Scroll Support**: Handles standard scrollTop on mobile
- **Timing Considerations**:
  - 100ms initial delay for page render
  - Retry mechanism with 50ms intervals for OverlayScrollbars initialization
  - Maximum 10 retry attempts
- **Path Validation**: Only restores if URL exactly matches saved path
- **Expiry**: Scroll data expires after 5 minutes to prevent stale restoration
- **SessionStorage**: Persists across navigation but cleared after restoration

**Benefits:**
- Returns to exact pixel position after viewing paper details
- Works with both desktop (OverlayScrollbars) and mobile (native) scroll
- Handles timing issues with custom scrollbars
- URL-aware (only restores on matching page)
- Time-aware (prevents stale data restoration)
- No visual jump (uses `useLayoutEffect`)

---

### LaTeX Rendering

**Implementation:** KaTeX library with custom parsing.

**Component:** `LaTeXText`

**File:** `frontend/src/components/ui/LaTeXText.tsx`

**Supported Delimiters:**
- Inline: `$...$` or `\(...\)`
- Block: `$$...$$` or `\[...\]`

**Algorithm:**

1. **Parse Text**
   ```tsx
   function parseLatex(text: string) {
     const segments = [];
     let currentIndex = 0;

     // Regex to find LaTeX delimiters
     const latexRegex = /(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^\$]+?\$|\\\([^\)]+?\\\))/g;

     let match;
     while ((match = latexRegex.exec(text)) !== null) {
       // Add text before LaTeX
       if (match.index > currentIndex) {
         segments.push({
           type: 'text',
           content: text.slice(currentIndex, match.index)
         });
       }

       // Add LaTeX segment
       segments.push({
         type: 'latex',
         content: match[0],
         displayMode: match[0].startsWith('$$') || match[0].startsWith('\\[')
       });

       currentIndex = match.index + match[0].length;
     }

     // Add remaining text
     if (currentIndex < text.length) {
       segments.push({
         type: 'text',
         content: text.slice(currentIndex)
       });
     }

     return segments;
   }
   ```

2. **Render Segments**
   ```tsx
   {segments.map((segment, index) => {
     if (segment.type === 'text') {
       return <span key={index}>{segment.content}</span>;
     } else {
       try {
         const html = katex.renderToString(
           cleanLatex(segment.content),
           { displayMode: segment.displayMode }
         );
         return <span key={index} dangerouslySetInnerHTML={{ __html: html }} />;
       } catch (error) {
         // Fallback to raw LaTeX on error
         return <span key={index} className="latex-error">{segment.content}</span>;
       }
     }
   })}
   ```

3. **Error Handling**
   - Graceful degradation to raw LaTeX on parse errors
   - Visual indicator for failed rendering
   - Doesn't break page if LaTeX is invalid

**Example Usage:**
```tsx
<LaTeXText text="The loss function is $\mathcal{L} = \sum_{i=1}^n (y_i - \hat{y}_i)^2$" />

<LaTeXText
  text="$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$"
  displayMode={true}
/>
```

---

### H-Index Range Sliders

**Implementation:** rc-slider library with custom styling.

**Component:** `HIndexRangeSlider`

**Files:**
- `frontend/src/components/ui/HIndexRangeSlider.tsx`
- `frontend/src/components/ui/HIndexRangeSlider.css`

**Features:**

1. **Dual Handles**
   - Min and max handles
   - Independent movement
   - Prevents crossing

2. **Infinity Support**
   - "inf" value for unbounded ranges
   - Special handling in API/validation
   - Visual indicator for infinity

3. **Real-time Display**
   - Shows current min/max values
   - Updates as user drags
   - Formatted display (e.g., "50 - ∞")

4. **Debounced Updates**
   - Prevents excessive API calls
   - 300ms debounce on change
   - Only updates URL after user stops dragging

**Implementation:**

```tsx
const HIndexRangeSlider = ({ label, min, max, currentMin, currentMax, onChange }) => {
  const [localMin, setLocalMin] = useState(currentMin);
  const [localMax, setLocalMax] = useState(currentMax);

  // Debounced onChange
  const debouncedOnChange = useMemo(
    () => debounce((min, max) => onChange(min, max), 300),
    [onChange]
  );

  const handleChange = (values) => {
    const [newMin, newMax] = values;
    setLocalMin(newMin === max ? "inf" : newMin);
    setLocalMax(newMax === max ? "inf" : newMax);
    debouncedOnChange(
      newMin === max ? "inf" : newMin,
      newMax === max ? "inf" : newMax
    );
  };

  return (
    <div className="h-index-slider">
      <label>{label}</label>
      <div className="value-display">
        {formatValue(localMin)} - {formatValue(localMax)}
      </div>
      <Slider
        range
        min={min}
        max={max}
        value={[
          localMin === "inf" ? max : localMin,
          localMax === "inf" ? max : localMax
        ]}
        onChange={handleChange}
        className="custom-slider"
      />
    </div>
  );
};
```

**Custom Styling (HIndexRangeSlider.css):**
```css
.rc-slider-rail {
  background-color: #d4d4d4;
  height: 4px;
}

.rc-slider-track {
  background-color: #525252;
  height: 4px;
}

.rc-slider-handle {
  width: 16px;
  height: 16px;
  border: 2px solid #525252;
  background-color: white;
}

.rc-slider-handle:hover {
  border-color: #262626;
}
```

---

### Advanced Filtering System

**Architecture:** 9 filter types with URL-based state management.

**Filter Types:**

| Filter | Type | Values | Purpose |
|--------|------|--------|---------|
| `scoring` | Checkbox | completed, not_relevant_enough | Filter by scoring status |
| `recommendation` | Checkbox | must_read, should_read, can_skip, can_ignore | Filter by recommendation level |
| `impact` | Checkbox | high, moderate, low, negligible | Filter by impact score |
| `novelty` | Checkbox | high, moderate, low, none | Filter by novelty score |
| `topics` | Checkbox | 5 research topics | Select topics of interest |
| `relevance` | Checkbox | highly, moderately, tangentially, not_relevant | Filter by topic relevance |
| `h_index_status` | Checkbox | found, not_found | Filter by h-index availability |
| `highest_h_index_range` | Range Slider | 0 - 200+ | Filter by highest author h-index |
| `average_h_index_range` | Range Slider | 0 - 100+ | Filter by average author h-index |

**State Flow:**

```
User Interaction
    ↓
Update URL Parameters
    ↓
useSearchParams() detects change
    ↓
Component re-renders with new params
    ↓
useExplorerPapers() hook called with new filters
    ↓
React Query checks cache
    ↓
Cache key = ['papers', 'list', NEW_FILTERS, sort, page]
    ↓
Cache Miss → API Call
    ↓
Server validates all 16 parameters
    ↓
Dynamic SQL query built
    ↓
Database returns filtered papers
    ↓
React Query caches results
    ↓
Component renders filtered papers
```

**Filter Modes:**

1. **"all" Mode**
   - No filtering on this parameter
   - Includes all possible values
   - Default state

2. **"clear" Mode**
   - Excludes all values
   - Returns empty results for this filter
   - Special case: topics="clear" skips relevance filtering entirely

3. **CSV Mode**
   - Comma-separated list of values
   - Only includes papers matching these values
   - Case-sensitive, no spaces

**Special: Topics Filter Behavior**

Unlike other filters, `topics` doesn't filter papers out:

```javascript
// Other filters: Exclude papers not matching
recommendation=must_read  →  Only returns "Must Read" papers

// Topics filter: Controls fields and relevance checking
topics=agentic_ai        →  Returns ALL papers, but:
                             - Only agentic_ai_* fields populated
                             - Relevance filter only checks agentic_ai_relevance

topics=clear             →  Returns ALL papers, and:
                             - All topic fields populated
                             - Relevance filter is SKIPPED
```

**Implementation Example:**

```tsx
// FilterColumn component
const FilterColumn = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read current filters from URL
  const currentTopics = searchParams.get('topics')?.split(',') || [];

  // Update filter
  const handleTopicChange = (topic: string, checked: boolean) => {
    let newTopics;
    if (checked) {
      newTopics = [...currentTopics, topic];
    } else {
      newTopics = currentTopics.filter(t => t !== topic);
    }

    // Update URL
    setSearchParams({
      ...Object.fromEntries(searchParams),
      topics: newTopics.length === 0 ? 'clear' : newTopics.join(',')
    });
  };

  return (
    <div>
      <FilterSection title="Topics">
        <Checkbox
          checked={currentTopics.includes('agentic_ai')}
          onChange={(e) => handleTopicChange('agentic_ai', e.target.checked)}
        >
          Agentic AI
        </Checkbox>
        {/* ... other topics */}
      </FilterSection>
    </div>
  );
};
```

---

### Responsive Design

**Breakpoints:**

| Page | Breakpoint | Purpose |
|------|------------|---------|
| LandingPage | 1050px | Desktop shows two-column layout, mobile shows single column |
| ExplorerPage | 1050px | Desktop shows filter column, mobile shows modals |
| PaperDetails | 1050px | Desktop shows three-column layout, mobile shows single column |

**Consistent Breakpoint:**

All pages use **1050px** as the breakpoint between mobile and desktop layouts. This provides a consistent experience across the application and ensures sufficient space for the filter columns and multi-column layouts on desktop.

**Responsive Patterns:**

1. **Conditional Rendering**
   ```tsx
   // Desktop only
   <div className="hidden md:block">
     <FilterColumn />
   </div>

   // Mobile only
   <div className="md:hidden">
     <MobileFilterButton onClick={() => setShowModal(true)} />
   </div>
   ```

2. **Responsive Styling**
   ```tsx
   className="text-base md:text-2xl"        // Font size
   className="gap-4 md:gap-6"               // Spacing
   className="px-4 md:px-8"                 // Padding
   className="w-full md:w-1/2"              // Width
   className="flex-col md:flex-row"         // Layout direction
   ```

3. **Responsive Layouts**
   ```tsx
   // Mobile: Stack vertically
   // Desktop: Two columns
   <div className="flex flex-col md:flex-row">
     <aside className="md:w-64">Sidebar</aside>
     <main className="flex-1">Content</main>
   </div>
   ```

4. **Custom Breakpoints**
   ```tsx
   // tailwind.config.js
   module.exports = {
     theme: {
       screens: {
         'landingPageDesktop': '1050px',
         'explorerPageDesktop': '1050px',
         'paperDetailsDesktop': '1050px',
       }
     }
   }

   // Usage
   className="hidden paperDetailsDesktop:block"
   ```

**Mobile-First Approach:**

All styles are mobile-first, with desktop styles added via `md:` prefix:

```tsx
// Mobile: Full width, vertical stack, small text
// Desktop: Fixed width, horizontal, large text
<div className="w-full md:w-64 flex flex-col md:flex-row text-sm md:text-base">
```

---

### URL-Driven State

**Philosophy:** All application state lives in the URL.

**Benefits:**

1. **Shareable** - Copy URL to share exact filtered view
2. **Bookmarkable** - Save specific views
3. **Browser Navigation** - Back/forward buttons work perfectly
4. **No Prop Drilling** - Components read directly from URL
5. **Automatic Cache Invalidation** - URL change = cache key change = refetch
6. **Persistence** - Refresh preserves state
7. **Deep Linking** - Direct links to specific views

**Implementation:**

```tsx
// Read from URL
const [searchParams, setSearchParams] = useSearchParams();
const date = searchParams.get('date') || 'all';
const sortBy = searchParams.get('sortBy') || 'recommendation';
const topics = searchParams.get('topics') || 'all';

// Update URL (triggers automatic refetch)
setSearchParams({
  ...Object.fromEntries(searchParams),  // Preserve existing params
  sortBy: 'title',                       // Update specific param
  sortOrder: 'asc'
});
```

**React Query Integration:**

```tsx
const { data } = useExplorerPapers({
  filters: {
    date: searchParams.get('date') || 'all',
    topics: searchParams.get('topics') || 'all',
    // ... other filters from URL
  },
  sortOptions: {
    sortBy: searchParams.get('sortBy') || 'recommendation',
    sortOrder: searchParams.get('sortOrder') || 'desc'
  },
  page: 1,
  limit: 20
});

// Query key includes all params
// ['papers', 'list', {date: 'all', topics: 'agentic_ai'}, {sortBy: 'recommendation'}, 1, 20]

// URL change → Different query key → Automatic refetch!
```

**URL Structure:**

```
/explorer?
  date=2025-03-17
  &sortBy=recommendation
  &sortOrder=desc
  &topics=agentic_ai,reinforcement_learning
  &recommendation=must_read,should_read
  &impact=all
  &novelty=all
  &relevance=highly,moderately
  &scoring=all
  &h_index_status=found
  &highest_h_index_min=50
  &highest_h_index_max=inf
  &average_h_index_min=0
  &average_h_index_max=inf
```

**Helper Functions:**

```tsx
// Get all current params as object
const getAllParams = () => Object.fromEntries(searchParams);

// Update multiple params at once
const updateParams = (updates: Record<string, string>) => {
  setSearchParams({
    ...getAllParams(),
    ...updates
  });
};

// Reset specific param to default
const resetParam = (param: string, defaultValue: string) => {
  setSearchParams({
    ...getAllParams(),
    [param]: defaultValue
  });
};
```

---

## Data Flow

### Landing Page Load

```
1. User visits "/"
     ↓
2. LandingPage component mounts
     ↓
3. usePapersMetadata() hook executes
     ↓
4. React Query checks cache
     ├─ Cache Hit → Return cached data (instant, 0ms)
     └─ Cache Miss → Continue to step 5
     ↓
5. HTTP GET /api/papers/metadata
     ↓
6. Server: papersRouter handles request
     ↓
7. Database.getInstance().getDateMetadata()
     ↓
8. SQL Query:
     SELECT
       DATE(published_date) as date,
       COUNT(*) as total_count,
       SUM(CASE WHEN recommendation_score = 'Must Read' THEN 1 ELSE 0 END) as must_read_count,
       SUM(CASE WHEN recommendation_score = 'Should Read' THEN 1 ELSE 0 END) as should_read_count
     FROM papers
     GROUP BY DATE(published_date)
     ORDER BY date DESC
     ↓
9. Database.getInstance().getAllDatesMetadata()
     ↓
10. SQL Query:
     SELECT
       COUNT(*) as total_count,
       SUM(CASE WHEN recommendation_score = 'Must Read' THEN 1 ELSE 0 END) as must_read_count,
       SUM(CASE WHEN recommendation_score = 'Should Read' THEN 1 ELSE 0 END) as should_read_count
     FROM papers
     ↓
11. Server returns JSON response
     ↓
12. React Query caches response
      - Key: ['papers', 'metadata']
      - TTL: 2 hours
     ↓
13. Component receives data
     ↓
14. DateCardList renders
     ├─ AllTimeCard (aggregated stats)
     └─ DateCard[] (per-date stats)
```

---

### Explorer Page - Filter/Sort Flow

```
1. User clicks sort option "Title (A-Z)"
     ↓
2. SortDropdown updates URL
     setSearchParams({ sortBy: 'title', sortOrder: 'asc' })
     ↓
3. URL changes to /explorer?date=all&sortBy=title&sortOrder=asc&...
     ↓
4. ExplorerPage re-renders (URL changed)
     ↓
5. useExplorerPapers() reads new URL params
     filters = { date: 'all', topics: 'all', ... }
     sortOptions = { sortBy: 'title', sortOrder: 'asc' }
     ↓
6. React Query calculates cache key
     ['papers', 'list', filters, sortOptions, 1, 20]
     ↓
7. React Query checks cache
     ├─ Cache Hit → Return cached data (instant)
     └─ Cache Miss → Continue to step 8
     ↓
8. HTTP GET /api/papers?date=all&sortBy=title&sortOrder=asc&...
     ↓
9. Server: validateAllParameters(queryParams)
     ├─ Invalid → Return 400 error
     └─ Valid → Continue to step 10
     ↓
10. Server: Parse and map filters
      topics: "all" → undefined
      recommendation: "must_read,should_read" → ["Must Read", "Should Read"]
     ↓
11. Database._buildWhereClause(filters)
      Returns: { whereClause: "WHERE ...", params: [...] }
     ↓
12. Database._buildOrderByClause('title', 'asc', undefined)
      Returns: "ORDER BY title ASC"
     ↓
13. Execute parallel queries
      ├─ getPapersWithFilters() → papers array
      └─ getFilteredCount() → total count
     ↓
14. SQL Query:
      SELECT * FROM papers
      WHERE recommendation_score IN (?, ?)
      ORDER BY title ASC
      LIMIT 20 OFFSET 0
     ↓
15. Server: filterTopicFields(papers, topicsMode, topicsValues)
      - Nulls unselected topic fields
     ↓
16. Server returns JSON response with papers + pagination
     ↓
17. React Query caches response
      - Key: ['papers', 'list', NEW_FILTERS, NEW_SORT, 1, 20]
      - TTL: 2 hours
     ↓
18. Component receives data
     ↓
19. PaperCardList renders with sorted papers
```

---

### Paper Details View

```
1. User clicks PaperCard
     ↓
2. Store scroll position
     sessionStorage.setItem('explorerScrollPosition', window.scrollY)
     ↓
3. Navigate to /paper/2509.00640
     ↓
4. PaperDetails component mounts
     ↓
5. Extract id from URL params
     const { id } = useParams();
     ↓
6. usePaperDetails(id) hook executes
     ↓
7. React Query checks cache
     ├─ Cache Hit → Return cached data
     └─ Cache Miss → Continue to step 8
     ↓
8. HTTP GET /api/papers/details/2509.00640
     ↓
9. Server: papersRouter handles request
     ↓
10. Database query:
      SELECT * FROM papers WHERE id = ?
     ↓
11. Parse JSON fields (authors, categories, author_h_indexes)
     ↓
12. Server returns full paper object
     ↓
13. React Query caches response
      - Key: ['paper', '2509.00640']
      - TTL: 2 hours
     ↓
14. Component receives data
     ↓
15. Render sections:
      ├─ PaperDetailsHeader (title, authors, LaTeX)
      ├─ ScoringSection (recommendation, novelty, impact)
      ├─ HIndexSection (highest, average, per-author)
      ├─ SummarySection (AI summary, LaTeX)
      ├─ AbstractSection (full abstract, LaTeX)
      └─ TopicRelevanceSection (5 topics with scores)
     ↓
16. LaTeXText components render math expressions
     ↓
17. User clicks "Back" button
     ↓
18. Navigate to /explorer (previous URL)
     ↓
19. ExplorerPage mounts
     ↓
20. Restore scroll position
      const savedPosition = sessionStorage.getItem('explorerScrollPosition');
      window.scrollTo(0, parseInt(savedPosition));
     ↓
21. User returns to exact position in list
```

---

### Infinite Scroll Flow

```
1. User scrolls down in ExplorerPage
     ↓
2. Scroll event listener detects proximity to bottom
     if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500)
     ↓
3. Check if next page available
     if (hasNextPage && !isFetchingNextPage)
     ↓
4. Call fetchNextPage()
     ↓
5. React Query executes next page query
     ['papers', 'list', filters, sort, PAGE_2, 20]
     ↓
6. HTTP GET /api/papers?...&page=2&limit=20
     ↓
7. Server returns next 20 papers
     ↓
8. React Query merges with existing data
     data.pages = [
       { papers: [...20 papers from page 1...] },
       { papers: [...20 papers from page 2...] }
     ]
     ↓
9. Component re-renders with appended papers
     ↓
10. PaperCardList renders all 40 papers
     ↓
11. User continues scrolling
     ↓
12. Process repeats for page 3, 4, 5...
```

---

## Development Guide

### Adding a New Filter

**Example:** Adding a "Published Year" filter

1. **Update Validation** (`server/validation/papersValidator.js`)
   ```javascript
   const ALLOWED_VALUES = {
     // ... existing
     year: ['2024', '2025']
   };

   function validateAllParameters(queryParams) {
     // Add to required parameters
     const requiredParams = [
       // ... existing
       'year'
     ];

     // Add validation
     const yearValidation = validateCSVField('year', queryParams.year, ALLOWED_VALUES.year);
     if (!yearValidation.valid) {
       return { valid: false, error: yearValidation.error, parameter: 'year' };
     }
   }
   ```

2. **Update Route Handler** (`server/routes/papers.js`)
   ```javascript
   // Parse year filter
   const yearMode = validated.parsed.year.mode;
   const yearValues = validated.parsed.year.values;

   if (yearMode === 'all') {
     filters.year = undefined;
   } else if (yearMode === 'clear') {
     filters.year = ['__IMPOSSIBLE_VALUE__'];
   } else {
     filters.year = yearValues;  // Already in correct format
   }
   ```

3. **Update Database Query** (`server/database/db.js`)
   ```javascript
   _buildWhereClause(filters) {
     const conditions = [];
     const params = [];

     // ... existing filters

     if (filters.year && filters.year.length > 0) {
       const placeholders = filters.year.map(() => '?').join(', ');
       conditions.push(`CAST(strftime('%Y', published_date) AS TEXT) IN (${placeholders})`);
       params.push(...filters.year);
     }

     return { whereClause: conditions.join(' AND '), params };
   }
   ```

4. **Update Frontend Types** (`frontend/src/types/api.ts`)
   ```tsx
   interface ExplorerFilters {
     // ... existing
     year: string;  // "all", "clear", or CSV
   }
   ```

5. **Update Frontend Hook** (`frontend/src/hooks/useExplorerPapers.ts`)
   ```tsx
   const queryParams = new URLSearchParams({
     // ... existing
     year: filters.year
   });
   ```

6. **Add UI Component** (`frontend/src/components/ui/FilterColumn.tsx`)
   ```tsx
   <FilterSection title="Year">
     <Checkbox
       checked={currentYear.includes('2025')}
       onChange={(e) => handleYearChange('2025', e.target.checked)}
     >
       2025
     </Checkbox>
     <Checkbox
       checked={currentYear.includes('2024')}
       onChange={(e) => handleYearChange('2024', e.target.checked)}
     >
       2024
     </Checkbox>
   </FilterSection>
   ```

---

### Adding a New Sort Option

**Example:** Adding "Citation Count" sorting

1. **Update Database** (add `citation_count` column)
   ```sql
   ALTER TABLE papers ADD COLUMN citation_count INTEGER DEFAULT 0;
   ```

2. **Update Validation** (`server/validation/papersValidator.js`)
   ```javascript
   const ALLOWED_VALUES = {
     sortBy: [
       // ... existing
       'citation_count'
     ]
   };
   ```

3. **Update Database Query** (`server/database/db.js`)
   ```javascript
   _buildOrderByClause(sortBy, sortOrder, topics) {
     // ... existing cases

     if (sortBy === 'citation_count') {
       return `ORDER BY citation_count ${sortOrder.toUpperCase()}, arxiv_id DESC`;
     }
   }
   ```

4. **Update Frontend Types** (`frontend/src/types/api.ts`)
   ```tsx
   type SortOption =
     // ... existing
     | 'citation_count-asc'
     | 'citation_count-desc';

   const SORT_OPTIONS = {
     // ... existing
     'citation_count-desc': 'Citation Count (High to Low)',
     'citation_count-asc': 'Citation Count (Low to High)'
   };
   ```

5. **Update Sort UI** (`frontend/src/components/ui/SortDropdown.tsx`)
   ```tsx
   <button onClick={() => handleSort('citation_count', 'desc')}>
     Citation Count (High to Low)
   </button>
   <button onClick={() => handleSort('citation_count', 'asc')}>
     Citation Count (Low to High)
   </button>
   ```

---

### Modifying Cache Duration

**File:** `frontend/src/main.tsx`

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 60 * 2,      // 2 hours (change here)
      cacheTime: 1000 * 60 * 60 * 2.5,    // 2.5 hours (change here)
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    },
  },
});
```

**Rules:**
- `staleTime` ≤ `cacheTime`
- `staleTime` = how long data is considered fresh
- `cacheTime` = how long unused data stays in memory
- For daily updates: 2 hours is optimal
- For real-time data: Reduce to minutes or seconds

---

### Adding a New Component

**Example:** Adding a "FeaturedPapersCarousel"

1. **Create Component File**
   ```tsx
   // frontend/src/components/ui/FeaturedPapersCarousel.tsx
   interface FeaturedPapersCarouselProps {
     papers: Paper[];
   }

   export const FeaturedPapersCarousel: React.FC<FeaturedPapersCarouselProps> = ({ papers }) => {
     return (
       <div className="carousel">
         {papers.map(paper => (
           <PaperCard key={paper.id} paper={paper} />
         ))}
       </div>
     );
   };
   ```

2. **Add to Page**
   ```tsx
   // frontend/src/pages/LandingPage.tsx
   import { FeaturedPapersCarousel } from '../components/ui/FeaturedPapersCarousel';

   <FeaturedPapersCarousel papers={featuredPapers} />
   ```

3. **Add Styling** (Tailwind or CSS module)
   ```tsx
   className="flex overflow-x-auto gap-4 snap-x snap-mandatory"
   ```

---

### Testing the API

**Using curl:**

```bash
# Health check
curl http://localhost:3000/api/health

# Metadata
curl http://localhost:3000/api/papers/metadata

# Paper details
curl http://localhost:3000/api/papers/details/2509.00640

# Filtered papers (all required params)
curl "http://localhost:3000/api/papers?date=all&page=1&limit=20&sortBy=recommendation&sortOrder=desc&topics=all&recommendation=all&impact=all&novelty=all&relevance=all&scoring=all&h_index_status=all&highest_h_index_min=0&highest_h_index_max=inf&average_h_index_min=0&average_h_index_max=inf"

# Filtered papers (specific filters)
curl "http://localhost:3000/api/papers?date=2025-03-17&page=1&limit=20&sortBy=recommendation&sortOrder=desc&topics=agentic_ai,reinforcement_learning&recommendation=must_read,should_read&impact=all&novelty=all&relevance=highly,moderately&scoring=all&h_index_status=found&highest_h_index_min=50&highest_h_index_max=inf&average_h_index_min=0&average_h_index_max=inf"
```

**Using Postman/Insomnia:**

1. Create new GET request
2. URL: `http://localhost:3000/api/papers`
3. Add query parameters (all 16 required)
4. Send request
5. View JSON response

---

### Debugging Tips

**React Query DevTools:**

Add to `frontend/src/main.tsx`:
```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

**Server Logging:**

Add to `server/database/db.js`:
```javascript
_buildWhereClause(filters) {
  // ... build query
  console.log('WHERE:', whereClause);
  console.log('PARAMS:', params);
  return { whereClause, params };
}
```

**Frontend Logging:**

```tsx
useEffect(() => {
  console.log('Current filters:', filters);
  console.log('Current sort:', sortOptions);
}, [filters, sortOptions]);
```

---

## Configuration

### Environment Variables

**Backend** (`server/.env`):

```bash
# Server
PORT=3000

# Database
DATABASE_PATH=./database/researchfeed.db

# CORS
ADDITIONAL_CORS_ORIGINS=http://example.com,https://example.com
```

**Frontend** (`frontend/.env`):

```bash
# API URL
VITE_API_URL=http://localhost:3000/api
```

### Tailwind Configuration

**File:** `frontend/tailwind.config.js`

```javascript
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      screens: {
        'landingPageDesktop': '1050px',
        'explorerPageDesktop': '1050px',
        'paperDetailsDesktop': '1050px',
      },
      colors: {
        neutral: {
          100: '#f5f5f5',
          150: '#ebebeb',
          200: '#e5e5e5',
          300: '#d4d4d4',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        }
      }
    }
  },
  plugins: []
};
```

### React Query Configuration

**File:** `frontend/src/main.tsx`

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 60 * 2,      // 2 hours
      cacheTime: 1000 * 60 * 60 * 2.5,    // 2.5 hours
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});
```

---

## License

MIT License - See LICENSE file for details

---

## Contributors

- Your Name - Initial work

---

## Acknowledgments

- Built with React, TypeScript, and Vite
- UI components styled with TailwindCSS
- LaTeX rendering powered by KaTeX
- Data management with React Query
- SQLite for lightweight database

---

**Last Updated:** October 10, 2025
