import { ExplorerHeader } from '../layout/ExplorerHeader';
import { LeftArrow } from '../common/LeftArrow';

interface ExplorerPageErrorProps {
  error: string;
  onRetry: () => void;
}

function getErrorCode(error: string): string {
  if (error.includes('Network Error') || error.includes('fetch')) return '503';
  if (error.includes('Not Found')) return '404';
  if (error.includes('Validation Error')) return '400';
  return '500';
}

function getErrorTitle(error: string): string {
  if (error.includes('Network Error')) return 'Connection Failed';
  if (error.includes('Not Found')) return 'Not Found';
  if (error.includes('Validation Error')) return 'Invalid Data';
  return 'Something Went Wrong';
}

export function ExplorerPageError({ error, onRetry }: ExplorerPageErrorProps) {
  const errorCode = getErrorCode(error);
  const errorTitle = getErrorTitle(error);

  return (
    <div className="h-screen bg-neutral-100 flex flex-col">
      {/* Mobile: Single column layout */}
      <div className="flex flex-col explorerPageDesktop:hidden h-screen">
        <div className="flex flex-row items-center gap-1 pb-4">
          <LeftArrow />
          <ExplorerHeader />
        </div>
        <div className="flex-1 flex items-center justify-center px-5">
          <div className="text-center max-w-md mx-auto">
            <div className="font-header font-bold text-neutral-800 text-[4rem] leading-none mb-4">
              {errorCode}
            </div>
            <h1 className="font-header text-neutral-700 text-[1.5rem] mb-4">
              {errorTitle}
            </h1>
            <p className="font-body text-neutral-600 text-[0.875rem] leading-relaxed mb-6">
              {error}
            </p>
            <button
              onClick={onRetry}
              className="px-6 py-2 bg-neutral-600 hover:bg-neutral-500 transition-colors text-neutral-100 font-header text-[1rem]"
            >
              Retry
            </button>
          </div>
        </div>
      </div>

      {/* Desktop: Three-column layout matching ExplorerPage */}
      <div className="hidden explorerPageDesktop:flex flex-1 overflow-hidden">
        {/* Arrow Column: Fixed, no scroll */}
        <div className="w-16 pt-8">
          <LeftArrow />
        </div>

        {/* Content Column: Header + Error Message */}
        <div className="flex-1 pt-10 px-8">
          <ExplorerHeader />
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center max-w-md mx-auto">
              <div className="font-header font-bold text-neutral-800 text-[6rem] leading-none mb-4">
                {errorCode}
              </div>
              <h1 className="font-header text-neutral-700 text-[2rem] mb-4">
                {errorTitle}
              </h1>
              <p className="font-body text-neutral-600 text-[1rem] leading-relaxed mb-6">
                {error}
              </p>
              <button
                onClick={onRetry}
                className="px-6 py-2 bg-neutral-600 hover:bg-neutral-500 transition-colors text-neutral-100 font-header text-[1rem]"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
