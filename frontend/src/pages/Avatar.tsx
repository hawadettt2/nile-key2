import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { connectToDEM, getDEMSessions } from '@/services/api';

type AvatarState = 'initializing' | 'ready' | 'thinking' | 'responding' | 'speaking' | 'error';

const STATE_CONFIG: Record<AvatarState, { label: string; color: string; pulse: boolean; ring: string; description: string; shadow: string }> = {
  initializing: { label: 'Initializing', color: 'bg-slate-500', pulse: true, ring: 'ring-slate-200', description: 'Preparing your executive session...', shadow: 'shadow-slate-200/50' },
  ready: { label: 'Ready', color: 'bg-emerald-600', pulse: false, ring: 'ring-emerald-100', description: 'Ready to assist you with export and trade decisions.', shadow: 'shadow-emerald-500/20' },
  thinking: { label: 'Thinking', color: 'bg-amber-500', pulse: true, ring: 'ring-amber-100', description: 'Analyzing your request...', shadow: 'shadow-amber-500/20' },
  responding: { label: 'Responding', color: 'bg-blue-600', pulse: false, ring: 'ring-blue-100', description: 'Preparing a structured response.', shadow: 'shadow-blue-500/20' },
  speaking: { label: 'Speaking', color: 'bg-indigo-600', pulse: true, ring: 'ring-indigo-100', description: 'Presenting the response...', shadow: 'shadow-indigo-500/20' },
  error: { label: 'Error', color: 'bg-red-500', pulse: false, ring: 'ring-red-100', description: 'Something went wrong. Please try again.', shadow: 'shadow-red-500/20' },
};

const EXECUTIVE_AVATAR_STYLES = (
  <style>{`
    @keyframes breathe {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.02); }
    }
    .animate-breathe {
      animation: breathe 3s ease-in-out infinite;
    }
    @keyframes speak {
      0%, 100% { transform: scaleY(1); }
      50% { transform: scaleY(0.6); }
    }
    .animate-speak {
      animation: speak 0.22s ease-in-out infinite;
      transform-origin: center;
      transform-box: fill-box;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .animate-fade-in {
      animation: fadeIn 0.35s ease-out forwards;
    }
  `}</style>
);

const ExecutiveAvatarVisual = ({ state }: { state: AvatarState }) => {
  const isError = state === 'error';
  const isThinking = state === 'thinking';
  const isInitializing = state === 'initializing';
  const isSpeaking = state === 'speaking';
  const isReady = state === 'ready';
  const isResponding = state === 'responding';
  const isActive = isThinking || isInitializing || isSpeaking;

  const eyeY = isThinking || isInitializing ? 52 : 56;
  const eyeRx = 5.2;
  const eyeRy = isThinking || isInitializing ? 2.8 : 5.8;

  return (
    <svg viewBox="0 0 120 120" className="w-20 h-20 sm:w-24 sm:h-24" role="img" aria-label="Executive avatar">
      <defs>
        <radialGradient id="faceGradient" cx="50%" cy="40%" r="55%" fx="50%" fy="38%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="85%" stopColor="#f8fafc" />
          <stop offset="100%" stopColor="#e2e8f0" />
        </radialGradient>
        <linearGradient id="hairGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1e293b" />
          <stop offset="100%" stopColor="#0f172a" />
        </linearGradient>
        <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#000000" floodOpacity="0.08" />
        </filter>
      </defs>

      <circle cx="60" cy="62" r="36" fill="url(#faceGradient)" filter="url(#softShadow)" />

      <path
        d="M22 56 Q22 18 60 18 Q98 18 98 56 Q98 42 88 32 Q60 12 32 32 Q22 42 22 56"
        fill="url(#hairGradient)"
      />
      <path
        d="M22 56 Q22 42 32 32 Q60 12 88 32 Q98 42 98 56"
        fill="none"
        stroke="url(#hairGradient)"
        strokeWidth="1.5"
        opacity="0.4"
      />

      {isError ? (
        <>
          <line x1="36" y1="50" x2="52" y2="64" stroke="#ef4444" strokeWidth="2.8" strokeLinecap="round" />
          <line x1="52" y1="50" x2="36" y2="64" stroke="#ef4444" strokeWidth="2.8" strokeLinecap="round" />
          <line x1="68" y1="50" x2="84" y2="64" stroke="#ef4444" strokeWidth="2.8" strokeLinecap="round" />
          <line x1="84" y1="50" x2="68" y2="64" stroke="#ef4444" strokeWidth="2.8" strokeLinecap="round" />
        </>
      ) : isThinking || isInitializing ? (
        <>
          <line x1="36" y1={eyeY} x2="52" y2={eyeY} stroke="#1e293b" strokeWidth="2.8" strokeLinecap="round" />
          <line x1="68" y1={eyeY} x2="84" y2={eyeY} stroke="#1e293b" strokeWidth="2.8" strokeLinecap="round" />
        </>
      ) : (
        <>
          <ellipse cx="44" cy={eyeY} rx={eyeRx} ry={eyeRy} fill="#1e293b" />
          <ellipse cx="76" cy={eyeY} rx={eyeRx} ry={eyeRy} fill="#1e293b" />
          <circle cx="46" cy={eyeY - 1.2} r="1.4" fill="#ffffff" opacity="0.9" />
          <circle cx="78" cy={eyeY - 1.2} r="1.4" fill="#ffffff" opacity="0.9" />
        </>
      )}

      {!isError && !isThinking && !isInitializing && (
        <path d="M40 68 Q44 66 48 68" stroke="#94a3b8" strokeWidth="1.6" fill="none" strokeLinecap="round" opacity="0.7" />
      )}

      {isSpeaking ? (
        <ellipse cx="60" cy="80" rx="5.5" ry="3.2" fill="#1e293b" className="animate-speak" opacity="0.9" />
      ) : isReady || isResponding ? (
        <path d="M48 78 Q60 84 72 78" stroke="#1e293b" strokeWidth="2.4" fill="none" strokeLinecap="round" opacity="0.85" />
      ) : isError ? (
        <path d="M48 84 Q60 78 72 84" stroke="#ef4444" strokeWidth="2.4" fill="none" strokeLinecap="round" opacity="0.85" />
      ) : isThinking || isInitializing ? (
        <line x1="50" y1="80" x2="70" y2="80" stroke="#1e293b" strokeWidth="2.4" strokeLinecap="round" opacity="0.7" />
      ) : null}
    </svg>
  );
};

export function Avatar() {
  const user = useAuthStore((s) => s.user);
  const [status, setStatus] = useState<AvatarState>('initializing');
  const [transcript, setTranscript] = useState<string[]>([]);
  const [response, setResponse] = useState<string>('');
  const [lastSentText, setLastSentText] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const accessToken =
    typeof window !== 'undefined'
      ? localStorage.getItem('access_token')
      : null;

  useEffect(() => {
    const initSession = async () => {
      if (!user) return;
      try {
        const storedSessionId = typeof window !== 'undefined' ? localStorage.getItem('avatar_session_id') : null;
        if (storedSessionId) {
          setSessionId(storedSessionId);
          return;
        }
        const sessionsRes = await getDEMSessions();
        if (sessionsRes.data && sessionsRes.data.length > 0) {
          const sessionId = sessionsRes.data[0].session_id;
          localStorage.setItem('avatar_session_id', sessionId);
          setSessionId(sessionId);
          return;
        }
        const connectRes = await connectToDEM({ user_id: user.id });
        const sessionId = connectRes.data?.session_id;
        if (sessionId) {
          localStorage.setItem('avatar_session_id', sessionId);
          setSessionId(sessionId);
        }
      } catch (err) {
        console.error('Failed to init DEM session:', err);
        setStatus('error');
      }
    };

    initSession();
  }, [user]);

  useEffect(() => {
    if (!accessToken || !sessionId) return;

    const ws = new WebSocket(`ws://${window.location.hostname}:8020/ws/avatar`);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'auth',
        session_id: sessionId,
        token: accessToken,
      }));
      setStatus('ready');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'avatar_state') {
        setStatus(data.state);
      } else if (data.type === 'status') {
        if (data.text.toLowerCase().includes('ready') || data.text.toLowerCase().includes('connected') || data.text.toLowerCase().includes('authenticated')) {
          setStatus('ready');
        } else if (data.text.toLowerCase().includes('error')) {
          setStatus('error');
        }
      } else if (data.type === 'transcript') {
        setTranscript((prev) => [...prev, data.text]);
      } else if (data.type === 'response') {
        setResponse(data.text);
        setStatus('responding');
        speakText(data.text);
      } else if (data.type === 'error') {
        setStatus('error');
      }
    };

    ws.onerror = () => setStatus('error');
    ws.onclose = () => setStatus('ready');

    return () => ws.close();
  }, [accessToken, sessionId]);

  const sendText = (text: string) => {
    if (!text.trim() || wsRef.current?.readyState !== WebSocket.OPEN) return;
    setLastSentText(text.trim());
    wsRef.current.send(JSON.stringify({ type: 'text', text }));
  };

  const extractSpokenText = (raw: string): string => {
    try {
      const parsed = JSON.parse(raw);
      const outcome = parsed?.content?.outcome;
      if (outcome && typeof outcome === 'string' && outcome.trim().length > 0) {
        return outcome.trim();
      }
      if (parsed?.content?.result?.summary && typeof parsed.content.result.summary === 'string') {
        return parsed.content.result.summary.trim();
      }
      if (typeof parsed?.content?.message === 'string' && parsed.content.message.trim().length > 0) {
        return parsed.content.message.trim();
      }
      if (typeof parsed?.message === 'string' && parsed.message.trim().length > 0) {
        return parsed.message.trim();
      }
    } catch {
      // fallback below
    }
    if (typeof raw === 'string' && raw.trim().length > 0 && !raw.trim().startsWith('{')) {
      return raw.trim();
    }
    return 'I have received your request. Please check the structured response below.';
  };

  const speakText = (rawResponse: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    const text = extractSpokenText(rawResponse);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => setStatus('speaking');
    utterance.onend = () => setStatus('ready');
    utterance.onerror = () => setStatus('error');
    window.speechSynthesis.speak(utterance);
  };

  const currentState = STATE_CONFIG[status];

  return (
    <>
      {EXECUTIVE_AVATAR_STYLES}
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
        <div className="max-w-3xl mx-auto px-4 py-8 sm:py-12">
          <div className="flex flex-col items-center text-center mb-10">
            <div className="relative mb-6">
              <div className={`absolute -inset-4 rounded-full ${currentState.color} opacity-0 transition-all duration-700 ${currentState.pulse ? 'opacity-25 scale-110' : 'opacity-0 scale-100'}`} />
              <div className={`relative w-28 h-28 sm:w-32 sm:h-32 rounded-full flex items-center justify-center text-white shadow-xl transition-all duration-500 ${currentState.color} ${currentState.shadow} ${currentState.pulse ? 'animate-breathe' : ''}`}>
                <ExecutiveAvatarVisual state={status} />
              </div>
              <div className="absolute -bottom-1.5 -right-1.5 w-7 h-7 sm:w-8 sm:h-8 bg-white rounded-full border-2 border-slate-200 flex items-center justify-center transition-all duration-500 shadow-sm">
                <div className={`w-3.5 h-3.5 sm:w-4 sm:h-4 rounded-full transition-colors duration-500 ${currentState.color}`} />
              </div>
            </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3 tracking-tight">AI Executive Avatar</h1>
          <div className={`inline-flex items-center gap-2 px-5 py-2 bg-white border border-slate-200 rounded-full shadow-sm transition-all duration-500 ${currentState.pulse ? 'shadow-md' : ''}`}>
            <span className={`relative flex h-2.5 w-2.5`}>
              {currentState.pulse && <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${currentState.color} opacity-75`}></span>}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${currentState.color}`}></span>
            </span>
            <span className="text-sm font-semibold text-slate-700">{currentState.label}</span>
          </div>
          <p className="mt-4 text-sm text-slate-500 font-medium transition-all duration-500 max-w-md">{currentState.description}</p>
          {sessionId && (
            <p className="mt-2 text-[10px] text-slate-400 font-mono tracking-wide">Session: {sessionId}</p>
          )}
        </div>

        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden mb-4 transition-all duration-500 hover:shadow-md">
          <div className="px-6 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-widest">Conversation</span>
            <span className="text-xs text-slate-400 font-medium">Text-first</span>
          </div>
          <div className="p-6 min-h-[160px] max-h-[360px] overflow-y-auto">
            {transcript.length === 0 && !lastSentText && (
              <p className="text-sm text-slate-400 italic">Start the conversation by typing a request below.</p>
            )}
            <div className="space-y-3">
              {lastSentText && (
                <div className="text-sm text-slate-700 bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 transition-all duration-500 shadow-sm">
                  {lastSentText}
                </div>
              )}
              {transcript.map((t, i) => (
                <div key={i} className="text-sm text-slate-700 bg-slate-50 border border-slate-100 rounded-xl px-4 py-3 transition-all duration-500 shadow-sm">
                  {t}
                </div>
              ))}
            </div>
          </div>
        </div>

        {response && (
          <div className="mb-6 bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden transition-all duration-500 hover:shadow-md">
            <div className="px-6 py-3.5 border-b border-slate-100 bg-slate-50/50">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-widest">Structured Business Response</span>
            </div>
            <div className="p-6">
              <pre className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed font-mono bg-slate-50 border border-slate-100 rounded-xl p-4 max-h-[240px] overflow-y-auto transition-all duration-500 shadow-sm">
                {response}
              </pre>
            </div>
          </div>
        )}

        <div className="bg-white/80 backdrop-blur-sm border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden transition-all duration-500 hover:shadow-md">
          <div className="p-5">
            <input
              type="text"
              placeholder="Type your request..."
              className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-300"
              onKeyDown={(e) => {
                if (e.key === 'Enter') sendText(e.currentTarget.value);
              }}
            />
            <p className="mt-2.5 text-xs text-slate-400 text-center font-medium">Press Enter to send</p>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
