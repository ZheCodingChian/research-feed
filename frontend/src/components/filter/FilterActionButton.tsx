interface FilterActionButtonProps {
  filteredCount: number;
  totalCount: number;
  isLoading: boolean;
  onClick: () => void;
}

export function FilterActionButton({
  filteredCount,
  totalCount,
  isLoading,
  onClick,
}: FilterActionButtonProps) {
  const showError = !isLoading && filteredCount === 0 && totalCount === 0;

  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="w-full py-2 bg-neutral-600 hover:bg-neutral-700 transition-colors disabled:opacity-75 flex items-center justify-center"
    >
      {isLoading ? (
        <svg
          className="animate-spin w-[1.25rem] h-[1.25rem] text-neutral-100"
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
      ) : (
        <span className="text-neutral-100 font-header font-bold text-[1rem]">
          {showError
            ? 'Show -- / -- Papers'
            : `Show ${filteredCount} / ${totalCount} Papers`}
        </span>
      )}
    </button>
  );
}
