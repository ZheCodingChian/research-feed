import { useInfiniteQuery } from '@tanstack/react-query';
import { apiCall, API_ENDPOINTS } from '../config/api';
import { ExplorerMetadata, Paper } from '../types/api';

export interface ExplorerPapersResponse {
  papers: Paper[];
  pagination: {
    currentPage: number;
    totalPages: number;
    totalCount: number;
    limit: number;
    hasNextPage: boolean;
    hasPrevPage: boolean;
  };
  metadata: ExplorerMetadata;
}

export interface ExplorerFilters {
  date: string;                    // Required: "all" or "YYYY-MM-DD"
  topics: string;                  // Required: "all", "clear", or CSV
  recommendation: string;          // Required: "all", "clear", or CSV
  impact: string;                  // Required: "all", "clear", or CSV
  novelty: string;                 // Required: "all", "clear", or CSV
  relevance: string;               // Required: "all", "clear", or CSV
  scoring: string;                 // Required: "all", "clear", or CSV
  h_index_status: string;          // Required: "all", "clear", or CSV
  highest_h_index_range: string;   // Required: "all" or "min-max"
  average_h_index_range: string;   // Required: "all" or "min-max"
}

export interface SortOptions {
  sortBy: string;
  sortOrder: string;
}

export function useExplorerPapers(
  filters: ExplorerFilters,
  sortOptions: SortOptions,
  limit: number = 30
) {
  return useInfiniteQuery<ExplorerPapersResponse>({
    queryKey: ['papers', 'list', filters, sortOptions, limit],
    queryFn: async ({ pageParam = 1 }) => {
      // Build query params - ALL parameters are required by backend
      const params = new URLSearchParams({
        page: pageParam.toString(),
        limit: limit.toString(),
        sortBy: sortOptions.sortBy,
        sortOrder: sortOptions.sortOrder,
        date: filters.date,
        topics: filters.topics,
        recommendation: filters.recommendation,
        impact: filters.impact,
        novelty: filters.novelty,
        relevance: filters.relevance,
        scoring: filters.scoring,
        h_index_status: filters.h_index_status,
        highest_h_index_range: filters.highest_h_index_range,
        average_h_index_range: filters.average_h_index_range,
      });

      const result = await apiCall(`${API_ENDPOINTS.PAPERS}?${params.toString()}`);
      return result.data;
    },
    getNextPageParam: (lastPage) => {
      return lastPage.pagination.hasNextPage
        ? lastPage.pagination.currentPage + 1
        : undefined;
    },
    initialPageParam: 1,
  });
}
