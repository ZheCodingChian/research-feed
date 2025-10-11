export function SkeletonDateCard() {
  return (
    <div className="w-full bg-neutral-200 py-5 pl-5 pr-5 md:pl-10 md:pr-10 relative overflow-hidden">
      {/* Shimmer overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-neutral-300/50 to-transparent animate-shimmer" />

      {/* Two column layout: Content on left, Arrow on right - exact same structure as DateCard */}
      <div className="flex">
        {/* Left column: Date and metrics */}
        <div className="flex-1">
          {/* Date */}
          <div className="mb-4 md:mb-6">
            <span className="font-header font-bold text-neutral-900 text-[1rem] md:text-[1.5rem] invisible">
              Saturday, 21 September 2024
            </span>
          </div>

          {/* Three metric columns */}
          <div className="flex gap-5 md:gap-10">
            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1 invisible">
                Total
              </div>
              <div className="font-body text-neutral-900 text-[1.25rem] md:text-[2rem] invisible">
                999
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1 invisible">
                Must Read
              </div>
              <div className="font-body text-neutral-900 text-[1.25rem] md:text-[2rem] invisible">
                999
              </div>
            </div>

            <div>
              <div className="font-header text-neutral-600 text-[0.75rem] md:text-[1rem] mb-1 invisible">
                Should Read
              </div>
              <div className="font-body text-neutral-900 text-[1.25rem] md:text-[2rem] invisible">
                999
              </div>
            </div>
          </div>
        </div>

        {/* Right column: Arrow */}
        <div className="flex items-center justify-center">
          <div className="h-[0.75rem] w-[0.75rem] md:h-[1.25rem] md:w-[1.25rem] invisible" />
        </div>
      </div>
    </div>
  );
}