import { useEffect, useState } from 'react';
import { SortOption, SORT_OPTIONS } from '../../constants/sortOptions';
import { useSortSelection } from '../../hooks/useSortSelection';

interface MobileSortModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSortModal({ isOpen, onClose }: MobileSortModalProps) {
  const { currentSort, handleSortChange } = useSortSelection();
  const [shouldRender, setShouldRender] = useState(false);
  const [isAnimatingIn, setIsAnimatingIn] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
      setTimeout(() => setIsAnimatingIn(true), 10);
      document.body.style.overflow = 'hidden';
    } else {
      setIsAnimatingIn(false);
      const timer = setTimeout(() => setShouldRender(false), 300);
      document.body.style.overflow = '';
      return () => clearTimeout(timer);
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  const handleOptionSelect = (sortOption: SortOption) => {
    handleSortChange(sortOption);
    onClose();
  };

  if (!shouldRender) return null;

  return (
    <div className="fixed inset-0 z-50 explorerPageDesktop:hidden">
      <div
        className={`absolute inset-0 bg-black/40 transition-opacity duration-300 ${
          isAnimatingIn ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      <div
        className={`absolute bottom-0 left-0 right-0 bg-neutral-100 max-h-[75vh] flex flex-col transition-transform duration-300 ease-out ${
          isAnimatingIn ? 'translate-y-0' : 'translate-y-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="sort-modal-title"
      >
        <div className="bg-neutral-150 px-4 py-3 flex items-center justify-between">
          <h2
            id="sort-modal-title"
            className="text-neutral-800 font-header font-bold text-[1.25rem]"
          >
            Sort By:
          </h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center"
            aria-label="Close sort modal"
          >
            <svg
              width="1rem"
              height="1rem"
              viewBox="0 0 12 12"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M0.577804 0.590216C0.15473 1.01329 0.15473 1.69921 0.577804 2.12229L4.4617 6.00617L0.577804 9.89014C0.15473 10.3132 0.15473 10.9991 0.577804 11.4222C1.00087 11.8452 1.6868 11.8452 2.10986 11.4222L5.99375 7.53822L9.87772 11.4222C10.3008 11.8452 10.9867 11.8452 11.4098 11.4222C11.8328 10.9991 11.8328 10.3132 11.4098 9.89014L7.5258 6.00617L11.4098 2.1223C11.8328 1.69924 11.8328 1.0133 11.4098 0.590238C10.9866 0.167164 10.3008 0.167164 9.87772 0.590238L5.99375 4.47412L2.10986 0.590216C1.6868 0.167153 1.00087 0.167153 0.577804 0.590216Z"
                fill="#171717"
              />
            </svg>
          </button>
        </div>

        <div className="bg-neutral-100 overflow-y-auto flex-1 pt-1 pb-6">
          {(Object.keys(SORT_OPTIONS) as SortOption[]).map((sortOption) => {
            const isActive = sortOption === currentSort;

            return (
              <button
                key={sortOption}
                onClick={() => handleOptionSelect(sortOption)}
                className="w-full px-4 py-3 flex items-center gap-3 hover:bg-neutral-150 transition-colors"
              >
                <div
                  className={`w-[1rem] h-[1rem] rounded-[0.2rem] flex items-center justify-center transition-colors ${
                    isActive ? 'bg-neutral-700' : 'bg-neutral-300'
                  }`}
                >
                  {isActive && (
                    <svg
                      width="0.625rem"
                      height="0.625rem"
                      viewBox="0 0 10 10"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <rect width="10" height="10" rx="5" fill="#DAD7CD"/>
                    </svg>
                  )}
                </div>
                <span className="text-neutral-800 font-header text-[1rem]">
                  {SORT_OPTIONS[sortOption]}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}