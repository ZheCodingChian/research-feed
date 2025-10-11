import { useState, useRef, useEffect } from 'react';
import { SortOption, SORT_OPTIONS } from '../../constants/sortOptions';
import { useSortSelection } from '../../hooks/useSortSelection';

export function SortDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { currentSort, handleSortChange } = useSortSelection();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setIsOpen(!isOpen);
    }
  };

  const handleOptionSelect = (sortOption: SortOption) => {
    handleSortChange(sortOption);
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className="relative w-fit">
      {/* Dropdown Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className="bg-neutral-200 hover:bg-neutral-300 transition-colors px-3 py-1 flex flex-row items-center gap-2 w-full"
        role="button"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        aria-label="Sort options"
      >
        {/* Label Section */}
        <span className="text-neutral-800 font-header font-bold text-[1.125rem] whitespace-nowrap">
          Sort By:
        </span>

        {/* Current Option Section */}
        <span className="text-neutral-700 font-header font-bold text-[1.125rem] whitespace-nowrap">
          {SORT_OPTIONS[currentSort]}
        </span>

        {/* Arrow Icon Section */}
        <svg
          width="1.125rem"
          height="1.125rem"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          className={`transition-transform duration-300 ${isOpen ? 'rotate-180' : 'rotate-0'}`}
          fill="#4f4e4b"
        >
          <path d="M21,21H3L12,3Z" transform="rotate(180 12 12)" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className="absolute top-full left-0 mt-1 bg-neutral-600 shadow-lg z-50 min-w-full w-fit"
          role="menu"
        >
          {(Object.keys(SORT_OPTIONS) as SortOption[]).map((sortOption) => (
            <button
              key={sortOption}
              onClick={() => handleOptionSelect(sortOption)}
              className="w-full text-left px-4 py-3 text-neutral-100 font-header text-[1rem] hover:bg-neutral-700 transition-colors whitespace-nowrap"
              role="menuitem"
            >
              {SORT_OPTIONS[sortOption]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
