// Date metadata for landing page
export interface DateMetadata {
  date: string;
  total_count: number;
  must_read_count: number;
  should_read_count: number;
}

export interface AllTimeMetadata {
  total_count: number;
  must_read_count: number;
  should_read_count: number;
}

export interface AllDatesMetadata {
  total_count: number;
  must_read_count: number;
  should_read_count: number;
}

/**
 * Complete response from /papers/metadata endpoint
 */
export interface PapersMetadataResponse {
  all_dates: AllDatesMetadata;
  dates: DateMetadata[];
}

/**
 * Metadata for explorer page
 */
export interface ExplorerMetadata {
  startDate: string;
  endDate: string;
  totalPapers: number;
  maxHighestHIndex: number;
  maxAverageHIndex: number;
}

/**
 * Topic relevance level
 */
export type RelevanceLevel =
  | "Highly Relevant"
  | "Moderately Relevant"
  | "Tangentially Relevant"
  | "Not Relevant"
  | "not_validated"
  | "below_threshold";

/**
 * Topic relevance justification
 */
export type RelevanceJustification = "below_threshold" | string;

/**
 * Author h-index information
 */
export interface AuthorHIndex {
  name: string;
  h_index: number | null;
  profile_url: string | null;
}

/**
 * Individual paper object
 */
export interface Paper {
  id: string;
  title: string;
  authors: string[];
  categories: string[];
  category_enhancement: string | null;
  abstract: string;
  published_date: string;
  arxiv_url: string;
  pdf_url: string;
  scraper_status: string | null;
  intro_status: string | null;
  embedding_status: string | null;
  agentic_ai_score: number | null;
  proximal_policy_optimization_score: number | null;
  reinforcement_learning_score: number | null;
  reasoning_models_score: number | null;
  inference_time_scaling_score: number | null;
  llm_validation_status: string | null;
  agentic_ai_relevance: RelevanceLevel | null;
  proximal_policy_optimization_relevance: RelevanceLevel | null;
  reinforcement_learning_relevance: RelevanceLevel | null;
  reasoning_models_relevance: RelevanceLevel | null;
  inference_time_scaling_relevance: RelevanceLevel | null;
  agentic_ai_justification: RelevanceJustification | null;
  proximal_policy_optimization_justification: RelevanceJustification | null;
  reinforcement_learning_justification: RelevanceJustification | null;
  reasoning_models_justification: RelevanceJustification | null;
  inference_time_scaling_justification: RelevanceJustification | null;
  llm_score_status: string | null;
  summary: string | null;
  novelty_score: string | null;
  novelty_justification: string | null;
  impact_score: string | null;
  impact_justification: string | null;
  recommendation_score: string | null;
  recommendation_justification: string | null;
  h_index_status: string | null;
  semantic_scholar_url: string | null;
  total_authors: number | null;
  authors_found: number | null;
  highest_h_index: number | null;
  average_h_index: number | null;
  notable_authors_count: number | null;
  author_h_indexes: AuthorHIndex[] | null;
}

