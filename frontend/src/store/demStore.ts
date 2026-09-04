import { create } from 'zustand';

interface DEMSession {
  session_id: string;
  status: string;
  started_at: string;
  ended_at?: string;
}

interface Mission {
  mission_id: string;
  session_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string;
  created_at: string;
  completed_at?: string;
  reasoning?: string;
  requires_approval?: boolean;
  approval_status?: string;
}

interface AgentInsight {
  insight_id: string;
  insight_type: string;
  title: string;
  summary: string;
  confidence: string;
  severity?: string | null;
  evidence: Array<Record<string, unknown>>;
  inference?: string | null;
  recommended_action?: { action: string; rationale: string; non_executing: boolean } | null;
  links: { goal_id?: string | null; plan_id?: string | null; session_id?: string | null };
  user_message: string;
}

interface AgentDecision {
  session_id: string;
  mission_id?: string;
  decision_id?: string;
  chosen_path?: string;
  reasoning?: string;
  alternatives: string[];
  requires_approval: boolean;
  approval_status: string;
  created_at?: string;
}

interface AgentExecutionState {
  session_id: string;
  goal_id?: string | null;
  plan_id?: string | null;
  goal_status?: string | null;
  plan_status?: string | null;
  mission_count: number;
  completed_missions: number;
  failed_missions: number;
  pending_approval_missions: number;
  autonomy_level?: string | null;
}

interface DEMState {
  activeSession: DEMSession | null;
  missions: Mission[];
  currentMission: Mission | null;
  executionProgress: { status: string; stepCount: number; totalSteps: number } | null;
  insights: AgentInsight[];
  decisions: AgentDecision[];
  executionState: AgentExecutionState | null;
  isLoading: boolean;
  error: string | null;
  setActiveSession: (session: DEMSession | null) => void;
  setMissions: (missions: Mission[]) => void;
  setCurrentMission: (mission: Mission | null) => void;
  setExecutionProgress: (progress: { status: string; stepCount: number; totalSteps: number } | null) => void;
  setInsights: (insights: AgentInsight[]) => void;
  setDecisions: (decisions: AgentDecision[]) => void;
  setExecutionState: (state: AgentExecutionState | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  activeSession: null,
  missions: [],
  currentMission: null,
  executionProgress: null,
  insights: [],
  decisions: [],
  executionState: null,
  isLoading: false,
  error: null,
};

export const useDEMStore = create<DEMState>((set) => ({
  ...initialState,
  setActiveSession: (session) => set({ activeSession: session }),
  setMissions: (missions) => set({ missions }),
  setCurrentMission: (mission) => set({ currentMission: mission }),
  setExecutionProgress: (progress) => set({ executionProgress: progress }),
  setInsights: (insights) => set({ insights }),
  setDecisions: (decisions) => set({ decisions }),
  setExecutionState: (executionState) => set({ executionState }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
