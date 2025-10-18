import { Paper } from '../../types/api';

interface DesktopPaperMetadataSectionProps {
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

export function DesktopPaperMetadataSection({ paper }: DesktopPaperMetadataSectionProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Metadata</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      <div className="flex flex-col gap-1">
        <p className="font-header font-bold text-[1rem] text-neutral-800">arXiv ID</p>
        <p className="font-header font-normal text-[1rem] text-neutral-700">{paper.id}</p>
      </div>

      <div className="flex flex-col gap-1">
        <p className="font-header font-bold text-[1rem] text-neutral-800">Published</p>
        <p className="font-header font-normal text-[1rem] text-neutral-700">
          {formatPublishedDate(paper.published_date)}
        </p>
      </div>

      <div className="flex flex-col gap-1">
        <p className="font-header font-bold text-[1rem] text-neutral-800">Categories</p>
        <div className="flex flex-col">
          {paper.categories.map((cat, idx) => (
            <p key={idx} className="font-header font-normal text-[1rem] text-neutral-700">
              {cat}
            </p>
          ))}
        </div>
      </div>

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
