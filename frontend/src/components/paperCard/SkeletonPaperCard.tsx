export function SkeletonPaperCard() {
  return (
    <div className="bg-neutral-200 px-6 py-4 flex flex-col gap-2 relative overflow-hidden">
      {/* Shimmer overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-neutral-300/50 to-transparent animate-shimmer" />

      {/* Row 1: ArXiv ID and Recommendation Tag */}
      <div className="flex flex-row justify-between items-center">
        <span className="text-neutral-500 font-header font-bold text-[0.875rem] invisible">
          arXiv:2024.12345
        </span>
        <span className="px-2 py-0.5 text-neutral-100 font-header font-normal text-[0.875rem] bg-green invisible">
          Must Read
        </span>
      </div>

      {/* Row 2: Title */}
      <h3 className="text-neutral-800 font-header font-bold text-[1.125em] invisible">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ac convallis ex, non venenatis est.
      </h3>

      {/* Row 3: Authors */}
      <p className="text-neutral-500 font-header font-normal text-[1rem] invisible">
        John Smith, Jane Doe, Bob Johnson, Alice Williams
      </p>

      {/* Row 4: Abstract (truncated to 3 lines) */}
      <p
        className="text-neutral-700 font-body font-normal text-[1rem] invisible"
        style={{
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ac convallis ex, non venenatis est. Fusce ante justo, tempor a accumsan eget, vestibulum quis magna. Aliquam id libero dolor. Vestibulum sit amet egestas ex. Proin vitae congue sem, sagittis commodo elit. Aliquam commodo cursus ipsum quis semper. Aliquam erat volutpat.
      </p>

      {/* Row 5: Topic Tags */}
      <div className="flex flex-row flex-wrap gap-1 pt-1">
        <span className="bg-neutral-600 text-neutral-100 font-header font-normal text-[0.875rem] px-2 py-0.5 invisible">
          RLHF
        </span>
        <span className="bg-neutral-600 text-neutral-100 font-header font-normal text-[0.875rem] px-2 py-0.5 invisible">
          Weak Supervision
        </span>
        <span className="bg-neutral-600 text-neutral-100 font-header font-normal text-[0.875rem] px-2 py-0.5 invisible">
          Diffusion Reasoning
        </span>
      </div>
    </div>
  );
}
