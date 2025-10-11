import { Paper } from '../../types/api';
import { getRelevanceColor } from '../../utils/relevanceColors';

interface PaperTopicRelevanceSectionProps {
  paper: Paper;
}

export function PaperTopicRelevanceSection({ paper }: PaperTopicRelevanceSectionProps) {
  if (paper.llm_validation_status !== 'completed') {
    return null;
  }

  const topics = [
    {
      name: 'Agentic AI',
      relevance: paper.agentic_ai_relevance,
      justification: paper.agentic_ai_justification,
    },
    {
      name: 'Proximal Policy Optimization (PPO)',
      relevance: paper.proximal_policy_optimization_relevance,
      justification: paper.proximal_policy_optimization_justification,
    },
    {
      name: 'Reinforcement Learning',
      relevance: paper.reinforcement_learning_relevance,
      justification: paper.reinforcement_learning_justification,
    },
    {
      name: 'Reasoning Models',
      relevance: paper.reasoning_models_relevance,
      justification: paper.reasoning_models_justification,
    },
    {
      name: 'Inference Time Scaling',
      relevance: paper.inference_time_scaling_relevance,
      justification: paper.inference_time_scaling_justification,
    },
  ];

  const validTopics = topics.filter(
    (topic) => topic.relevance !== 'not_validated' && topic.relevance !== null
  );

  if (validTopics.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h2 className="font-header font-bold text-[1rem] text-neutral-800">Topic Relevance</h2>
        <div className="w-fill h-[3px] bg-neutral-300"></div>
      </div>

      {validTopics.map((topic) => (
        <div key={topic.name} className="flex flex-col gap-2">
          <p className="font-header font-bold text-[1rem] text-neutral-800">{topic.name}</p>
          <span
            className={`px-2 py-0.5 text-[0.875rem] font-header font-normal text-neutral-100 ${getRelevanceColor(topic.relevance!)} w-fit`}
          >
            {topic.relevance}
          </span>
          {topic.justification && topic.justification !== 'below_threshold' && (
            <p className="font-body font-normal text-[0.875rem] text-neutral-700">
              {topic.justification}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
