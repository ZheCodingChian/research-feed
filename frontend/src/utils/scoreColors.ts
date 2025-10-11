/**
 * Maps recommendation score to Tailwind background color class
 */
export function getRecommendationColor(score: string | null): string {
  if (!score) return 'bg-neutral-500';

  switch (score) {
    case 'Must Read':
      return 'bg-green';
    case 'Should Read':
      return 'bg-blue';
    case 'Can Skip':
      return 'bg-orange';
    case 'Ignore':
      return 'bg-red';
    default:
      return 'bg-neutral-500';
  }
}

/**
 * Maps novelty score to Tailwind background color class
 */
export function getNoveltyColor(score: string | null): string {
  if (!score) return 'bg-neutral-500';

  switch (score) {
    case 'Groundbreaking':
      return 'bg-green';
    case 'Significant':
      return 'bg-blue';
    case 'Incremental':
      return 'bg-orange';
    case 'Minimal':
      return 'bg-red';
    default:
      return 'bg-neutral-500';
  }
}

/**
 * Maps impact score to Tailwind background color class
 */
export function getImpactColor(score: string | null): string {
  if (!score) return 'bg-neutral-500';

  switch (score) {
    case 'Transformative':
      return 'bg-green';
    case 'Substantial':
      return 'bg-blue';
    case 'Moderate':
      return 'bg-orange';
    case 'Negligible':
      return 'bg-red';
    default:
      return 'bg-neutral-500';
  }
}
