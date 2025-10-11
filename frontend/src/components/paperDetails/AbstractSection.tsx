import { LaTeXText } from '../common/LaTeXText';

interface AbstractSectionProps {
  abstract: string;
}

export function AbstractSection({ abstract }: AbstractSectionProps) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-header font-bold text-[1.25rem] text-neutral-800">
        Abstract
      </h2>
      <p className="font-body font-normal text-[1rem] text-neutral-700">
        <LaTeXText>{abstract}</LaTeXText>
      </p>
    </div>
  );
}
