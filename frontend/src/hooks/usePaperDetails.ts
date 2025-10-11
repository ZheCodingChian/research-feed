import { useQuery } from '@tanstack/react-query';
import { apiCall, API_ENDPOINTS } from '../config/api';
import { Paper } from '../types/api';

interface PaperDetailsResponse {
  success: boolean;
  data: Paper;
}

export function usePaperDetails(arxivId: string) {
  return useQuery<Paper>({
    queryKey: ['paper', 'details', arxivId],
    queryFn: async () => {
      const result: PaperDetailsResponse = await apiCall(
        `${API_ENDPOINTS.PAPER_DETAILS}/${arxivId}`
      );
      return result.data;
    },
    staleTime: 2 * 60 * 60 * 1000,
    gcTime: 2 * 60 * 60 * 1000,
  });
}
