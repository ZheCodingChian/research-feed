import { useState } from 'react';
import { Paper } from '../../types/api';

interface PaperSimilarityScorersSectionProps {
  paper: Paper;
}

export function PaperSimilarityScoresSection({ paper }: PaperSimilarityScorersSectionProps) {
  const [showNormalized, setShowNormalized] = useState(false);

  if (paper.embedding_status !== 'completed') {
    return null;
  }

  const topics = [
    { name: 'Agentic AI', score: paper.agentic_ai_score },
    { name: 'Proximal Policy Optimization (PPO)', score: paper.proximal_policy_optimization_score },
    { name: 'Reinforcement Learning', score: paper.reinforcement_learning_score },
    { name: 'Reasoning Models', score: paper.reasoning_models_score },
    { name: 'Inference Time Scaling', score: paper.inference_time_scaling_score },
  ];

  topics.forEach((topic) => {
    if (topic.score === null) {
      throw new Error(`Score for ${topic.name} is null`);
    }
  });

  const totalScore = topics.reduce((sum, topic) => sum + (topic.score as number), 0);

  const getDisplayValue = (score: number): string => {
    if (showNormalized) {
      const normalized = (score / totalScore) * 100;
      return `${normalized.toFixed(1)}%`;
    }
    return score.toFixed(3);
  };

  const getBarWidth = (score: number): number => {
    if (showNormalized) {
      return (score / totalScore) * 100;
    }
    return score * 100;
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Similarity Scores</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      {topics.map((topic) => (
        <div key={topic.name} className="flex flex-col gap-2">
          <p className="font-header font-bold text-[1rem] text-neutral-800">{topic.name}</p>
          <div className="relative w-full bg-neutral-200 flex items-center py-0.5">
            <div
              className="absolute top-0 left-0 h-full bg-neutral-600"
              style={{ width: `${getBarWidth(topic.score as number)}%` }}
            />
            <span className="relative ml-auto pr-3 font-header text-[0.875rem] text-neutral-900">
              {getDisplayValue(topic.score as number)}
            </span>
          </div>
        </div>
      ))}

      <button
        onClick={() => setShowNormalized(!showNormalized)}
        className="py-1 mt-2 w-full bg-neutral-600 hover:bg-neutral-500 text-neutral-100 font-header text-[1rem] text-center transition-colors"
      >
        {showNormalized ? 'Show Raw Scores ⇄' : 'Show Normalized Scores ⇄'}
      </button>
    </div>
  );
}
