import { BrandHeader } from '../components/ui/BrandHeader';
import { DateCardList } from '../components/ui/DateCardList';
import { LandingPageError } from '../components/ui/LandingPageError';
import { usePapersMetadata } from '../hooks/usePapersMetadata';

export function LandingPage() {
  const { data, isLoading, error, refetch } = usePapersMetadata();

  if (error) {
    return <LandingPageError error={error?.message || 'An unknown error occurred'} />;
  }

  // Normal state - existing layout unchanged
  return (
    <div className="bg-neutral-100">
      {/* Mobile: Stack vertically with fixed header */}
      <div className="flex flex-col landingPageDesktop:hidden h-screen overflow-hidden">
        <div className="px-5 py-8">
          <BrandHeader />
        </div>
        <div className="flex-1 overflow-y-auto px-5 pb-32">
          <DateCardList data={data} isLoading={isLoading} />
        </div>
      </div>

      {/* Desktop: Two columns */}
      <div className="hidden landingPageDesktop:flex gap-16 min-h-screen pt-14 pb-10 px-12">
        {/* Column 1: Header with max-width and sticky positioning */}
        <div className="max-w-[25rem] sticky top-14 self-start">
          <BrandHeader />
        </div>

        {/* Column 2: DateList takes remaining space */}
        <div className="flex-1">
          <DateCardList data={data} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}