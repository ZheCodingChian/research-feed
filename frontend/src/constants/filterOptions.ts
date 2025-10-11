export interface FilterOption {
  value: string;
  label: string;
}

export const SCORING_OPTIONS: FilterOption[] = [
  { value: 'completed', label: 'Completed' },
  { value: 'not_relevant_enough', label: 'Not Relevant Enough' },
];

export const RECOMMENDATION_OPTIONS: FilterOption[] = [
  { value: 'must_read', label: 'Must Read' },
  { value: 'should_read', label: 'Should Read' },
  { value: 'can_skip', label: 'Can Skip' },
  { value: 'can_ignore', label: 'Can Ignore' },
];

export const IMPACT_OPTIONS: FilterOption[] = [
  { value: 'transformative', label: 'Transformative' },
  { value: 'substantial', label: 'Substantial' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'negligible', label: 'Negligible' },
];

export const NOVELTY_OPTIONS: FilterOption[] = [
  { value: 'groundbreaking', label: 'Groundbreaking' },
  { value: 'significant', label: 'Significant' },
  { value: 'incremental', label: 'Incremental' },
  { value: 'minimal', label: 'Minimal' },
];

export const TOPICS_OPTIONS: FilterOption[] = [
  { value: 'agentic_ai', label: 'Agentic AI' },
  { value: 'proximal_policy_optimization', label: 'Proximal Policy Optimization (PPO)' },
  { value: 'reinforcement_learning', label: 'Reinforcement Learning' },
  { value: 'reasoning_models', label: 'Reasoning Models' },
  { value: 'inference_time_scaling', label: 'Inference Time Scaling' },
];

export const RELEVANCE_OPTIONS: FilterOption[] = [
  { value: 'highly', label: 'Highly Relevant' },
  { value: 'moderately', label: 'Moderately Relevant' },
  { value: 'tangentially', label: 'Tangentially Relevant' },
  { value: 'not_relevant', label: 'Not Relevant' },
];

export const H_INDEX_OPTIONS: FilterOption[] = [
  { value: 'found', label: 'H-Index Found' },
  { value: 'not_found', label: 'H-Index Not Found' },
];
