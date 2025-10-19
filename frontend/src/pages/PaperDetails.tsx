import { useParams, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { OverlayScrollbarsComponent } from 'overlayscrollbars-react';
import { usePaperDetails } from '../hooks/usePaperDetails';
import { PaperDetailsHeader } from '../components/layout/PaperDetailsHeader';
import { MobilePaperMetadataSection } from '../components/paperDetails/MobilePaperMetadataSection';
import { SummarySection } from '../components/paperDetails/SummarySection';
import { AbstractSection } from '../components/paperDetails/AbstractSection';
import { PaperScoringSection } from '../components/paperDetails/PaperScoringSection';
import { PaperTopicRelevanceSection } from '../components/paperDetails/PaperTopicRelevanceSection';
import { PaperSimilarityScoresSection } from '../components/paperDetails/PaperSimilarityScoresSection';
import { PaperHIndexSection } from '../components/paperDetails/PaperHIndexSection';
import { PaperIndividualAuthorHIndexSection } from '../components/paperDetails/PaperIndividualAuthorHIndexSection';
import { LeftArrow } from '../components/common/LeftArrow';
import { PaperDetailsRightColumn } from '../components/paperDetails/PaperDetailsRightColumn';

export function PaperDetails() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  if (!id) {
    return <Navigate to="/explorer" replace />;
  }

  const { data: paper, isLoading, error } = usePaperDetails(id);

  const handleBack = () => {
    const from = location.state?.from;
    if (from) {
      navigate(from);
    } else {
      navigate('/');
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen bg-neutral-100 flex flex-col">
        <div className="max-w-[1440px] mx-auto w-full h-full flex flex-col">
          {/* Mobile: Loading state */}
          <div className="flex flex-col paperDetailsDesktop:hidden h-screen overflow-hidden">
          <div className="flex flex-row items-center gap-1">
            <LeftArrow onClick={handleBack} />
          </div>

          <div className="flex-1 flex items-center justify-center">
            <svg
              className="animate-spin w-[3rem] h-[3rem] text-neutral-600"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        </div>

        {/* Desktop: Loading state */}
        <div className="hidden paperDetailsDesktop:flex flex-1 overflow-hidden">
          <div className="w-16 pt-8">
            <LeftArrow onClick={handleBack} />
          </div>

          <div className="flex-1 flex items-center justify-center">
            <svg
              className="animate-spin w-[3rem] h-[3rem] text-neutral-600"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        </div>
        </div>
      </div>
    );
  }

  if (error || !paper) {
    return (
      <div className="h-screen bg-neutral-100 flex items-center justify-center">
        <div className="max-w-[1440px] mx-auto w-full h-full flex items-center justify-center">
          <div className="flex flex-col gap-4 items-center">
            <p className="font-header font-bold text-neutral-800 text-[1.5rem]">
              Paper Not Found
            </p>
            <a
              href="/explorer"
              className="font-header text-neutral-100 bg-neutral-600 hover:bg-neutral-500 px-4 py-2"
            >
              Back to Explorer
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-neutral-100 flex flex-col">
      <div className="max-w-[1440px] mx-auto w-full h-full flex flex-col">
        {/* Mobile: Single column layout */}
        <div className="flex flex-col paperDetailsDesktop:hidden h-screen overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <div className="flex flex-row items-center gap-1">
            <LeftArrow onClick={handleBack} />
          </div>

          <div className="flex flex-col px-8 gap-6">
            <PaperDetailsHeader paper={paper} />
            <MobilePaperMetadataSection paper={paper} />
            {paper.summary && <SummarySection summary={paper.summary} />}
            <AbstractSection abstract={paper.abstract} />
            <PaperScoringSection paper={paper} />
            <PaperTopicRelevanceSection paper={paper} />
            <PaperSimilarityScoresSection paper={paper} />
            <PaperHIndexSection paper={paper} />
            <PaperIndividualAuthorHIndexSection paper={paper} />
            <div className="h-16"> {/* Spacer to avoid content being hidden behind bottom nav */}
            </div>
          </div>
        </div>
      </div>

      {/* Desktop: Three-column layout */}
      <div className="hidden paperDetailsDesktop:flex flex-1 overflow-hidden">
        {/* Arrow Column: Fixed, no scroll */}
        <div className="w-16 pt-8">
          <LeftArrow onClick={handleBack} />
        </div>

        {/* Content Column: Scrollable with OverlayScrollbars */}
        <OverlayScrollbarsComponent
          options={{
            scrollbars: {
              autoHide: 'leave',
              autoHideDelay: 1300,
              theme: 'os-theme-dark',
            },
          }}
          className="flex-1 pt-12 pb-16 px-8"
        >
          <div className="flex flex-col gap-6">
            <PaperDetailsHeader paper={paper} />
            {paper.summary && <SummarySection summary={paper.summary} />}
            <AbstractSection abstract={paper.abstract} />
          </div>
        </OverlayScrollbarsComponent>

        {/* Right Column: Paper metadata and details */}
        <OverlayScrollbarsComponent
          options={{
            scrollbars: {
              autoHide: 'leave',
              autoHideDelay: 1300,
              theme: 'os-theme-dark',
            },
          }}
          className="w-[450px] pt-12 pb-16 pl-8 pr-16"
        >
          <PaperDetailsRightColumn paper={paper} />
        </OverlayScrollbarsComponent>
        </div>
      </div>
    </div>
  );
}
