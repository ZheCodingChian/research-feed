import { Paper } from '../../types/api';

interface PaperHIndexSectionProps {
  paper: Paper;
}

export function PaperHIndexSection({ paper }: PaperHIndexSectionProps) {
  if (paper.h_index_status !== 'completed') {
    return null;
  }

  if (
    paper.authors_found === null ||
    paper.total_authors === null ||
    paper.highest_h_index === null ||
    paper.average_h_index === null ||
    paper.notable_authors_count === null ||
    paper.semantic_scholar_url === null
  ) {
    throw new Error('Author H-Index data is incomplete');
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Author H-Index</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      <div className="flex justify-between">
        <p className="font-header text-[1rem] text-neutral-800">Authors Found</p>
        <p className="font-header text-[1rem] text-neutral-700">
          {paper.authors_found}/{paper.total_authors}
        </p>
      </div>

      <div className="flex justify-between">
        <p className="font-header text-[1rem] text-neutral-800">Highest H-Index</p>
        <p className="font-header text-[1rem] text-neutral-700">{paper.highest_h_index}</p>
      </div>

      <div className="flex justify-between">
        <p className="font-header text-[1rem] text-neutral-800">Average H-Index</p>
        <p className="font-header text-[1rem] text-neutral-700">{paper.average_h_index.toFixed(2)}</p>
      </div>

      <div className="flex justify-between">
        <p className="font-header text-[1rem] text-neutral-800">Notable Authors (H&gt;5)</p>
        <p className="font-header text-[1rem] text-neutral-700">{paper.notable_authors_count}</p>
      </div>

      <a
        href={paper.semantic_scholar_url}
        target="_blank"
        rel="noopener noreferrer"
        className="py-1 w-full bg-neutral-600 hover:bg-neutral-500 text-neutral-100 font-header text-[1rem] text-center transition-colors"
      >
        View Paper on Semantic Scholar
      </a>
    </div>
  );
}
