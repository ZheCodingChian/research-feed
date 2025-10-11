import { BrandHeader } from '../layout/BrandHeader';

interface LandingPageErrorProps {
  error: string;
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

export function LandingPageError({ error }: LandingPageErrorProps) {
  const errorCode = getErrorCode(error);
  const errorTitle = getErrorTitle(error);

  return (
    <div className="min-h-screen bg-neutral-100 pt-8 pb-8 landingPageDesktop:pt-14 landingPageDesktop:pb-10 px-5 landingPageDesktop:px-12">
      <div className="flex flex-col gap-8">
        <BrandHeader />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center max-w-md mx-auto">
            <div className="font-header font-bold text-neutral-800 text-[4rem] md:text-[6rem] leading-none mb-4">
              {errorCode}
            </div>
            <h1 className="font-header text-neutral-700 text-[1.5rem] md:text-[2rem] mb-4">
              {errorTitle}
            </h1>
            <p className="font-body text-neutral-600 text-[0.875rem] md:text-[1rem] leading-relaxed">
              {error}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
