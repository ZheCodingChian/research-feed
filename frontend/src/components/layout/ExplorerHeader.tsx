import { useSearchParams } from 'react-router-dom';

function formatDate(dateString: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC'
  }).format(date);
}

export function ExplorerHeader() {
  const [searchParams] = useSearchParams();
  const date = searchParams.get('date') || 'all';

  return (
    <div className="bg-neutral-100 w-full">
      <h1 className="text-neutral-800 font-bold text-[1.25rem] explorerPageDesktop:text-[1.5rem] font-header">
        {date === 'all' ? 'All Dates' : formatDate(date)}
      </h1>
    </div>
  );
}