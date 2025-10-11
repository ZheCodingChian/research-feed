import { useQuery } from '@tanstack/react-query';
import { PapersMetadataResponse } from '../types/api';
import { apiCall, API_ENDPOINTS } from '../config/api';

export function usePapersMetadata() {
  return useQuery({
    queryKey: ['papers', 'metadata'],
    queryFn: async () => {
      const result = await apiCall(API_ENDPOINTS.PAPERS_METADATA);

      // Data Validation Errors
      if (!result.metadata || !result.metadata.all_dates || !result.metadata.dates) {
        throw new Error('Data Validation Error: Missing required fields');
      }

      if (!Array.isArray(result.metadata.dates)) {
        throw new Error('Data Validation Error: dates must be an array');
      }

      return result.metadata as PapersMetadataResponse;
    },
  });
}