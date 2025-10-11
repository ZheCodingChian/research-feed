import { RefObject } from 'react';
import { OverlayScrollbarsComponentRef } from 'overlayscrollbars-react';
import { Paper } from '../../types/api';
import { PaperCard } from './PaperCard';
import { SkeletonPaperCard } from './SkeletonPaperCard';

interface PaperCardListProps {
  papers: Paper[];
  isLoading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoadingMore?: boolean;
  scrollRef?: RefObject<OverlayScrollbarsComponentRef> | RefObject<HTMLDivElement>;
  onBeforeLoadMore?: (scrollTop: number) => void;
}

export function PaperCardList({
  papers,
  isLoading = false,
  onLoadMore,
  hasMore = false,
  isLoadingMore = false,
  scrollRef,
  onBeforeLoadMore,
}: PaperCardListProps) {
  const handleLoadMoreClick = () => {
    // Capture scroll position BEFORE any state changes
    let scrollPosition = 0;

    if (scrollRef?.current) {
      // Check if it's an OverlayScrollbarsComponentRef
      const current = scrollRef.current as any;

      if ('osInstance' in current && typeof current.osInstance === 'function') {
        // Desktop: OverlayScrollbars
        const osInstance = current.osInstance();
        if (osInstance) {
          const { viewport } = osInstance.elements();
          scrollPosition = viewport.scrollTop;
          console.log('[PaperCardList] Captured desktop scroll:', scrollPosition);
        }
      } else if ('scrollTop' in current) {
        // Mobile: Native div
        scrollPosition = current.scrollTop;
        console.log('[PaperCardList] Captured mobile scroll:', scrollPosition);
      }
    }

    // Notify parent to save position
    onBeforeLoadMore?.(scrollPosition);

    // Then trigger fetch (this will cause re-render)
    onLoadMore?.();
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4">
        {Array.from({ length: 10 }, (_, i) => (
          <SkeletonPaperCard key={`skeleton-${i}`} />
        ))}
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <p className="font-header font-bold text-neutral-600 text-[2rem]">
          No Papers Found
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {papers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} scrollRef={scrollRef} />
      ))}

      {/* Load More Button */}
      {hasMore && onLoadMore && (
        <button
          onClick={handleLoadMoreClick}
          disabled={isLoadingMore}
          className="font-header text-[1rem] text-neutral-100 py-1 px-4 mx-auto
                     bg-neutral-600
                     hover:bg-neutral-500 disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors"
        >
          {isLoadingMore ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin w-[1rem] h-[1rem] text-neutral-700"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Loading...
            </span>
          ) : (
            'Load More Papers'
          )}
        </button>
      )}
    </div>
  );
}
