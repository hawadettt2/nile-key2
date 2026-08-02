import { create } from 'zustand';

export interface SupplierAnalysisResult {
  supplier_id: number;
  analysis_type: string;
  results: Record<string, unknown>;
  generated_at: string;
}

export interface TrendDetectionResult {
  entity_type: string;
  trends: Record<string, unknown>[];
  generated_at: string;
}

interface TradeIntelligenceState {
  supplierAnalysis: SupplierAnalysisResult | null;
  trends: TrendDetectionResult | null;
  analysisType: 'supplier' | 'trends' | null;
  isLoading: boolean;
  error: string | null;
  setSupplierAnalysis: (analysis: SupplierAnalysisResult | null) => void;
  setTrends: (trends: TrendDetectionResult | null) => void;
  setAnalysisType: (type: 'supplier' | 'trends' | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  supplierAnalysis: null,
  trends: null,
  analysisType: null,
  isLoading: false,
  error: null,
};

export const useTradeIntelligenceStore = create<TradeIntelligenceState>((set) => ({
  ...initialState,
  setSupplierAnalysis: (supplierAnalysis) => set({ supplierAnalysis }),
  setTrends: (trends) => set({ trends }),
  setAnalysisType: (analysisType) => set({ analysisType }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
