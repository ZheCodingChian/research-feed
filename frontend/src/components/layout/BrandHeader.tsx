import { TensorplexLogo } from '../common/TensorplexLogo';

export function BrandHeader() {
  return (
    <div className="flex items-start gap-4 md:gap-8">
      <TensorplexLogo />
      <div>
        <h1 className="font-header font-bold text-neutral-800 text-[2rem] md:text-[2.25rem]">
          Research Feed
        </h1>
        <p className="font-body text-neutral-700 text-[0.75rem] md:text-[1rem]">
          Daily feed of research papers curated by AI-powered analysis.
        </p>
      </div>
    </div>
  );
}