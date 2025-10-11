import { PaperCountDisplay } from './PaperCountDisplay';

interface FilterHeaderProps {
  filteredCount: number;
  totalCount: number;
  onReset: () => void;
  isLoading?: boolean;
}

export function FilterHeader({ filteredCount, totalCount, onReset, isLoading = false }: FilterHeaderProps) {
  return (
    <div className="flex flex-col gap-2">
      {/* Showing Papers Count */}
      <PaperCountDisplay
        filteredCount={filteredCount}
        totalCount={totalCount}
        isLoading={isLoading}
      />

      {/* Reset Button */}
      <button
        onClick={onReset}
        className="w-full px-3 py-1 bg-neutral-600 hover:bg-neutral-500 transition-colors text-neutral-100 font-header text-[1rem]"
      >
        Reset To Default
      </button>
    </div>
  );
}
