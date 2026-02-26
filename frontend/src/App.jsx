import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield, AlertTriangle, Calendar, Sparkles, MoreVertical,
    Clock, Target, Activity, Search, Send, ChevronRight,
    Info, TrendingDown, Brain, Zap, FileText, MessageSquare,
    Users, BarChart3, Briefcase, Bell, RefreshCw
} from 'lucide-react';
import DetailPanel from './components/DetailPanel';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ─── LEFT SIDEBAR NAV ITEMS ─────────────────────────────────
const NAV_ITEMS = [
    { icon: Activity, label: 'Stream', active: true },
    { icon: Users, label: 'Clients' },
    { icon: BarChart3, label: 'Book' },
    { icon: Briefcase, label: 'Cases' },
    { icon: Calendar, label: 'Meetings' },
    { icon: Bell, label: 'Alerts' },
    { icon: FileText, label: 'Drafts' },
    { icon: Target, label: 'Actions' },
];

// ─── MAIN APP ────────────────────────────────────────────────
function App() {
    const [filter, setFilter] = useState('all');
    const [selectedCard, setSelectedCard] = useState(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [streamMessages, setStreamMessages] = useState([]);
    const [streamTabs, setStreamTabs] = useState([]);
    const [liveStrip, setLiveStrip] = useState(null);
    const [heartbeatStatus, setHeartbeatStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [chatInput, setChatInput] = useState('');
    const [urgencyFilter, setUrgencyFilter] = useState('all'); // 'all' | 'high' | 'critical'

    // Fetch intelligence stream (always fetch ALL, filtering is client-side)
    const fetchStream = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/stream?filter=all`);
            const data = await res.json();
            if (data.stream) setStreamMessages(data.stream);
            if (data.tabs) setStreamTabs(data.tabs);
        } catch (err) {
            console.error('Failed to fetch stream:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Fetch live strip data
    const fetchLiveStrip = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/live-strip`);
            const data = await res.json();
            setLiveStrip(data);
        } catch (err) {
            console.error('Failed to fetch live strip:', err);
        }
    }, []);

    // Fetch heartbeat status
    const fetchHeartbeatStatus = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/heartbeat-status`);
            const data = await res.json();
            setHeartbeatStatus(data);
        } catch (err) {
            console.error('Failed to fetch heartbeat status:', err);
        }
    }, []);

    // Initial load + SSE connection
    useEffect(() => {
        // Initial fetch
        fetchStream();
        fetchLiveStrip();
        fetchHeartbeatStatus();

        // Standard polling for strip/heartbeat (lower frequency since SSE handles the main stream)
        const stripInterval = setInterval(fetchLiveStrip, 30000);
        const hbInterval = setInterval(fetchHeartbeatStatus, 60000);

        // SSE for real-time intelligence stream updates
        let eventSource = new EventSource(`${API_BASE}/stream/live`);

        eventSource.onmessage = (event) => {
            if (event.data === 'update') {
                console.log('SSE push received: data updated');
                fetchStream();
                fetchLiveStrip(); // Fetch strip too as risk counts might have changed
            }
        };

        eventSource.onerror = (err) => {
            console.error('SSE connection error, attempting to reconnect...', err);
        };

        return () => {
            clearInterval(stripInterval);
            clearInterval(hbInterval);
            if (eventSource) {
                eventSource.close();
            }
        };
    }, [fetchStream, fetchLiveStrip, fetchHeartbeatStatus]);

    // Re-fetch only on initial load (tab/urgency changes are client-side)
    useEffect(() => {
        fetchStream();
    }, [fetchStream]);

    const handleCardClick = (card) => {
        setSelectedCard(card);
        setIsDrawerOpen(true);
    };

    // Draft action handlers
    const handleDraftApprove = async (draftId) => {
        try {
            await fetch(`${API_BASE}/drafts/${draftId}/approve`, { method: 'POST' });
            fetchStream(); // Refresh
        } catch (err) {
            console.error('Failed to approve draft:', err);
        }
    };

    const handleDraftReject = async (draftId) => {
        try {
            await fetch(`${API_BASE}/drafts/${draftId}/reject`, { method: 'POST' });
            fetchStream();
        } catch (err) {
            console.error('Failed to reject draft:', err);
        }
    };

    // Chat handler
    const handleChat = async () => {
        if (!chatInput.trim()) return;
        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: chatInput, history: [] })
            });
            const data = await res.json();
            // Inject Atlas response into stream
            setStreamMessages(prev => [{
                id: `chat-${Date.now()}`,
                type: 'atlas',
                text: data.response,
                timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
                cards: []
            }, ...prev]);
            setChatInput('');
        } catch (err) {
            console.error('Failed to send chat:', err);
        }
    };

    // ─── CLIENT-SIDE TAB + URGENCY FILTER (no API calls) ─────
    const filteredMessages = useMemo(() => {
        let msgs = streamMessages;

        // Tab filter
        if (filter !== 'all') {
            msgs = msgs.filter(msg => msg.type === filter);
        }

        // Urgency filter
        if (urgencyFilter !== 'all') {
            msgs = msgs.filter(msg => {
                if (msg.type === 'heartbeat') return false;
                if (msg.cards && msg.cards.length > 0) {
                    if (urgencyFilter === 'critical') {
                        return msg.cards.some(c => c.urgency === 'critical');
                    }
                    return msg.cards.some(c => c.urgency === 'high' || c.urgency === 'critical');
                }
                return false;
            });
        }
        return msgs;
    }, [streamMessages, filter, urgencyFilter]);

    return (
        <div className="portal-layout">
            {/* ─── LEFT SIDEBAR ──────────────────────────────── */}
            <aside className="left-sidebar">
                <div className="sidebar-logo">
                    <div style={{
                        width: '32px', height: '32px', borderRadius: '10px',
                        background: 'linear-gradient(135deg, #528bff 0%, #7c3aed 100%)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 2px 12px rgba(82, 139, 255, 0.3)'
                    }}>
                        <Zap size={15} className="text-white" />
                    </div>
                </div>
                <nav className="sidebar-nav">
                    {NAV_ITEMS.map(item => (
                        <button key={item.label} className={`sidebar-nav-item ${item.active ? 'active' : ''}`} title={item.label}>
                            <item.icon size={18} />
                            <span className="sidebar-label">{item.label}</span>
                        </button>
                    ))}
                </nav>
            </aside>

            {/* ─── MAIN CONTENT ──────────────────────────────── */}
            <div className="main-content">
                {/* ─── HEADER ─────────────────────────────────── */}
                <header className="atlas-header">
                    <div className="flex items-center gap-5">
                        <div className="flex items-center gap-2.5">
                            <div className="w-2 h-2 rounded-full bg-[#12b76a] animate-pulse shadow-[0_0_8px_#12b76a]" />
                            <h1 className="text-[13px] font-black text-[#101828] uppercase tracking-[0.25em]">Atlas</h1>
                        </div>
                        <div className="h-4 w-px bg-[#eaecf0]" />
                        <span className="text-[9px] font-bold text-[#667085] uppercase tracking-widest">Monitoring • Live</span>
                    </div>
                    <div className="flex flex-col items-end gap-0.5">
                        <span className="text-[8px] font-bold text-[#98a2b3] uppercase tracking-widest">
                            Last full book review: {heartbeatStatus?.last_run_text || '—'}
                        </span>
                        <span className="text-[8px] font-bold text-[#b2ddff] uppercase tracking-widest">
                            Next scheduled sweep: {heartbeatStatus?.next_run_text || '—'}
                        </span>
                    </div>
                </header>

                {/* ─── LIVE INTELLIGENCE STRIP ─────────────────── */}
                <div className="live-strip">
                    <motion.div
                        animate={{ x: [0, -80, 0] }}
                        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                        className="flex items-center gap-6"
                    >
                        <StripMetric label="FTSE 100" value={liveStrip?.ftse_100 ? `${liveStrip.ftse_100.toLocaleString()}` : '—'} />
                        {Object.entries(liveStrip?.sectors || {}).map(([sector, change]) => (
                            <StripMetric
                                key={sector}
                                label={sector.toUpperCase()}
                                value={`${(change * 100).toFixed(2)}%`}
                                negative={change < 0}
                                positive={change > 0}
                            />
                        ))}
                        <StripMetric label="Clients Impacted" value={liveStrip?.clients_impacted ?? '—'} />
                        <StripMetric label="Open Risks" value={liveStrip?.open_risks ?? '—'} />
                        <StripMetric label="Meetings Today" value={liveStrip?.meetings_today ?? '—'} />
                    </motion.div>
                </div>

                {/* ─── FILTER STRIP ──────────────────────────── */}
                <div className="filter-strip" style={{ height: 'auto', padding: '6px 20px', gap: '6px', flexDirection: 'column' }}>
                    {/* Action Cluster Tabs */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '2px', overflowX: 'auto', width: '100%', justifyContent: 'center' }}>
                        {streamTabs.length > 0 ? streamTabs.map(tab => (
                            <button
                                key={tab.key}
                                onClick={() => setFilter(tab.key)}
                                className={`filter-pill ${filter === tab.key ? 'active' : ''}`}
                            >
                                {tab.label}
                                {tab.count > 0 && (
                                    <span style={{
                                        marginLeft: '4px', fontSize: '8px', fontWeight: 900,
                                        padding: '1px 5px', borderRadius: '4px',
                                        background: filter === tab.key ? 'rgba(255,255,255,0.2)' : '#f2f4f7',
                                        color: filter === tab.key ? 'rgba(255,255,255,0.8)' : '#667085'
                                    }}>
                                        {tab.count}
                                    </span>
                                )}
                                {tab.highCount > 0 && tab.key !== 'all' && (
                                    <span style={{
                                        marginLeft: '2px', width: '5px', height: '5px',
                                        borderRadius: '50%', background: '#d92d20',
                                        display: 'inline-block', flexShrink: 0
                                    }} />
                                )}
                            </button>
                        )) : (
                            <button className="filter-pill active">All</button>
                        )}
                    </div>
                    {/* Urgency Sub-Filters */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'center' }}>
                        <span style={{ fontSize: '8px', fontWeight: 800, color: '#98a2b3', textTransform: 'uppercase', letterSpacing: '0.1em', marginRight: '4px' }}>Urgency:</span>
                        {[{ key: 'all', label: 'All' }, { key: 'high', label: '⚠️ High+' }, { key: 'critical', label: '🔴 Critical' }].map(u => (
                            <button
                                key={u.key}
                                onClick={() => setUrgencyFilter(u.key)}
                                style={{
                                    padding: '2px 8px', fontSize: '8px', fontWeight: 800,
                                    textTransform: 'uppercase', letterSpacing: '0.08em',
                                    borderRadius: '4px', border: '1px solid',
                                    cursor: 'pointer', transition: 'all 0.15s',
                                    background: urgencyFilter === u.key ? '#101828' : 'transparent',
                                    color: urgencyFilter === u.key ? 'white' : '#98a2b3',
                                    borderColor: urgencyFilter === u.key ? '#101828' : '#eaecf0',
                                }}
                            >
                                {u.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* ─── MAIN STREAM ────────────────────────────── */}
                <main className="stream-main">
                    <div className="stream-container">
                        {loading ? (
                            <div className="flex justify-center py-20">
                                <RefreshCw size={20} className="text-[#d0d5dd] animate-spin" />
                            </div>
                        ) : filteredMessages.length === 0 ? (
                            <div className="flex flex-col items-center py-20 gap-3">
                                <Activity size={24} className="text-[#d0d5dd]" />
                                <p className="text-[12px] font-bold text-[#98a2b3] uppercase tracking-wider">No intelligence yet</p>
                                <p className="text-[11px] text-[#d0d5dd]">Switch tabs or wait for heartbeat sweep…</p>
                            </div>
                        ) : (
                            filteredMessages.map((msg) => (
                                <React.Fragment key={msg.id}>
                                    {msg.type === 'heartbeat' ? (
                                        <HeartbeatMessage msg={msg} />
                                    ) : (
                                        <AtlasMessage
                                            msg={msg}
                                            onCardClick={handleCardClick}
                                            onApprove={handleDraftApprove}
                                            onReject={handleDraftReject}
                                        />
                                    )}
                                </React.Fragment>
                            ))
                        )}
                    </div>
                </main>

                {/* ─── INPUT BAR ──────────────────────────────── */}
                <div className="input-bar">
                    <div className="input-bar-inner">
                        <Search size={14} className="text-[#98a2b3]" />
                        <input
                            type="text"
                            placeholder="Ask Atlas about this book…"
                            className="input-field"
                            value={chatInput}
                            onChange={e => setChatInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleChat()}
                        />
                        <button className="send-btn" onClick={handleChat}>
                            <Send size={14} />
                        </button>
                    </div>
                </div>
            </div>

            {/* ─── DRAWER ─────────────────────────────────── */}
            <AnimatePresence mode="wait">
                {isDrawerOpen && (
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 28, stiffness: 260 }}
                        className="sidebar-right"
                    >
                        <DetailPanel context={selectedCard} onClose={() => setIsDrawerOpen(false)} />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// ─── COMPONENTS ──────────────────────────────────────────────                // ─── COMPONENTS ──────────────────────────────────────────────

const StripMetric = ({ label, value, negative, positive }) => (
    <div className="flex items-center gap-1.5 whitespace-nowrap">
        <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-wider">{label}:</span>
        <span className={`text-[9px] font-black uppercase tracking-wider ${negative ? 'text-[#d92d20]' : positive ? 'text-[#12b76a]' : 'text-[#101828]'}`}>{value}</span>
    </div>
);

const HeartbeatMessage = ({ msg }) => (
    <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="heartbeat-msg"
    >
        <Activity size={10} className="text-[#12b76a]" />
        <span>{msg.text}</span>
        <span className="text-[#d0d5dd]">•</span>
        <span className="text-[#b2ddff]">{msg.timestamp}</span>
    </motion.div>
);

const AtlasMessage = ({ msg, onCardClick, onApprove, onReject }) => (
    <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="atlas-message"
    >
        <span className="msg-timestamp">{msg.timestamp}</span>

        <div className="atlas-bubble">
            <div className="bubble-avatar">
                <Zap size={12} />
            </div>
            <div className="bubble-content">
                <p className="atlas-text">{msg.text}</p>

                {msg.summary && (
                    <div className="inline-summary">
                        {msg.summary.map((s, i) => (
                            <div key={i} className="summary-bullet">
                                <div className="w-1 h-1 rounded-full bg-[#d92d20] mt-1.5 shrink-0" />
                                <span>{s}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>

        {msg.cards && msg.cards.length > 0 && (
            <div className="cards-stack">
                {msg.cards.map(card => (
                    <MiniCard
                        key={card.id}
                        card={card}
                        onClick={() => onCardClick(card)}
                        onApprove={onApprove}
                        onReject={onReject}
                    />
                ))}
            </div>
        )}

        <div className="msg-meta">
            <Shield size={9} className="text-[#12b76a]" />
            <span>Deterministic • Validated</span>
        </div>
    </motion.div>
);

const MiniCard = ({ card, onClick, onApprove, onReject }) => {
    const tintMap = {
        market_risk: 'mini-card-blue',
        behavioural_risk: 'mini-card-amber',
        market_interrupt: 'mini-card-amber',
        meeting_brief: 'mini-card-purple',
        draft: 'mini-card-green',
        tax_window: 'mini-card-green',
        tax_opportunity: 'mini-card-green',
        compliance_exposure: 'mini-card-blue',
    };
    const iconMap = {
        market_risk: Shield,
        behavioural_risk: Brain,
        market_interrupt: TrendingDown,
        meeting_brief: Calendar,
        draft: FileText,
        tax_window: Clock,
        tax_opportunity: Clock,
        compliance_exposure: AlertTriangle,
    };
    const tint = tintMap[card.type] || 'mini-card-blue';
    const Icon = iconMap[card.type] || Info;

    return (
        <div className={`mini-card-capsule ${tint}`} onClick={onClick}>
            <div className="mini-card-accent" />
            <div className="card-icon-box">
                <Icon size={14} />
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-[11px] font-black text-[#101828] uppercase tracking-wider truncate">{card.client || card.asset}</span>
                </div>
                {card.impact && (
                    <div className="text-[12px] font-medium text-[#344054] leading-relaxed mt-0.5 mb-2">
                        {card.impact}
                    </div>
                )}
                {card.memory && (
                    <div className="text-[10px] font-medium text-[#667085] italic mb-1">{card.memory}</div>
                )}
                {card.chips && (
                    <div className="flex flex-wrap gap-1.5 mt-1">
                        {card.chips.map((chip, i) => (
                            <span key={i} className="intel-chip">{chip}</span>
                        ))}
                    </div>
                )}
            </div>
            <div className="flex flex-col items-end gap-2">
                {card.isDraft ? (
                    <span className="text-[9px] font-black text-[#12b76a] uppercase tracking-wider">Ready</span>
                ) : (
                    <ChevronRight size={14} className="text-[#d0d5dd]" />
                )}
            </div>

            {(card.isDraft || card.actions) && (
                <div className="card-actions" onClick={e => e.stopPropagation()}>
                    {card.isDraft ? (
                        <>
                            <button className="action-btn action-primary" onClick={() => onApprove?.(card.id)}>Approve & Send</button>
                            <button className="action-btn action-secondary" onClick={onClick}>Edit</button>
                            <button className="action-btn action-ghost" onClick={() => onReject?.(card.id)}>Dismiss</button>
                        </>
                    ) : card.actions?.map((a, i) => (
                        <button key={i} className="action-btn action-secondary">{a}</button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default App;
