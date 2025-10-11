import { Paper } from '../../types/api';
import { getRecommendationColor, getNoveltyColor, getImpactColor } from '../../utils/scoreColors';

interface PaperScoringSectionProps {
  paper: Paper;
}

export function PaperScoringSection({ paper }: PaperScoringSectionProps) {
  // Only render if LLM scoring is completed
  if (paper.llm_score_status !== 'completed') {
    return null;
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Title and divider */}
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Scoring</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      {/* Recommendation */}
      {paper.recommendation_score && (
        <div className="flex flex-col gap-2">
          <p className="font-header font-bold text-[1rem] text-neutral-800">Recommendation</p>
          <span className={`px-2 py-0.5 text-[0.875rem] font-header font-normal text-neutral-100 ${getRecommendationColor(paper.recommendation_score)} w-fit`}>
            {paper.recommendation_score}
          </span>
          {paper.recommendation_justification && (
            <p className="font-body font-normal text-[0.875rem] text-neutral-700">
              {paper.recommendation_justification}
            </p>
          )}
        </div>
      )}

      {/* Novelty */}
      {paper.novelty_score && (
        <div className="flex flex-col gap-2">
          <p className="font-header font-bold text-[1rem] text-neutral-800">Novelty</p>
          <span className={`px-2 py-0.5 text-[0.875rem] font-header font-normal text-neutral-100 ${getNoveltyColor(paper.novelty_score)} w-fit`}>
            {paper.novelty_score}
          </span>
          {paper.novelty_justification && (
            <p className="font-body font-normal text-[0.875rem] text-neutral-700">
              {paper.novelty_justification}
            </p>
          )}
        </div>
      )}

      {/* Potential Impact */}
      {paper.impact_score && (
        <div className="flex flex-col gap-2">
          <p className="font-header font-bold text-[1rem] text-neutral-800">Potential Impact</p>
          <span className={`px-2 py-0.5 text-[0.875rem] font-header font-normal text-neutral-100 ${getImpactColor(paper.impact_score)} w-fit`}>
            {paper.impact_score}
          </span>
          {paper.impact_justification && (
            <p className="font-body font-normal text-[0.875rem] text-neutral-700">
              {paper.impact_justification}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
