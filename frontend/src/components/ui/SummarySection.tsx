import { LaTeXText } from './LaTeXText';

interface SummarySectionProps {
  summary: string;
}

export function SummarySection({ summary }: SummarySectionProps) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-header font-bold text-[1.25rem] text-neutral-800">
        AI Summary
      </h2>
      <p className="font-body font-normal text-[1rem] text-neutral-700">
        <LaTeXText>{summary}</LaTeXText>
      </p>
    </div>
  );
}
