import { useSearchParams } from 'react-router-dom';

export function useFilterReset() {
  const [searchParams, setSearchParams] = useSearchParams();

  const resetFilters = () => {
    const newParams = new URLSearchParams();
    newParams.set('date', searchParams.get('date') || 'all');
    newParams.set('sortBy', 'recommendation');
    newParams.set('sortOrder', 'desc');
    setSearchParams(newParams);
  };

  return resetFilters;
}
