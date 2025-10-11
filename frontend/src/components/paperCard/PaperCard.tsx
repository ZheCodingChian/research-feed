import { RefObject } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { OverlayScrollbarsComponentRef } from 'overlayscrollbars-react';
import { Paper } from '../../types/api';
import { LaTeXText } from '../common/LaTeXText';

interface PaperCardProps {
  paper: Paper;
  scrollRef?: RefObject<OverlayScrollbarsComponentRef> | RefObject<HTMLDivElement>;
}

export function PaperCard({ paper, scrollRef }: PaperCardProps) {
  const location = useLocation();

  const handleClick = () => {
    // Save scroll position to sessionStorage before navigation
    console.log('[SCROLL] PaperCard clicked, saving scroll position...');
    console.log('[SCROLL] scrollRef:', scrollRef);

    let scrollTop = 0;

    if (scrollRef?.current) {
      const current = scrollRef.current as any;
      console.log('[SCROLL] scrollRef.current:', current);

      // Check if it's an OverlayScrollbarsComponentRef
      if ('osInstance' in current && typeof current.osInstance === 'function') {
        // Desktop: OverlayScrollbars
        const osInstance = current.osInstance();
        console.log('[SCROLL] Desktop - osInstance:', osInstance);
        if (osInstance) {
          const { viewport } = osInstance.elements();
          scrollTop = viewport.scrollTop;
          console.log('[SCROLL] Desktop scrollTop:', scrollTop);
        }
      } else if ('scrollTop' in current) {
        // Mobile: Native div
        scrollTop = current.scrollTop;
        console.log('[SCROLL] Mobile scrollTop:', scrollTop);
      }
    } else {
      console.log('[SCROLL] No scrollRef available');
    }

    const scrollData = {
      path: location.pathname + location.search,
      scrollTop: scrollTop,
      timestamp: Date.now()
    };

    console.log('[SCROLL] Saving to sessionStorage:', scrollData);
    sessionStorage.setItem('explorerScrollPosition', JSON.stringify(scrollData));
    console.log('[SCROLL] Saved successfully!');
  };

  // Helper function to check if a topic is relevant
  const isRelevant = (relevance: string | null): boolean => {
    if (!relevance) return false;
    return ['Highly Relevant', 'Moderately Relevant', 'Tangentially Relevant'].includes(relevance);
  };

  // Determine which topics to show
  const topics: string[] = [];
  if (isRelevant(paper.agentic_ai_relevance)) topics.push('Agentic AI');
  if (isRelevant(paper.proximal_policy_optimization_relevance)) topics.push('PPO');
  if (isRelevant(paper.reinforcement_learning_relevance)) topics.push('Reinforcement Learning');
  if (isRelevant(paper.reasoning_models_relevance)) topics.push('Reasoning Models');
  if (isRelevant(paper.inference_time_scaling_relevance)) topics.push('Inference Time Scaling');

  // Determine if recommendation tag should be shown
  const showRecommendationTag =
    paper.recommendation_score === 'Must Read' ||
    paper.recommendation_score === 'Should Read';

  return (
    <Link to={`/paper/${paper.id}`} state={{ from: location.pathname + location.search }} onClick={handleClick}>
      <div className="bg-neutral-200 hover:scale-[1.01] transition-all px-6 py-4 flex flex-col gap-2 cursor-pointer">
      {/* Row 1: ArXiv ID and Recommendation Tag */}
      <div className="flex flex-row justify-between items-center">
        <span className="text-neutral-500 font-header font-bold text-[0.75rem] explorerPageDesktop:text-[0.875rem]">
          {paper.id}
        </span>
        {showRecommendationTag && (
          <span
            className={`px-2 py-0.5 text-neutral-100 font-header font-normal text-[0.75rem] explorerPageDesktop:text-[0.875rem] ${
              paper.recommendation_score === 'Must Read'
                ? 'bg-green'
                : 'bg-blue'
            }`}
          >
            {paper.recommendation_score}
          </span>
        )}
      </div>

      <h3 className="text-neutral-800 font-header font-bold text-[1rem] explorerPageDesktop:text-[1.125rem]">
        <LaTeXText>{paper.title}</LaTeXText>
      </h3>

      {/* Row 3: Authors */}
      <p className="text-neutral-500 font-header font-normal text-[0.875rem] explorerPageDesktop:text-[1rem] line-clamp-2">
        {paper.authors.join(', ')}
      </p>

      {/* Row 4: Abstract (5 lines mobile, 3 lines desktop) */}
      <p className="text-neutral-700 font-body font-normal text-[0.875rem] explorerPageDesktop:text-[1rem] line-clamp-5 explorerPageDesktop:line-clamp-3">
        {paper.abstract}
      </p>

      {/* Row 5: Topic Tags */}
      {topics.length > 0 && (
        <div className="flex flex-row flex-wrap gap-1 pt-1">
          {topics.map((topic) => (
            <span
              key={topic}
              className="bg-neutral-600 text-neutral-100 font-header font-normal text-[0.75rem] explorerPageDesktop:text-[0.875rem] px-2 py-0.5"
            >
              {topic}
            </span>
          ))}
        </div>
      )}
      </div>
    </Link>
  );
}
