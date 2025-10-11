interface RightArrowProps {
  className?: string;
}

export function RightArrow({ className = "h-[0.75rem] w-[0.75rem] md:h-[1.25rem] md:w-[1.25rem]" }: RightArrowProps) {
  return (
    <svg
      className={`fill-neutral-600 ${className}`}
      viewBox="0 0 512 512"
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="315.1,48.6 196.9,48.6 354.5,206.1 0,206.1 0,284.9 354.5,284.9 196.9,442.4 315.1,442.4 512,245.5" />
    </svg>
  );
}