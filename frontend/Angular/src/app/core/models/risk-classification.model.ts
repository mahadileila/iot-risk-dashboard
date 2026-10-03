export interface RiskClassificationBand {
  label: string;
  min_score: number | null;
  max_score: number | null;
  color: string;
  description: string | null;
}