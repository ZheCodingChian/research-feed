import { RelevanceLevel } from '../types/api';

export function getRelevanceColor(relevance: RelevanceLevel): string {
  switch (relevance) {
    case 'Highly Relevant':
      return 'bg-green';
    case 'Moderately Relevant':
      return 'bg-blue';
    case 'Tangentially Relevant':
      return 'bg-orange';
    case 'Not Relevant':
      return 'bg-red';
    default:
      return 'bg-neutral-500';
  }
}
