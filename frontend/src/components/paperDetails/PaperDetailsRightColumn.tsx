import { Paper } from '../../types/api';
import { DesktopPaperMetadataSection } from './DesktopPaperMetadataSection';
import { PaperScoringSection } from './PaperScoringSection';
import { PaperTopicRelevanceSection } from './PaperTopicRelevanceSection';
import { PaperSimilarityScoresSection } from './PaperSimilarityScoresSection';
import { PaperHIndexSection } from './PaperHIndexSection';
import { PaperIndividualAuthorHIndexSection } from './PaperIndividualAuthorHIndexSection';

interface PaperDetailsRightColumnProps {
  paper: Paper;
}

export function PaperDetailsRightColumn({ paper }: PaperDetailsRightColumnProps) {
  return (
    <div className="flex flex-col gap-8">
      <DesktopPaperMetadataSection paper={paper} />
      <PaperScoringSection paper={paper} />
      <PaperTopicRelevanceSection paper={paper} />
      <PaperSimilarityScoresSection paper={paper} />
      <PaperHIndexSection paper={paper} />
      <PaperIndividualAuthorHIndexSection paper={paper} />
    </div>
  );
}
