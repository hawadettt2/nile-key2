import { api } from './api';

export interface ExportReadinessRequest {
  product_id?: number;
  hs_code?: string;
  product_name?: string;
  target_market: string;
}

export interface ExportReadinessSection {
  title: string;
  source: string;
  confidence: number | null;
  data: Record<string, unknown> | null;
  availability: 'available' | 'partial' | 'not_available';
  notes: string | null;
}

export interface ExportReadinessReport {
  report_id: string;
  product: {
    product_id: number | null;
    hs_code: string | null;
    name: string;
  };
  target_market: string;
  sections: ExportReadinessSection[];
  action_checklist: string[];
  recommendation: string | null;
  data_quality_note: string;
  generated_at: string;
}

export const analyzeExportReadiness = (data: ExportReadinessRequest) =>
  api.post<ExportReadinessReport>('/api/v1/export-readiness/analyze', data);
