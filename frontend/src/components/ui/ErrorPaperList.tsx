import { useFilterReset } from '../../hooks/useFilterReset';

interface ErrorPaperListProps {
  error: string;
}

export function ErrorPaperList({ error }: ErrorPaperListProps) {
  const resetFilters = useFilterReset();

  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="text-center max-w-md mx-auto">
        <h2 className="font-header font-bold text-neutral-800 text-[1.5rem] mb-4">
          Error: Could not fetch papers
        </h2>
        <p className="font-body text-neutral-600 text-[0.875rem] explorerPageDesktop:text-[1rem] leading-relaxed mb-6">
          {error}
        </p>
        <button
          onClick={resetFilters}
          className="px-6 py-2 bg-neutral-600 hover:bg-neutral-500 transition-colors text-neutral-100 font-header text-[1rem]"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
}
