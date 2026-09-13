import { render, screen, act, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@/services/api', () => ({
  connectToDEM: () => Promise.resolve({ data: { session_id: 'test-session-id' } }),
  getDEMSessions: () => Promise.resolve({ data: [] }),
}));

const mockUseAuthStore = vi.fn();
vi.mock('@/store/authStore', () => ({
  useAuthStore: (selector?: (s: any) => any) => {
    const state = mockUseAuthStore();
    if (typeof selector === 'function') {
      return selector(state);
    }
    return state;
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'ar' },
  }),
  I18nextProvider: ({ children }: any) => children,
}));

import { Avatar } from '@/pages/Avatar';

function renderAvatar() {
  return render(
    <BrowserRouter>
      <Avatar />
    </BrowserRouter>
  );
}

const getWsInstance = async () => {
  await waitFor(() => {
    expect((global as any).WebSocket.mock.results.length).toBeGreaterThan(0);
  });
  return (global as any).WebSocket.mock.results?.[0]?.value;
};

describe('Avatar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('avatar_session_id', 'test-session-id');
    mockUseAuthStore.mockReturnValue({
      user: { id: 1, email: 'test@example.com', username: 'test', full_name: 'Test', role: 'owner', phone: '', company: '', is_active: true, approval_status: 'approved', created_at: '', updated_at: '' },
      isAuthenticated: true,
      isLoading: false,
      error: null,
      accessToken: 'test-token',
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
      loadUser: vi.fn(),
      clearError: vi.fn(),
      updateProfile: vi.fn(),
      refreshTokens: vi.fn(),
    });

    (global as any).WebSocket = vi.fn(() => ({
      send: vi.fn(),
      close: vi.fn(),
      get readyState() { return 1; },
      set onopen(fn) { this._onopen = fn; },
      get onopen() { return this._onopen; },
      set onmessage(fn) { this._onmessage = fn; },
      get onmessage() { return this._onmessage; },
      set onerror(fn) { this._onerror = fn; },
      get onerror() { return this._onerror; },
      set onclose(fn) { this._onclose = fn; },
      get onclose() { return this._onclose; },
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));

    (global as any).SpeechSynthesisUtterance = class {
      onstart: (() => void) | null = null;
      onend: (() => void) | null = null;
      onerror: (() => void) | null = null;
      constructor(public text: string) {}
    };
  });

  afterEach(() => {
    localStorage.clear();
    vi.resetAllMocks();
  });

  const triggerMessage = (data: object) => {
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    if (wsInstance?.onmessage) {
      wsInstance.onmessage({ data: JSON.stringify(data) });
    }
  };

  const triggerError = () => {
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    if (wsInstance?.onerror) {
      wsInstance.onerror();
    }
  };

  it('renders executive avatar heading', async () => {
    renderAvatar();
    expect(screen.getByText('AI Executive Avatar')).toBeDefined();
  });

  it('shows initializing state', async () => {
    renderAvatar();
    expect(screen.getByText('avatar.states.initializing')).toBeDefined();
  });

  it('renders text input', async () => {
    renderAvatar();
    expect(screen.getByPlaceholderText('avatar.sections.start_conversation')).toBeDefined();
  });

  it('shows conversation header', async () => {
    renderAvatar();
    expect(screen.getByText('avatar.sections.conversation')).toBeDefined();
    expect(screen.getByText('avatar.sections.text_first')).toBeDefined();
  });

  it('shows conversation section', async () => {
    renderAvatar();
    expect(screen.getByText('avatar.sections.conversation')).toBeDefined();
    expect(screen.getByText('avatar.sections.text_first')).toBeDefined();
  });

  it('shows input placeholder', async () => {
    renderAvatar();
    expect(screen.getByPlaceholderText('avatar.sections.start_conversation')).toBeDefined();
  });

  it('maps websocket open to ready state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    expect(screen.getByText('avatar.states.ready')).toBeDefined();
  });

  it('maps avatar_state ready event to ready state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'ready' }) });
    });
    expect(screen.getByText('avatar.states.ready')).toBeDefined();
  });

  it('maps avatar_state thinking event to thinking state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    expect(screen.getByText('avatar.states.thinking')).toBeDefined();
  });

  it('maps response event to responding state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: '{"ok": true}' }) });
    });
    expect(screen.getByText('avatar.states.responding')).toBeDefined();
  });

  it('maps avatar_state error event to error state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'error' }) });
    });
    expect(screen.getByText('avatar.states.error')).toBeDefined();
  });

  it('maps websocket error to error state', async () => {
    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onerror?.();
    });
    expect(screen.getByText('avatar.states.error')).toBeDefined();
  });

  it('shows state description', async () => {
    renderAvatar();
    expect(screen.getByText('avatar.states.initializing_desc')).toBeDefined();
  });

  it('has transition classes on avatar circle', async () => {
    renderAvatar();
    const avatarCircle = document.querySelector('.rounded-full.text-white');
    expect(avatarCircle?.classList.contains('transition-all')).toBe(true);
    expect(avatarCircle?.classList.contains('duration-500')).toBe(true);
  });

  it('has transition classes on status pill', async () => {
    renderAvatar();
    const statusPill = document.querySelector('.inline-flex.items-center.gap-2');
    expect(statusPill?.classList.contains('transition-all')).toBe(true);
    expect(statusPill?.classList.contains('duration-500')).toBe(true);
  });

  it('enters speaking state when speech synthesis starts after response', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'Hello' }) });
    });
    await act(async () => {
      utteranceHandlers.onstart?.();
    });
    expect(screen.getByText('avatar.states.speaking')).toBeDefined();
  });

  it('returns to ready when speech synthesis ends after response', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'Hello' }) });
    });
    await act(async () => {
      utteranceHandlers.onstart?.();
    });
    await act(async () => {
      utteranceHandlers.onend?.();
    });
    expect(screen.getByText('avatar.states.ready')).toBeDefined();
  });

  it('returns to ready when speech synthesis errors after response', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'Hello' }) });
    });
    await act(async () => {
      utteranceHandlers.onerror?.();
    });
    expect(screen.getByText('avatar.states.ready')).toBeDefined();
  });

  it('does not enter speaking state when speech synthesis is unavailable', async () => {
    (global as any).window.speechSynthesis = undefined;

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'Hello' }) });
    });
    expect(screen.getByText('avatar.states.responding')).toBeDefined();
    expect(screen.queryByText('avatar.states.speaking')).toBeNull();
  });

  it('extracts outcome text from structured DEM response for speaking', async () => {
    const utteranceHandlers: any = {};
    let capturedText: string | undefined;
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
      capturedText = utterance.text;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: JSON.stringify({ content: { outcome: 'تم إتمام العملية بنجاح' } }) }) });
    });
    expect(capturedText).toBe('تم إتمام العملية بنجاح');
  });

  it('uses fallback spoken text when DEM response has no readable text', async () => {
    const utteranceHandlers: any = {};
    let capturedText: string | undefined;
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
      capturedText = utterance.text;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: JSON.stringify({ content: {} }) }) });
    });
    expect(capturedText).toBe('avatar.sections.fallback_spoken');
  });

  it('does not pass raw JSON when response contains only plain text', async () => {
    const utteranceHandlers: any = {};
    let capturedText: string | undefined;
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
      capturedText = utterance.text;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'تم إتمام المهمة بنجاح' }) });
    });
    expect(capturedText).toBe('تم إتمام المهمة بنجاح');
    expect(capturedText).not.toBe(JSON.stringify({ content: {} }));
  });

  it('uses business_answer.executive_summary first for speaking', async () => {
    const utteranceHandlers: any = {};
    let capturedText: string | undefined;
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
      capturedText = utterance.text;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: JSON.stringify({
        content: {
          outcome: 'Legacy Outcome',
          business_answer: {
            executive_summary: 'BI Executive Summary for Speech',
          },
        },
      }) }) });
    });
    expect(capturedText).toBe('BI Executive Summary for Speech');
  });

  it('falls back to legacy outcome when business_answer is absent for speaking', async () => {
    const utteranceHandlers: any = {};
    let capturedText: string | undefined;
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
      capturedText = utterance.text;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: JSON.stringify({
        content: {
          outcome: 'Legacy Outcome Only',
        },
      }) }) });
    });
    expect(capturedText).toBe('Legacy Outcome Only');
  });

  it('keeps structured response visible when speech synthesis errors', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: '{"content": {"outcome": "ok"}}' }) });
    });
    await act(async () => {
      utteranceHandlers.onerror?.();
    });

    expect(screen.getByText('avatar.sections.structured_response')).toBeDefined();
    expect(screen.getByText('avatar.states.ready')).toBeDefined();
  });

  it('still shows error state on real websocket error even when speech synthesis errors', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    renderAvatar();
    const wsInstance = await getWsInstance();
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: '{"content": {"outcome": "ok"}}' }) });
    });
    await act(async () => {
      wsInstance?.onerror?.();
    });

    expect(screen.getByText('avatar.states.error')).toBeDefined();
  });

  it('does not set initializing after intentional cleanup from token change', async () => {
    localStorage.setItem('access_token', 'token-v1');
    localStorage.setItem('avatar_session_id', 'session-1');
    renderAvatar();
    const wsInstance1 = await getWsInstance();
    await act(async () => {
      wsInstance1?.onopen?.();
    });
    expect(screen.getByText('avatar.states.ready')).toBeDefined();

    localStorage.setItem('access_token', 'token-v2');
    await act(async () => {
      wsInstance1?.onclose?.();
    });
    expect(screen.queryByText('avatar.states.initializing')).toBeNull();
  });
});
