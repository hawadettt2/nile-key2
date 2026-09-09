import { render, screen, act, fireEvent } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Avatar } from '@/pages/Avatar';
import { useAuthStore } from '@/store/authStore';
import { vi } from 'vitest';

vi.mock('@/store/authStore');
vi.mock('@/services/api', () => ({
  connectToDEM: vi.fn(() => ({ data: { session_id: 'test-session-id' } })),
  getDEMSessions: vi.fn(() => ({ data: [] })),
}));

const mockedUseAuthStore = vi.mocked(useAuthStore);

describe('Avatar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('avatar_session_id', 'test-session-id');
    mockedUseAuthStore.mockReturnValue({
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
    } as any);

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
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByText('AI Executive Avatar')).toBeDefined();
  });

  it('shows initializing state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByText('Initializing')).toBeDefined();
  });

  it('renders text input', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByPlaceholderText('Type your request...')).toBeDefined();
  });

  it('shows conversation header', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByText('Conversation')).toBeDefined();
    expect(screen.getByText('Text-first')).toBeDefined();
  });

  it('shows conversation section', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByText('Conversation')).toBeDefined();
    expect(screen.getByText('Text-first')).toBeDefined();
  });

  it('shows input placeholder', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByPlaceholderText('Type your request...')).toBeDefined();
  });

  it('maps websocket open to ready state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    expect(screen.getByText('Ready')).toBeDefined();
  });

  it('maps avatar_state ready event to ready state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'ready' }) });
    });
    expect(screen.getByText('Ready')).toBeDefined();
  });

  it('maps avatar_state thinking event to thinking state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    expect(screen.getByText('Thinking')).toBeDefined();
  });

  it('maps response event to responding state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: '{"ok": true}' }) });
    });
    expect(screen.getByText('Responding')).toBeDefined();
  });

  it('maps avatar_state error event to error state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'error' }) });
    });
    expect(screen.getByText('Error')).toBeDefined();
  });

  it('maps websocket error to error state', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onerror?.();
    });
    expect(screen.getByText('Error')).toBeDefined();
  });

  it('shows state description', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    expect(screen.getByText('Preparing your executive session...')).toBeDefined();
  });

  it('has transition classes on avatar circle', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const avatarCircle = document.querySelector('.rounded-full.text-white');
    expect(avatarCircle?.classList.contains('transition-all')).toBe(true);
    expect(avatarCircle?.classList.contains('duration-500')).toBe(true);
  });

  it('has transition classes on status pill', async () => {
    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
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

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
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
    expect(screen.getByText('Speaking')).toBeDefined();
  });

  it('returns to ready when speech synthesis ends after response', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
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
    expect(screen.getByText('Ready')).toBeDefined();
  });

  it('enters error state when speech synthesis errors after response', async () => {
    const utteranceHandlers: any = {};
    const mockSpeak = (utterance: any) => {
      utteranceHandlers.onstart = utterance.onstart;
      utteranceHandlers.onend = utterance.onend;
      utteranceHandlers.onerror = utterance.onerror;
    };
    (global as any).window.speechSynthesis = { speak: mockSpeak };

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
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
    expect(screen.getByText('Error')).toBeDefined();
  });

  it('does not enter speaking state when speech synthesis is unavailable', async () => {
    (global as any).window.speechSynthesis = undefined;

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'avatar_state', state: 'thinking' }) });
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'Hello' }) });
    });
    expect(screen.getByText('Responding')).toBeDefined();
    expect(screen.queryByText('Speaking')).toBeNull();
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

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
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

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: JSON.stringify({ content: {} }) }) });
    });
    expect(capturedText).toBe('I have received your request. Please check the structured response below.');
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

    render(
      <BrowserRouter>
        <Avatar />
      </BrowserRouter>
    );
    const wsInstance = (global as any).WebSocket.mock.results?.[0]?.value;
    await act(async () => {
      wsInstance?.onopen?.();
    });
    await act(async () => {
      wsInstance?.onmessage?.({ data: JSON.stringify({ type: 'response', text: 'تم إتمام المهمة بنجاح' }) });
    });
    expect(capturedText).toBe('تم إتمام المهمة بنجاح');
    expect(capturedText).not.toBe(JSON.stringify({ content: {} }));
  });
});
