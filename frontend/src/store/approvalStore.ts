import { create } from 'zustand';

export interface ApprovalItem {
  mission_id: string;
  session_id: string;
  user_id: number;
  mission_type?: string;
  status: string;
  requires_approval: boolean;
  approval_status: string;
  reasoning?: string;
  created_at?: string;
}

interface ApprovalState {
  approvals: ApprovalItem[];
  isLoading: boolean;
  error: string | null;
  setApprovals: (approvals: ApprovalItem[]) => void;
  addApproval: (approval: ApprovalItem) => void;
  removeApproval: (missionId: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  approvals: [],
  isLoading: false,
  error: null,
};

export const useApprovalStore = create<ApprovalState>((set) => ({
  ...initialState,
  setApprovals: (approvals) => set({ approvals }),
  addApproval: (approval) => set((state) => ({ approvals: [...state.approvals, approval] })),
  removeApproval: (missionId) => set((state) => ({ approvals: state.approvals.filter(a => a.mission_id !== missionId) })),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
