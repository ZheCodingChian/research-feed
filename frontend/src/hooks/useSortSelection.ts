import { useSearchParams } from 'react-router-dom';
import { SortOption, createSortOption } from '../constants/sortOptions';

export function useSortSelection() {
  const [searchParams, setSearchParams] = useSearchParams();

  const sortBy = searchParams.get('sortBy') || 'recommendation';
  const sortOrder = searchParams.get('sortOrder') || 'desc';
  const currentSort = createSortOption(sortBy, sortOrder);

  const handleSortChange = (sortOption: SortOption) => {
    const [newSortBy, newSortOrder] = sortOption.split('-');
    const newParams = new URLSearchParams(searchParams);
    newParams.set('sortBy', newSortBy);
    newParams.set('sortOrder', newSortOrder);
    setSearchParams(newParams);
  };

  return { currentSort, handleSortChange };
}