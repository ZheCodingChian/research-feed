import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { useSearchParams, useLocation } from 'react-router-dom';
import { OverlayScrollbarsComponent, OverlayScrollbarsComponentRef } from 'overlayscrollbars-react';
import { useExplorerPapers } from '../hooks/useExplorerPapers';
import { ExplorerHeader } from '../components/layout/ExplorerHeader';
import { ExplorerPageError } from '../components/error/ExplorerPageError';
import { ErrorPaperList } from '../components/paperCard/ErrorPaperList';
import { PaperCardList } from '../components/paperCard/PaperCardList';
import { SortDropdown } from '../components/sort/SortDropdown';
import { FilterColumn } from '../components/filter/FilterColumn';
import { MobileFilterSortButtons } from '../components/filter/MobileFilterSortButtons';
import { MobileSortModal } from '../components/sort/MobileSortModal';
import { MobileFilterModal } from '../components/filter/MobileFilterModal';
import { PaperCountDisplay } from '../components/filter/PaperCountDisplay';
import { LeftArrow } from '../components/common/LeftArrow';

function isCriticalError(error: Error | null): boolean {
  if (!error) return false;
  const message = error.message.toLowerCase();

  // Critical = server issues or network failures (full page error)
  // Non-critical = client validation errors (inline error, user can fix)
  return (
    message.includes('network error') ||
    message.includes('failed to fetch') ||
    message.includes('status: 401') ||  // Unauthorized
    message.includes('status: 403') ||  // Forbidden
    message.includes('status: 404') ||  // Not Found
    message.includes('status: 429') ||  // Too Many Requests
    message.includes('status: 500') ||  // Internal Server Error
    message.includes('status: 502') ||  // Bad Gateway
    message.includes('status: 503') ||  // Service Unavailable
    message.includes('status: 504')     // Gateway Timeout
  );
  // 400 Bad Request is intentionally excluded - it's a validation error users can fix
}

export function ExplorerPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const [isSortModalOpen, setIsSortModalOpen] = useState(false);
  const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
  const [savedScrollTop, setSavedScrollTop] = useState(0);

  // Refs for scroll containers
  const rightScrollRef = useRef<OverlayScrollbarsComponentRef>(null);
  const mobileScrollRef = useRef<HTMLDivElement>(null);

  // Initialize missing URL params with defaults on mount
  useEffect(() => {
    const params = new URLSearchParams(searchParams);
    let changed = false;

    // Required params with defaults
    const defaults = {
      limit: '30',
      sortBy: 'recommendation',
      sortOrder: 'desc',
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
    };

    // Set missing params
    for (const [key, value] of Object.entries(defaults)) {
      if (!params.has(key)) {
        params.set(key, value);
        changed = true;
      }
    }

    if (changed) {
      setSearchParams(params, { replace: true }); // Replace to avoid history pollution
    }
  }, []); // Only run on mount

  // Read params (guaranteed to exist after initialization)
  const limit = parseInt(searchParams.get('limit') || '30');
  const sortBy = searchParams.get('sortBy') || 'recommendation';
  const sortOrder = searchParams.get('sortOrder') || 'desc';
  const date = searchParams.get('date') || 'all';

  // Parse filter params - return exact URL value
  const parseFilterParam = (key: string, defaultValue: string = 'all'): string => {
    return searchParams.get(key) || defaultValue;
  };

  const filters = {
    date,
    topics: parseFilterParam('topics'),
    recommendation: parseFilterParam('recommendation'),
    impact: parseFilterParam('impact'),
    novelty: parseFilterParam('novelty'),
    relevance: parseFilterParam('relevance'),
    scoring: parseFilterParam('scoring'),
    h_index_status: parseFilterParam('h_index_status'),
    highest_h_index_range: parseFilterParam('highest_h_index_range'),
    average_h_index_range: parseFilterParam('average_h_index_range'),
  };

  // Fetch papers with all filters and sort options
  const {
    data: papersData,
    isLoading,
    isFetching,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    error: papersError,
    refetch
  } = useExplorerPapers(
    filters,
    { sortBy, sortOrder },
    limit
  );

  // Flatten pages into single array
  const papers = papersData?.pages.flatMap(page => page.papers) ?? [];

  // Use first page's metadata (same across all pages)
  const pagination = papersData?.pages[0]?.pagination;
  const metadata = papersData?.pages[0]?.metadata;

  // Combine loading states - show shimmer during initial load or refetch
  const isLoadingData = isLoading || isFetching;

  // Restore scroll position after content update (for "Load More")
  useLayoutEffect(() => {
    if (!isFetchingNextPage && savedScrollTop > 0) {
      if (rightScrollRef.current) {
        const osInstance = rightScrollRef.current.osInstance();
        if (osInstance) {
          const { viewport } = osInstance.elements();
          viewport.scrollTop = savedScrollTop;
          setSavedScrollTop(0);
        }
      } else if (mobileScrollRef.current) {
        mobileScrollRef.current.scrollTop = savedScrollTop;
        setSavedScrollTop(0);
      }
    }
  }, [isFetchingNextPage, savedScrollTop, papersData?.pages.length]);

  // Restore scroll position from sessionStorage (when navigating back from paper details)
  useLayoutEffect(() => {
    const savedScrollData = sessionStorage.getItem('explorerScrollPosition');

    if (savedScrollData && !isLoading && papers.length > 0) {
      try {
        const scrollData = JSON.parse(savedScrollData);
        const currentPath = location.pathname + location.search;

        if (scrollData.path === currentPath && Date.now() - scrollData.timestamp < 5 * 60 * 1000 && scrollData.scrollTop > 0) {
          const attemptRestore = (attempt = 0) => {
            if (rightScrollRef.current) {
              const osInstance = rightScrollRef.current.osInstance();
              if (osInstance) {
                const { viewport } = osInstance.elements();
                viewport.scrollTop = scrollData.scrollTop;

                setTimeout(() => {
                  if (viewport.scrollTop < scrollData.scrollTop - 50 && attempt < 5) {
                    setTimeout(() => attemptRestore(attempt + 1), 50);
                  } else {
                    sessionStorage.removeItem('explorerScrollPosition');
                  }
                }, 0);
                return;
              } else if (attempt < 10) {
                setTimeout(() => attemptRestore(attempt + 1), 50);
                return;
              }
            } else if (mobileScrollRef.current) {
              mobileScrollRef.current.scrollTop = scrollData.scrollTop;
              sessionStorage.removeItem('explorerScrollPosition');
              return;
            }

            sessionStorage.removeItem('explorerScrollPosition');
          };

          setTimeout(() => attemptRestore(0), 100);
        }
      } catch (error) {
        sessionStorage.removeItem('explorerScrollPosition');
      }
    }
  }, [isLoading, papers.length, location.pathname, location.search]);

  // Check for critical errors
  if (isCriticalError(papersError)) {
    return <ExplorerPageError error={papersError?.message || 'An unknown error occurred'} onRetry={refetch} />;
  }

  return (
    <div className="h-screen bg-neutral-100 flex flex-col">
      <div className="max-w-[1440px] mx-auto w-full h-full flex flex-col">
        {/* Mobile: Single column layout */}
        <div className="flex flex-col explorerPageDesktop:hidden h-screen overflow-hidden">
        <div className="flex flex-row items-center gap-1">
          <LeftArrow />
          <ExplorerHeader />
        </div>

        {/* Fixed: Paper Count Display + Filter/Sort Buttons - Single Row */}
        {!isCriticalError(papersError) && (
          <div className="px-5 pb-2 flex items-center gap-3 justify-left">
            <MobileFilterSortButtons
              onFilterClick={() => setIsFilterModalOpen(true)}
              onSortClick={() => setIsSortModalOpen(true)}
            />

            <PaperCountDisplay
              filteredCount={pagination?.totalCount || 0}
              totalCount={metadata?.totalPapers || 0}
              isLoading={isLoadingData}
            />
            </div>
        )}

        {/* Scrollable: Paper List or Error */}
        <div ref={mobileScrollRef} className="flex-1 overflow-y-auto px-5 pb-8 flex flex-col gap-4">
          {papersError ? (
            <ErrorPaperList error={papersError.message} />
          ) : (
            <PaperCardList
              papers={papers}
              isLoading={isLoadingData}
              onLoadMore={fetchNextPage}
              hasMore={hasNextPage}
              isLoadingMore={isFetchingNextPage}
              scrollRef={mobileScrollRef}
              onBeforeLoadMore={setSavedScrollTop}
            />
          )}
        </div>
      </div>

      {/* Desktop: Three-column layout */}
      <div className="hidden explorerPageDesktop:flex flex-1 overflow-hidden">
        {/* Arrow Column: Fixed, no scroll */}
        <div className="w-16 pt-8">
          <LeftArrow />
        </div>

        {/* Filter Column: Header + Filters - Scrollable */}
        <OverlayScrollbarsComponent
          options={{
            scrollbars: {
              autoHide: 'leave',
              autoHideDelay: 1300,
              theme: 'os-theme-dark',
            },
          }}
          className="w-[400px] pt-10 pb-16 px-8"
        >
          <div className="flex flex-col gap-8">
            <ExplorerHeader />
            <FilterColumn
              filteredCount={pagination?.totalCount || 0}
              totalCount={metadata?.totalPapers || 0}
              isLoading={isLoadingData}
              maxHighestHIndex={metadata?.maxHighestHIndex || 100}
              maxAverageHIndex={metadata?.maxAverageHIndex || 100}
            />
          </div>
        </OverlayScrollbarsComponent>

        {/* Papers Column: Sort + Papers - Scrollable */}
        <OverlayScrollbarsComponent
          ref={rightScrollRef}
          options={{
            scrollbars: {
              autoHide: 'leave',
              autoHideDelay: 1300,
              theme: 'os-theme-dark',
            },
          }}
          className="flex-1 pl-8 pr-16 pb-16 pt-8"
        >
          <div className="h-[3rem]" />
          <div className="flex flex-col gap-4">
            {!papersError && (isLoadingData || (papers && papers.length > 0)) && (
              <SortDropdown />
            )}
            {papersError ? (
              <ErrorPaperList error={papersError.message} />
            ) : (
              <PaperCardList
                papers={papers}
                isLoading={isLoadingData}
                onLoadMore={fetchNextPage}
                hasMore={hasNextPage}
                isLoadingMore={isFetchingNextPage}
                scrollRef={rightScrollRef}
                onBeforeLoadMore={setSavedScrollTop}
              />
            )}
          </div>
        </OverlayScrollbarsComponent>
      </div>

        <MobileSortModal isOpen={isSortModalOpen} onClose={() => setIsSortModalOpen(false)} />
        <MobileFilterModal
          isOpen={isFilterModalOpen}
          onClose={() => setIsFilterModalOpen(false)}
          filteredCount={pagination?.totalCount || 0}
          totalCount={metadata?.totalPapers || 0}
          isLoading={isLoadingData}
          maxHighestHIndex={metadata?.maxHighestHIndex || 100}
          maxAverageHIndex={metadata?.maxAverageHIndex || 100}
        />
      </div>
    </div>
  );
}
