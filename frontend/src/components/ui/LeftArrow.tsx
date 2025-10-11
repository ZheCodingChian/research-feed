import { useNavigate } from 'react-router-dom';

interface LeftArrowProps {
  className?: string;
  onClick?: () => void;
}

export function LeftArrow({ className = '', onClick }: LeftArrowProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate('/');
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`w-16 h-12 pl-4 flex items-center justify-center text-neutral-800 hover:scale-[1.2] transition-all ${className}`}
      aria-label="Back"
    >
      <svg
        className="w-4 h-4 md:w-5 md:h-5"
        viewBox="0 0 512 512"
        fill="currentColor"
        xmlns="http://www.w3.org/2000/svg"
      >
        <polygon points="315.1,48.6 196.9,48.6 354.5,206.1 0,206.1 0,284.9 354.5,284.9 196.9,442.4 315.1,442.4 512,245.5" transform="scale(-1, 1) translate(-512, 0)" />
      </svg>
    </button>
  );
}