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

interface DEMState {
  activeSession: DEMSession | null;
  missions: Mission[];
  currentMission: Mission | null;
  executionProgress: { status: string; stepCount: number; totalSteps: number } | null;
  isLoading: boolean;
  error: string | null;
  setActiveSession: (session: DEMSession | null) => void;
  setMissions: (missions: Mission[]) => void;
  setCurrentMission: (mission: Mission | null) => void;
  setExecutionProgress: (progress: { status: string; stepCount: number; totalSteps: number } | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  activeSession: null,
  missions: [],
  currentMission: null,
  executionProgress: null,
  isLoading: false,
  error: null,
};

export const useDEMStore = create<DEMState>((set) => ({
  ...initialState,
  setActiveSession: (session) => set({ activeSession: session }),
  setMissions: (missions) => set({ missions }),
  setCurrentMission: (mission) => set({ currentMission: mission }),
  setExecutionProgress: (progress) => set({ executionProgress: progress }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
