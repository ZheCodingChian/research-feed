import { Paper } from '../../types/api';
import { LaTeXText } from './LaTeXText';

interface PaperDetailsHeaderProps {
  paper: Paper;
}

export function PaperDetailsHeader({ paper }: PaperDetailsHeaderProps) {
  const renderAuthors = () => {
    if (paper.h_index_status === 'completed' && paper.author_h_indexes && paper.author_h_indexes.length > 0) {
      return paper.author_h_indexes.map((author, index) => (
        <span key={index}>
          {author.profile_url ? (
            <a
              href={author.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-blue"
            >
              {author.name}
            </a>
          ) : (
            <span>{author.name}</span>
          )}
          {index < paper.author_h_indexes!.length - 1 && ', '}
        </span>
      ));
    } else {
      return paper.authors.join(', ');
    }
  };

  return (
    <div className="flex flex-col gap-1">
      <p className="font-header font-normal text-[1rem] text-neutral-700">
        Research Analysis
      </p>

      <h1 className="font-header font-bold text-[1.5rem] text-neutral-800">
        <LaTeXText>{paper.title}</LaTeXText>
      </h1>

      <p className="font-header font-normal text-[1rem] text-neutral-700">
        {renderAuthors()}
      </p>
    </div>
  );
}
