import { Link } from 'react-router-dom';
import { AllTimeMetadata } from '../../types/api';
import { formatDateForAllTimeCard } from '../../utils/dateUtils';
import { RightArrow } from '../common/RightArrow';

interface AllTimeCardProps {
  allTimeMetadata: AllTimeMetadata;
  dateRange: { start: string; end: string };
}

export function AllTimeCard({ allTimeMetadata, dateRange }: AllTimeCardProps) {
  const startFormatted = formatDateForAllTimeCard(dateRange.start);
  const endFormatted = formatDateForAllTimeCard(dateRange.end);

  return (
    <Link
      to="/explorer?date=all"
      className="block w-full bg-neutral-200 py-5 px-5 md:px-10 hover:scale-[1.02] transition-all"
    >
      {/* Two column layout: Content on left, Arrow on right */}
      <div className="flex">
        {/* Left column: Title, date range, and metrics */}
        <div className="flex-1">
          {/* Title */}
          <div className="mb-2 md:mb-3">
            <span className="font-header font-bold text-neutral-800 text-[1rem] md:text-[1.5rem]">
              View All Dates
            </span>
          </div>

          {/* Date range */}
          <div className="mb-4 md:mb-6">
            <span className="font-header font-bold text-neutral-600 text-[0.875rem] md:text-[1.125rem]">
              {startFormatted} - {endFormatted}
            </span>
          </div>

          {/* Three metric columns */}
          <div className="flex gap-5 md:gap-10">
            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Total
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {allTimeMetadata.total_count}
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Must Read
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {allTimeMetadata.must_read_count}
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Should Read
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {allTimeMetadata.should_read_count}
              </div>
            </div>
          </div>
        </div>

        {/* Right column: Arrow */}
        <div className="flex items-center justify-center">
          <RightArrow />
        </div>
      </div>
    </Link>
  );
}