import { useSearchParams } from 'react-router-dom';
import { useFilterReset } from '../../hooks/useFilterReset';
import { FilterHeader } from './FilterHeader';
import { FilterSection } from './FilterSection';
import { HIndexRangeSlider } from './HIndexRangeSlider';
import {
  SCORING_OPTIONS,
  RECOMMENDATION_OPTIONS,
  IMPACT_OPTIONS,
  NOVELTY_OPTIONS,
  TOPICS_OPTIONS,
  RELEVANCE_OPTIONS,
  H_INDEX_OPTIONS,
} from '../../constants/filterOptions';

interface FilterColumnProps {
  filteredCount: number;
  totalCount: number;
  isLoading?: boolean;
  maxHighestHIndex?: number;
  maxAverageHIndex?: number;
}

export function FilterColumn({
  filteredCount,
  totalCount,
  isLoading = false,
  maxHighestHIndex = 100,
  maxAverageHIndex = 100,
}: FilterColumnProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const resetFilters = useFilterReset();

  // Parse current filter values from URL
  const getFilterValues = (key: string, allOptions: string[]): string[] => {
    const param = searchParams.get(key);

    // "all" or missing = all options selected
    if (!param || param === 'all') {
      return allOptions;
    }

    // "clear" = none selected
    if (param === 'clear') {
      return [];
    }

    // CSV format - split and filter
    return param.split(',').filter(v => v.length > 0);
  };

  const scoringValues = getFilterValues('scoring', SCORING_OPTIONS.map(o => o.value));
  const recommendationValues = getFilterValues('recommendation', RECOMMENDATION_OPTIONS.map(o => o.value));
  const impactValues = getFilterValues('impact', IMPACT_OPTIONS.map(o => o.value));
  const noveltyValues = getFilterValues('novelty', NOVELTY_OPTIONS.map(o => o.value));
  const topicsValues = getFilterValues('topics', TOPICS_OPTIONS.map(o => o.value));
  const relevanceValues = getFilterValues('relevance', RELEVANCE_OPTIONS.map(o => o.value));
  const hIndexValues = getFilterValues('h_index_status', H_INDEX_OPTIONS.map(o => o.value));

  // Handle filter changes - ALWAYS set param (required by backend)
  const handleFilterChange = (filterKey: string, values: string[], allOptions: string[]) => {
    const newParams = new URLSearchParams(searchParams);

    if (values.length === 0) {
      // No options selected = "clear"
      newParams.set(filterKey, 'clear');
    } else if (values.length === allOptions.length) {
      // All options selected = "all"
      newParams.set(filterKey, 'all');
    } else {
      // Some options selected = CSV
      newParams.set(filterKey, values.join(','));
    }

    setSearchParams(newParams);
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Header with total and reset */}
      <FilterHeader filteredCount={filteredCount} totalCount={totalCount} onReset={resetFilters} isLoading={isLoading} />

      {/* Scoring Section */}
      <FilterSection
        title="Scoring:"
        options={SCORING_OPTIONS}
        selectedValues={scoringValues}
        onSelectionChange={(values) => handleFilterChange('scoring', values, SCORING_OPTIONS.map(o => o.value))}
      />

      {/* Recommendation Section */}
      <FilterSection
        title="Recommendation:"
        options={RECOMMENDATION_OPTIONS}
        selectedValues={recommendationValues}
        onSelectionChange={(values) => handleFilterChange('recommendation', values, RECOMMENDATION_OPTIONS.map(o => o.value))}
      />

      {/* Potential Impact Section */}
      <FilterSection
        title="Potential Impact:"
        options={IMPACT_OPTIONS}
        selectedValues={impactValues}
        onSelectionChange={(values) => handleFilterChange('impact', values, IMPACT_OPTIONS.map(o => o.value))}
      />

      {/* Novelty Section */}
      <FilterSection
        title="Novelty:"
        options={NOVELTY_OPTIONS}
        selectedValues={noveltyValues}
        onSelectionChange={(values) => handleFilterChange('novelty', values, NOVELTY_OPTIONS.map(o => o.value))}
      />

      {/* Topics Section */}
      <FilterSection
        title="Topics:"
        options={TOPICS_OPTIONS}
        selectedValues={topicsValues}
        onSelectionChange={(values) => handleFilterChange('topics', values, TOPICS_OPTIONS.map(o => o.value))}
      />

      {/* Relevance Section */}
      <FilterSection
        title="Relevance:"
        options={RELEVANCE_OPTIONS}
        selectedValues={relevanceValues}
        onSelectionChange={(values) => handleFilterChange('relevance', values, RELEVANCE_OPTIONS.map(o => o.value))}
      />

      {/* H-Index Section */}
      <FilterSection
        title="H-Index:"
        options={H_INDEX_OPTIONS}
        selectedValues={hIndexValues}
        onSelectionChange={(values) => handleFilterChange('h_index_status', values, H_INDEX_OPTIONS.map(o => o.value))}
      />

      {/* Highest H-Index Range Slider */}
      <HIndexRangeSlider
        title="Highest H-Index Range:"
        absoluteMax={maxHighestHIndex}
        urlParamKey="highest_h_index_range"
      />

      {/* Average H-Index Range Slider */}
      <HIndexRangeSlider
        title="Average H-Index Range:"
        absoluteMax={maxAverageHIndex}
        urlParamKey="average_h_index_range"
      />
    </div>
  );
}
