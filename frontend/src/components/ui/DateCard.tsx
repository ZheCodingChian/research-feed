import { Link } from 'react-router-dom';
import { DateMetadata } from '../../types/api';
import { formatDateForCard } from '../../utils/dateUtils';
import { RightArrow } from './RightArrow';

interface DateCardProps {
  dateMetadata: DateMetadata;
}

export function DateCard({ dateMetadata }: DateCardProps) {
  const formattedDate = formatDateForCard(dateMetadata.date);

  return (
    <Link
      to={`/explorer?date=${dateMetadata.date}`}
      className="block w-full bg-neutral-200 py-5 pl-5 pr-5 md:pl-10 md:pr-10 hover:scale-[1.02] transition-all"
    >
    {/* Two column layout: Content on left, Arrow on right */}
      <div className="flex">
        {/* Left column: Date and metrics */}
        <div className="flex-1">
          {/* Date */}
          <div className="mb-4 md:mb-6">
            <span className="font-header font-bold text-neutral-800 text-[1rem] md:text-[1.5rem]">
              {formattedDate}
            </span>
          </div>

          {/* Three metric columns */}
          <div className="flex gap-5 md:gap-10">
            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Total
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {dateMetadata.total_count}
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Must Read
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {dateMetadata.must_read_count}
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1">
                Should Read
              </div>
              <div className="font-body text-neutral-800 text-[1.25rem] md:text-[2rem]">
                {dateMetadata.should_read_count}
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