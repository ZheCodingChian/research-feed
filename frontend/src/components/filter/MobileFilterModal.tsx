import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFilterReset } from '../../hooks/useFilterReset';
import { FilterSection } from './FilterSection';
import { HIndexRangeSlider } from './HIndexRangeSlider';
import { FilterActionButton } from './FilterActionButton';
import {
  SCORING_OPTIONS,
  RECOMMENDATION_OPTIONS,
  IMPACT_OPTIONS,
  NOVELTY_OPTIONS,
  TOPICS_OPTIONS,
  RELEVANCE_OPTIONS,
  H_INDEX_OPTIONS,
} from '../../constants/filterOptions';

interface MobileFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  filteredCount: number;
  totalCount: number;
  isLoading: boolean;
  maxHighestHIndex: number;
  maxAverageHIndex: number;
}

export function MobileFilterModal({
  isOpen,
  onClose,
  filteredCount,
  totalCount,
  isLoading,
  maxHighestHIndex,
  maxAverageHIndex,
}: MobileFilterModalProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const resetFilters = useFilterReset();
  const [shouldRender, setShouldRender] = useState(false);
  const [isAnimatingIn, setIsAnimatingIn] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setShouldRender(true);
      setTimeout(() => setIsAnimatingIn(true), 10);

      // Prevent scrolling on body (works for most browsers)
      document.body.style.overflow = 'hidden';
      // Prevent scrolling on iOS Safari
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
      document.body.style.top = `-${window.scrollY}px`;
    } else {
      setIsAnimatingIn(false);
      const timer = setTimeout(() => setShouldRender(false), 200);

      // Restore scrolling
      const scrollY = document.body.style.top;
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.body.style.top = '';
      window.scrollTo(0, parseInt(scrollY || '0') * -1);

      return () => clearTimeout(timer);
    }

    return () => {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.body.style.top = '';
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

  const getFilterValues = (key: string, allOptions: string[]): string[] => {
    const param = searchParams.get(key);

    if (!param || param === 'all') {
      return allOptions;
    }

    if (param === 'clear') {
      return [];
    }

    return param.split(',').filter(v => v.length > 0);
  };

  const scoringValues = getFilterValues('scoring', SCORING_OPTIONS.map(o => o.value));
  const recommendationValues = getFilterValues('recommendation', RECOMMENDATION_OPTIONS.map(o => o.value));
  const impactValues = getFilterValues('impact', IMPACT_OPTIONS.map(o => o.value));
  const noveltyValues = getFilterValues('novelty', NOVELTY_OPTIONS.map(o => o.value));
  const topicsValues = getFilterValues('topics', TOPICS_OPTIONS.map(o => o.value));
  const relevanceValues = getFilterValues('relevance', RELEVANCE_OPTIONS.map(o => o.value));
  const hIndexValues = getFilterValues('h_index_status', H_INDEX_OPTIONS.map(o => o.value));

  const handleFilterChange = (filterKey: string, values: string[], allOptions: string[]) => {
    const newParams = new URLSearchParams(searchParams);

    if (values.length === 0) {
      newParams.set(filterKey, 'clear');
    } else if (values.length === allOptions.length) {
      newParams.set(filterKey, 'all');
    } else {
      newParams.set(filterKey, values.join(','));
    }

    setSearchParams(newParams);
  };

  if (!shouldRender) return null;

  return (
    <div className="fixed inset-0 z-50 explorerPageDesktop:hidden">
      <div
        className={`absolute inset-0 bg-black/40 transition-opacity duration-200 ${
          isAnimatingIn ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
        aria-hidden="true"
      />

      <div
        className={`absolute inset-0 bg-neutral-100 flex flex-col transition-transform duration-200 ease-out ${
          isAnimatingIn ? 'translate-y-0' : 'translate-y-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="filter-modal-title"
      >
        <div className="sticky top-0 z-10 bg-neutral-150 px-4 py-3 flex items-center justify-between">
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center"
            aria-label="Close filter modal"
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

          <h2
            id="filter-modal-title"
            className="absolute left-1/2 -translate-x-1/2 text-neutral-800 font-header font-bold text-[1.25rem]"
          >
            Filters
          </h2>

          <button
            onClick={resetFilters}
            className="py-1 px-2 text-neutral-700 hover:text-neutral-800 font-header text-[1rem] transition-colors"
          >
            Clear
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 flex flex-col gap-4 py-4">
          <FilterSection
            title="Scoring:"
            options={SCORING_OPTIONS}
            selectedValues={scoringValues}
            onSelectionChange={(values) => handleFilterChange('scoring', values, SCORING_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="Recommendation:"
            options={RECOMMENDATION_OPTIONS}
            selectedValues={recommendationValues}
            onSelectionChange={(values) => handleFilterChange('recommendation', values, RECOMMENDATION_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="Potential Impact:"
            options={IMPACT_OPTIONS}
            selectedValues={impactValues}
            onSelectionChange={(values) => handleFilterChange('impact', values, IMPACT_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="Novelty:"
            options={NOVELTY_OPTIONS}
            selectedValues={noveltyValues}
            onSelectionChange={(values) => handleFilterChange('novelty', values, NOVELTY_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="Topics:"
            options={TOPICS_OPTIONS}
            selectedValues={topicsValues}
            onSelectionChange={(values) => handleFilterChange('topics', values, TOPICS_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="Relevance:"
            options={RELEVANCE_OPTIONS}
            selectedValues={relevanceValues}
            onSelectionChange={(values) => handleFilterChange('relevance', values, RELEVANCE_OPTIONS.map(o => o.value))}
          />

          <FilterSection
            title="H-Index:"
            options={H_INDEX_OPTIONS}
            selectedValues={hIndexValues}
            onSelectionChange={(values) => handleFilterChange('h_index_status', values, H_INDEX_OPTIONS.map(o => o.value))}
          />

          <HIndexRangeSlider
            title="Highest H-Index Range:"
            absoluteMax={maxHighestHIndex}
            urlParamKey="highest_h_index_range"
          />

          <HIndexRangeSlider
            title="Average H-Index Range:"
            absoluteMax={maxAverageHIndex}
            urlParamKey="average_h_index_range"
          />
        </div>

        <div className="sticky bottom-0 z-10 bg-neutral-150 px-8 py-4">
          <FilterActionButton
            filteredCount={filteredCount}
            totalCount={totalCount}
            isLoading={isLoading}
            onClick={onClose}
          />
        </div>
      </div>
    </div>
  );
}
