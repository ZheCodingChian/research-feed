interface MobileFilterSortButtonsProps {
  onFilterClick: () => void;
  onSortClick: () => void;
}

export function MobileFilterSortButtons({
  onFilterClick,
  onSortClick,
}: MobileFilterSortButtonsProps) {
  return (
    <div className="flex flex-row gap-3">
        {/* Filter Button */}
        <button
          onClick={onFilterClick}
          className="bg-neutral-200 py-1 px-3 flex items-center justify-center gap-2"
        >
          <svg
            width="1rem"
            height="1rem"
            viewBox="0 0 13 10"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M0.125 1.45833C0.125 1.06713 0.442135 0.75 0.833333 0.75H12.1667C12.5579 0.75 12.875 1.06713 12.875 1.45833C12.875 1.84953 12.5579 2.16667 12.1667 2.16667H0.833333C0.442135 2.16667 0.125 1.84953 0.125 1.45833ZM2.25 5C2.25 4.60879 2.56713 4.29167 2.95833 4.29167H10.0417C10.4329 4.29167 10.75 4.60879 10.75 5C10.75 5.39121 10.4329 5.70833 10.0417 5.70833H2.95833C2.56713 5.70833 2.25 5.39121 2.25 5ZM4.375 8.54167C4.375 8.15045 4.69213 7.83333 5.08333 7.83333H7.91667C8.30788 7.83333 8.625 8.15045 8.625 8.54167C8.625 8.93288 8.30788 9.25 7.91667 9.25H5.08333C4.69213 9.25 4.375 8.93288 4.375 8.54167Z"
              fill="#333331"
            />
          </svg>
          <span className="text-neutral-800 font-header font-bold text-[0.75rem]">
            Filter
          </span>
        </button>

        {/* Sort Button */}
        <button
          onClick={onSortClick}
          className="bg-neutral-200 py-1 px-3 flex items-center justify-center gap-2"
        >
          <svg
            width="1rem"
            height="1rem"
            viewBox="0 0 13 10"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M9.33337 9.78125C9.47709 9.78125 9.61472 9.72301 9.71474 9.61983L12.5481 6.69795C12.7524 6.48732 12.7472 6.15097 12.5365 5.94676C12.3259 5.74248 11.9895 5.74765 11.7853 5.9583L9.86462 7.93902V0.750001C9.86462 0.45661 9.62676 0.218751 9.33337 0.218751C9.03998 0.218751 8.80212 0.45661 8.80212 0.750001V7.93902L6.88141 5.9583C6.67719 5.74765 6.34088 5.74248 6.13022 5.94676C5.91956 6.15097 5.91439 6.48732 6.11867 6.69795L8.952 9.61983C9.05202 9.72301 9.18965 9.78125 9.33337 9.78125ZM3.66671 9.78125C3.9601 9.78125 4.19796 9.5434 4.19796 9.25V2.06098L6.11867 4.0417C6.32289 4.25236 6.6592 4.25753 6.86986 4.05324C7.08052 3.84903 7.08569 3.51271 6.88141 3.30205L4.04809 0.38018C3.94804 0.276977 3.81043 0.218751 3.66671 0.218751C3.52298 0.218751 3.38538 0.276977 3.28533 0.38018L0.451993 3.30205C0.247738 3.51271 0.252916 3.84903 0.463546 4.05324C0.674183 4.25753 1.01051 4.25236 1.21476 4.0417L3.13546 2.06098V9.25C3.13546 9.5434 3.37331 9.78125 3.66671 9.78125Z"
              fill="#333331"
            />
          </svg>
          <span className="text-neutral-800 font-header font-bold text-[0.75rem]">
            Sort
          </span>
        </button>
    </div>
  );
}
