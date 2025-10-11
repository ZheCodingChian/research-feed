import { Paper } from '../../types/api';

interface PaperIndividualAuthorHIndexSectionProps {
  paper: Paper;
}

export function PaperIndividualAuthorHIndexSection({ paper }: PaperIndividualAuthorHIndexSectionProps) {
  if (paper.h_index_status !== 'completed') {
    return null;
  }

  if (!paper.author_h_indexes || paper.author_h_indexes.length === 0) {
    throw new Error('Individual author H-Index data is incomplete');
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Individual Author H-Index</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      {paper.author_h_indexes.map((author, index) => (
        <div key={index} className="flex justify-between">
          {author.profile_url ? (
            <a
              href={author.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-header font-normal text-[1rem] text-neutral-700 underline hover:text-blue"
            >
              {author.name}
            </a>
          ) : (
            <p className="font-header font-normal text-[1rem] text-neutral-700">{author.name}</p>
          )}
          <p className="font-header text-[1rem] text-neutral-700">
            {author.h_index !== null ? author.h_index : 'N/A'}
          </p>
        </div>
      ))}
    </div>
  );
}
