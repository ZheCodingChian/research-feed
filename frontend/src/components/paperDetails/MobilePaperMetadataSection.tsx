import { Paper } from '../../types/api';

interface MobilePaperMetadataSectionProps {
  paper: Paper;
}

function formatPublishedDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC'
  }).format(date);
}

export function MobilePaperMetadataSection({ paper }: MobilePaperMetadataSectionProps) {
  return (
    <div className="flex flex-col gap-3">
      <p className="font-header text-[1rem]">
        <span className="font-bold text-neutral-800">arXiv ID:</span>{' '}
        <span className="font-normal text-neutral-700">{paper.id}</span>
      </p>

      <p className="font-header text-[1rem]">
        <span className="font-bold text-neutral-800">Published:</span>{' '}
        <span className="font-normal text-neutral-700">{formatPublishedDate(paper.published_date)}</span>
      </p>

      <p className="font-header text-[1rem]">
        <span className="font-bold text-neutral-800">Categories:</span>{' '}
        <span className="font-normal text-neutral-700">{paper.categories.join(', ')}</span>
      </p>

      <a
        href={paper.arxiv_url}
        target="_blank"
        rel="noopener noreferrer"
        className="py-1 w-full bg-neutral-600 hover:bg-neutral-500 text-neutral-100 font-header text-[1rem] text-center transition-colors"
      >
        View on arXiv
      </a>
    </div>
  );
}
