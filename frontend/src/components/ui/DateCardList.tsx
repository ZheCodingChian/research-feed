import { PapersMetadataResponse } from '../../types/api';
import { getDateRange } from '../../utils/dateUtils';
import { AllTimeCard } from './AllTimeCard';
import { DateCard } from './DateCard';
import { SkeletonDateCard } from './SkeletonDateCard';

interface DateCardListProps {
  data: PapersMetadataResponse | undefined;
  isLoading: boolean;
}

export function DateCardList({ data, isLoading }: DateCardListProps) {
  // Loading state - show 10 skeleton cards
  if (isLoading) {
    return (
      <div className="flex flex-col gap-5">
        {Array.from({ length: 10 }, (_, i) => (
          <SkeletonDateCard key={`skeleton-${i}`} />
        ))}
      </div>
    );
  }


  // Empty state
  if (!data || data.dates.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="font-body text-neutral-600 text-sm">
          No research papers available yet.
        </p>
      </div>
    );
  }

  // Success state - render cards
  const dateRange = getDateRange(data.dates);

  return (
    <div className="flex flex-col gap-3 md:gap-5">
      {/* AllTimeCard first */}
      <AllTimeCard
        allTimeMetadata={data.all_dates}
        dateRange={dateRange}
      />

      {/* Individual DateCards */}
      {data.dates.map((dateData) => (
        <DateCard
          key={dateData.date}
          dateMetadata={dateData}
        />
      ))}
    </div>
  );
}