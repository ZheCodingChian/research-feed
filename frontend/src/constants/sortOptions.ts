export type SortOption =
  | 'recommendation-desc'
  | 'recommendation-asc'
  | 'relevance-desc'
  | 'relevance-asc'
  | 'highest_h_index-desc'
  | 'highest_h_index-asc'
  | 'average_h_index-desc'
  | 'average_h_index-asc'
  | 'arxiv_id-desc'
  | 'arxiv_id-asc'
  | 'title-asc'
  | 'title-desc';

export const SORT_OPTIONS: Record<SortOption, string> = {
  'recommendation-desc': 'Recommendation (Best First)',
  'recommendation-asc': 'Recommendation (Worst First)',
  'relevance-desc': 'Relevance (Highest to Lowest)',
  'relevance-asc': 'Relevance (Lowest to Highest)',
  'highest_h_index-desc': 'Highest H-Index (Descending)',
  'highest_h_index-asc': 'Highest H-Index (Ascending)',
  'average_h_index-desc': 'Average H-Index (Descending)',
  'average_h_index-asc': 'Average H-Index (Ascending)',
  'arxiv_id-desc': 'arXiv ID (Descending)',
  'arxiv_id-asc': 'arXiv ID (Ascending)',
  'title-asc': 'Title (A-Z)',
  'title-desc': 'Title (Z-A)',
};

export function parseSortOption(sortOption: SortOption): { sortBy: string; sortOrder: string } {
  const [sortBy, sortOrder] = sortOption.split('-');
  return { sortBy, sortOrder };
}

export function createSortOption(sortBy: string, sortOrder: string): SortOption {
  return `${sortBy}-${sortOrder}` as SortOption;
}
