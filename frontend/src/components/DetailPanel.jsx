import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Shield, Activity, Zap, CheckCircle, Send, Target, BarChart3, Clock, Brain, TrendingDown, Globe, Users, ChevronDown, ChevronRight, FileText, Mail } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ExpandableThought = ({ thoughts }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    if (!thoughts || thoughts.length === 0) return null;

    return (
        <div className="thought-container">
            <div className="thought-header" onClick={() => setIsExpanded(!isExpanded)}>
                <div className="thought-label">
                    {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    Thought
                </div>
            </div>
            {isExpanded && (
                <div className="thought-content">
                    {thoughts.map((thought, idx) => (
                        <div key={idx} className="thought-item">
                            <div className={`thought-dot ${idx === thoughts.length - 1 ? 'active' : ''}`} />
                            <span>{thought}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const DetailPanel = ({ context, onClose, onResolve, onPrepareAction, onSendChat, onApproveDraft }) => {
    const [activeTab, setActiveTab] = useState('Intelligence');
    const [localChatInput, setLocalChatInput] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [draftSent, setDraftSent] = useState(false);
    const chatEndRef = useRef(null);
    const hasInitializedRef = useRef(false);

    if (!context) return null;

    const d = context.drawerData || {};
    const isDraft = d.isDraft || context.type === 'draft';
    const isMarketInterrupt = d.isMarketInterrupt || context.type === 'market_interrupt';
    const riskId = context.original_id || context.id;

    // Auto-populate Discussion with proactive Atlas message when drawer opens
    useEffect(() => {
        if (hasInitializedRef.current) return;
        hasInitializedRef.current = true;

        const proactive = d.proactive_thought;
        const headline = d.headline;
        const consequence = d.consequence;
        const clientName = context.client || 'this client';

        if (proactive || headline) {
            let fullMessage = '';
            if (headline) fullMessage += `**${headline}**\n\n`;
            if (proactive) fullMessage += proactive + '\n\n';
            if (consequence) fullMessage += `> ⚠️ **If ignored:** ${consequence}\n\n`;
            fullMessage += `---\n\nI can draft a proactive communication to **${clientName}** right now. Just click **"Take Action"** below, or ask me anything about this risk.`;

            setChatHistory([{
                id: `proactive-${Date.now()}`,
                role: 'assistant',
                content: fullMessage,
                thoughts: [],
                isStreaming: false,
                isProactive: true
            }]);
        }
    }, []);

    // Auto-scroll to bottom of chat
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatHistory]);

    const handleInternalChat = async () => {
        if (!localChatInput.trim()) return;
        const msg = localChatInput;
        setLocalChatInput('');
        setChatHistory(prev => [...prev, { role: 'user', content: msg }]);

        const chatContext = {
            client_id: context.client_id,
            client_pname: context.client,
            risk_event_id: riskId,
            case_type: context.type
        };

        const assistantMsgId = `assistant-${Date.now()}`;
        setChatHistory(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '', thoughts: [], isStreaming: true }]);

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, history: chatHistory, context: chatContext })
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                const chunk = decoder.decode(value || new Uint8Array());
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        setChatHistory(prev => prev.map(c => {
                            if (c.id === assistantMsgId) {
                                if (data.type === 'thought') {
                                    return { ...c, thoughts: [...(c.thoughts || []), data.content] };
                                } else if (data.type === 'answer') {
                                    return { ...c, content: c.content + data.content };
                                }
                            }
                            return c;
                        }));
                    } catch (e) { console.error('JSON parse error:', e); }
                }
            }
            setChatHistory(prev => prev.map(c => c.id === assistantMsgId ? { ...c, isStreaming: false } : c));
        } catch (err) {
            console.error('Failed to send chat:', err);
        }
    };

    // Take Action: Generate a draft communication in the Discussion tab
    const handleTakeAction = async () => {
        setActiveTab('Discussion');
        const clientName = context.client || 'the client';
        const headline = d.headline || d.title || 'the identified risk';

        // Add a user-like system message
        setChatHistory(prev => [...prev, {
            role: 'user',
            content: `Draft a proactive client communication for ${clientName} regarding ${headline}.`
        }]);

        const assistantMsgId = `draft-${Date.now()}`;
        setChatHistory(prev => [...prev, {
            id: assistantMsgId,
            role: 'assistant',
            content: '',
            thoughts: [],
            isStreaming: true,
            isDraft: true
        }]);

        const chatContext = {
            client_id: context.client_id,
            client_pname: context.client,
            risk_event_id: riskId,
            case_type: context.type,
            action: 'generate_draft'
        };

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Generate a professional client communication draft for ${clientName} about this risk: ${headline}. ${d.proactive_thought || ''}. Include a subject line and body. Format it clearly with **Subject:** and **Body:** sections.`,
                    history: chatHistory,
                    context: chatContext
                })
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                const chunk = decoder.decode(value || new Uint8Array());
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        setChatHistory(prev => prev.map(c => {
                            if (c.id === assistantMsgId) {
                                if (data.type === 'thought') {
                                    return { ...c, thoughts: [...(c.thoughts || []), data.content] };
                                } else if (data.type === 'answer') {
                                    return { ...c, content: c.content + data.content };
                                }
                            }
                            return c;
                        }));
                    } catch (e) { console.error('JSON parse error:', e); }
                }
            }
            setChatHistory(prev => prev.map(c => c.id === assistantMsgId ? { ...c, isStreaming: false } : c));
        } catch (err) {
            console.error('Failed to generate draft:', err);
        }
    };

    const handleSendToClient = () => {
        setDraftSent(true);
        setChatHistory(prev => [...prev, {
            id: `sent-${Date.now()}`,
            role: 'assistant',
            content: `✅ **Communication sent successfully** to **${context.client || 'client'}**.\n\nThe drafted message has been dispatched via the client's preferred channel. I've also logged this interaction in their behavioural memory for future reference.`,
            thoughts: [],
            isStreaming: false,
            isSentConfirmation: true
        }]);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'white' }}>
            {/* Header */}
            <header style={{ padding: '16px 24px', borderBottom: '1px solid #f2f4f7', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'white', position: 'relative' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '2px', background: 'linear-gradient(to right, #1570ef, #7f56d9, #12b76a)' }} />
                <div>
                    <h3 style={{ fontSize: 10, fontWeight: 900, color: '#101828', textTransform: 'uppercase', letterSpacing: '0.2em', margin: 0 }}>
                        {d.title || 'Intelligence Detail'}
                    </h3>
                    <p style={{ fontSize: 9, color: '#667085', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', marginTop: 4, fontStyle: 'italic' }}>
                        Context // {context.client || context.asset || '—'}
                    </p>
                </div>
                <button onClick={onClose} style={{ padding: 8, background: 'transparent', border: 'none', cursor: 'pointer', borderRadius: 8 }}>
                    <X size={16} color="#667085" />
                </button>
            </header>

            {/* Tabs — Directives removed */}
            <div style={{ padding: '0 24px', borderBottom: '1px solid #f2f4f7', background: '#fcfdfe', display: 'flex', gap: 20 }}>
                {['Intelligence', 'Discussion'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        style={{
                            padding: '12px 0',
                            fontSize: 9,
                            fontWeight: 900,
                            textTransform: 'uppercase',
                            letterSpacing: '0.12em',
                            color: activeTab === tab ? '#101828' : '#667085',
                            border: 'none',
                            background: 'transparent',
                            borderBottom: `2px solid ${activeTab === tab ? '#101828' : 'transparent'}`,
                            cursor: 'pointer'
                        }}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 28 }}>
                {activeTab === 'Discussion' ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {chatHistory.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '40px 0' }}>
                                <Brain size={24} color="#d0d5dd" style={{ margin: '0 auto 12px' }} />
                                <p style={{ fontSize: 11, color: '#98a2b3', fontWeight: 600, textTransform: 'uppercase' }}>Reasoning Console</p>
                                <p style={{ fontSize: 10, color: '#d0d5dd' }}>Discuss this risk with Atlas to explore deeper implications.</p>
                            </div>
                        ) : (
                            chatHistory.map((chat, i) => (
                                <div key={i}>
                                    <div style={{
                                        padding: 12,
                                        borderRadius: 10,
                                        background: chat.isSentConfirmation ? '#ecfdf3' : chat.role === 'user' ? '#f9fafb' : '#f0f9ff',
                                        border: '1px solid',
                                        borderColor: chat.isSentConfirmation ? '#abefc6' : chat.role === 'user' ? '#f2f4f7' : '#e0f2fe'
                                    }}>
                                        <p style={{
                                            fontSize: 8, fontWeight: 900,
                                            color: chat.isSentConfirmation ? '#067647' : chat.role === 'user' ? '#667085' : '#026aa2',
                                            textTransform: 'uppercase', marginBottom: 4
                                        }}>
                                            {chat.role === 'user' ? 'Advisor' : 'Atlas'}
                                        </p>

                                        <ExpandableThought thoughts={chat.thoughts} />

                                        <div className="markdown-content" style={{ fontSize: 13, color: '#101828', lineHeight: 1.5, margin: 0 }}>
                                            {chat.role === 'assistant' ? (
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {chat.content + (chat.isStreaming ? ' |' : '')}
                                                </ReactMarkdown>
                                            ) : (
                                                chat.content
                                            )}
                                        </div>
                                    </div>

                                    {/* Send to Client button for draft messages */}
                                    {chat.isDraft && !chat.isStreaming && !draftSent && (
                                        <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                                            <button
                                                onClick={handleSendToClient}
                                                style={{
                                                    flex: 1, padding: '10px 0',
                                                    background: '#12b76a', color: 'white',
                                                    border: 'none', borderRadius: 10,
                                                    fontSize: 9, fontWeight: 900,
                                                    textTransform: 'uppercase', letterSpacing: '0.15em',
                                                    cursor: 'pointer',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6
                                                }}
                                            >
                                                <Mail size={12} /> Send to Client
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setLocalChatInput('Refine this draft — ');
                                                }}
                                                style={{
                                                    flex: 1, padding: '10px 0',
                                                    background: 'white', color: '#344054',
                                                    border: '1px solid #d0d5dd', borderRadius: 10,
                                                    fontSize: 9, fontWeight: 900,
                                                    textTransform: 'uppercase', letterSpacing: '0.15em',
                                                    cursor: 'pointer',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6
                                                }}
                                            >
                                                <FileText size={12} /> Refine Draft
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                        <div ref={chatEndRef} />
                    </div>
                ) : isDraft ? (
                    <DraftContent context={context} drawerData={d} />
                ) : (
                    <>
                        {/* Portfolio Allocation */}
                        {d.portfolio && d.portfolio.length > 0 && (
                            <section>
                                <SectionTitle icon={<BarChart3 size={13} color="#1570ef" />} label="Portfolio Concentration" />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                    {d.portfolio.map((item, i) => (
                                        <AllocationBar key={i} label={item.label} value={item.value} color={item.color} />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Volatility Delta */}
                        {d.volatility && (
                            <section>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 10 }}>
                                    <SectionTitle icon={<Activity size={13} color="#d92d20" />} label="Volatility Delta (7D)" />
                                    <span style={{ fontSize: 10, fontWeight: 900, color: d.volatilityLabel === 'Within Mandate' ? '#12b76a' : '#d92d20' }}>{d.volatility}</span>
                                </div>
                                <div style={{ height: 40, background: '#f8f9fb', borderRadius: 10, border: '1px solid #eaecf0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: 10, fontWeight: 700, color: d.volatilityLabel === 'Within Mandate' ? '#12b76a' : '#d92d20', textTransform: 'uppercase' }}>
                                        {d.volatilityLabel || 'Monitoring'}
                                    </span>
                                </div>
                            </section>
                        )}

                        {/* Behavioural Indicators */}
                        {d.behaviour && (
                            <section>
                                <SectionTitle icon={<Zap size={13} color="#f79009" />} label="Behavioural Indicators" />
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                    <ConfidenceMeter label="Risk Aversion" value={d.behaviour.riskAversion} color="#f79009" />
                                    <ConfidenceMeter label="Drawdown Tolerance" value={d.behaviour.drawdownTolerance} color={d.behaviour.drawdownTolerance < 30 ? '#d92d20' : '#1570ef'} />
                                </div>
                                {d.behaviourNote && (
                                    <p style={{ marginTop: 12, padding: 12, background: '#fffaf0', border: '1px solid #fedf89', borderRadius: 10, fontSize: 11, color: '#b54708', fontWeight: 500, fontStyle: 'italic', lineHeight: 1.6 }}>
                                        {d.behaviourNote}
                                    </p>
                                )}
                            </section>
                        )}

                        {/* Memory Visualization */}
                        {d.memory && d.memory.length > 0 && (
                            <section style={{ paddingTop: 16, borderTop: '1px solid #f2f4f7' }}>
                                <SectionTitle icon={<Brain size={13} color="#7f56d9" />} label="Memory Reference" />
                                <p style={{ fontSize: 10, fontWeight: 700, color: '#98a2b3', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10 }}>
                                    Referenced {d.memory.length} past conversation{d.memory.length > 1 ? 's' : ''}:
                                </p>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {d.memory.map((m, i) => (
                                        <MemoryItem key={i} date={m.date} text={m.text} />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Market Context (for interrupts) */}
                        {isMarketInterrupt && d.marketContext && (
                            <section style={{ paddingTop: 16, borderTop: '1px solid #f2f4f7' }}>
                                <SectionTitle icon={<Globe size={13} color="#1570ef" />} label="Market Context" />
                                <p style={{ fontSize: 11, color: '#475467', fontWeight: 500, lineHeight: 1.7, marginBottom: 8 }}>
                                    {d.marketContext}
                                </p>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 9, fontWeight: 800, color: '#98a2b3', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                                    <Globe size={10} />
                                    Source: Live Web Search
                                </div>
                            </section>
                        )}

                        {/* Exposed Clients (for interrupts) */}
                        {isMarketInterrupt && d.exposedClients && d.exposedClients.length > 0 && (
                            <section style={{ paddingTop: 16, borderTop: '1px solid #f2f4f7' }}>
                                <SectionTitle icon={<Users size={13} color="#f79009" />} label="Exposed Clients" />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                    {d.exposedClients.map((client, i) => (
                                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 12px', background: '#fffaf0', border: '1px solid #fedf89', borderRadius: 8 }}>
                                            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#f79009', flexShrink: 0 }} />
                                            <span style={{ fontSize: 11, fontWeight: 700, color: '#b54708' }}>{client.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* News Headlines (for morning intelligence) */}
                        {d.news && d.news.length > 0 && (
                            <section style={{ paddingTop: 16, borderTop: '1px solid #f2f4f7' }}>
                                <SectionTitle icon={<Globe size={13} color="#1570ef" />} label="Market News" />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                    {d.news.map((item, idx) => (
                                        <div key={idx} style={{ padding: 10, background: '#f8f9fb', borderRadius: 8, border: '1px solid #eaecf0' }}>
                                            <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: '#101828', lineHeight: 1.5 }}>
                                                {item.headline || item}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Intelligence Trace */}
                        {d.trace && d.trace.length > 0 && (
                            <section style={{ paddingTop: 16, borderTop: '1px solid #f2f4f7' }}>
                                <SectionTitle icon={<Shield size={13} color="#12b76a" />} label="Intelligence Trace" />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {d.trace.map((step, idx) => (
                                        <div key={idx} style={{ display: 'flex', gap: 8, fontSize: 10, color: '#475467', fontWeight: 500, alignItems: 'center' }}>
                                            <CheckCircle size={11} color="#12b76a" style={{ flexShrink: 0 }} />
                                            {step}
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
                    </>
                )}
            </div>

            {/* Footer */}
            <footer style={{ padding: '16px 24px', borderTop: '1px solid #f2f4f7', background: 'white', display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ position: 'relative' }}>
                    <input
                        type="text"
                        placeholder="Discuss this context with Atlas..."
                        value={localChatInput}
                        onChange={e => setLocalChatInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleInternalChat()}
                        style={{ width: '100%', height: 40, paddingLeft: 14, paddingRight: 44, background: '#f8f9fb', border: '1px solid #eaecf0', borderRadius: 10, fontSize: 12, fontWeight: 500, outline: 'none', boxSizing: 'border-box' }}
                    />
                    <button
                        onClick={handleInternalChat}
                        style={{ position: 'absolute', right: 6, top: '50%', transform: 'translateY(-50%)', width: 28, height: 28, background: '#101828', color: 'white', border: 'none', borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                        <Send size={12} />
                    </button>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    {isDraft ? (
                        <button
                            onClick={() => onApproveDraft(context.id)}
                            style={{ flex: 1, padding: '10px 0', background: '#12b76a', color: 'white', border: 'none', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
                            Finalize & Send
                        </button>
                    ) : (
                        <>
                            <button
                                onClick={handleTakeAction}
                                style={{ flex: 1, padding: '10px 0', background: '#101828', color: 'white', border: 'none', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
                                Take Action
                            </button>
                            <button
                                onClick={() => onResolve(riskId)}
                                style={{ flex: 1, padding: '10px 0', background: 'white', color: '#344054', border: '1px solid #d0d5dd', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
                                Mark Resolved
                            </button>
                        </>
                    )}
                </div>
            </footer>
        </div>
    );
};

// ─── SUB-COMPONENTS ─────────────────────────────────────────

const SectionTitle = ({ icon, label }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
        {icon}
        <h4 style={{ fontSize: 9, fontWeight: 900, color: '#101828', textTransform: 'uppercase', letterSpacing: '0.15em', margin: 0 }}>{label}</h4>
    </div>
);

const MemoryItem = ({ date, text }) => (
    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: '8px 12px', background: '#f9f5ff', border: '1px solid #e9d7fe', borderRadius: 8 }}>
        <Clock size={12} color="#7f56d9" style={{ flexShrink: 0, marginTop: 1 }} />
        <div>
            <span style={{ fontSize: 9, fontWeight: 900, color: '#6941c6', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{date}</span>
            <p style={{ fontSize: 11, color: '#475467', fontWeight: 500, margin: '2px 0 0' }}>{text}</p>
        </div>
    </div>
);

const DraftContent = ({ context, drawerData }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <label style={{ fontSize: 9, fontWeight: 900, color: '#667085', textTransform: 'uppercase', letterSpacing: '0.12em' }}>Subject Line</label>
                <span style={{ fontSize: 8, fontWeight: 900, color: '#12b76a', textTransform: 'uppercase' }}>Auto-Optimized</span>
            </div>
            <input
                type="text"
                defaultValue={drawerData.subject || context.subject || 'Re: Portfolio Update'}
                style={{ width: '100%', padding: 12, background: '#f8f9fb', border: '1px solid #eaecf0', borderRadius: 10, fontSize: 12, fontWeight: 600, color: '#101828', outline: 'none', boxSizing: 'border-box' }}
            />
        </div>
        <div>
            <label style={{ fontSize: 9, fontWeight: 900, color: '#667085', textTransform: 'uppercase', letterSpacing: '0.12em', display: 'block', marginBottom: 6 }}>Message Body</label>
            <textarea
                style={{ width: '100%', height: 220, padding: 16, background: '#f8f9fb', border: '1px solid #eaecf0', borderRadius: 10, fontSize: 12, color: '#475467', lineHeight: 1.7, fontWeight: 500, outline: 'none', resize: 'none', boxSizing: 'border-box' }}
                defaultValue={drawerData.body || ''}
            />
        </div>
        <div style={{ padding: 12, background: '#f9f5ff', borderRadius: 10, border: '1px solid #e9d7fe', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Shield size={13} color="#7f56d9" />
                <span style={{ fontSize: 10, fontWeight: 700, color: '#6941c6' }}>Compliance Guardrail Active</span>
            </div>
            <CheckCircle size={13} color="#12b76a" />
        </div>
    </div>
);

const AllocationBar = ({ label, value, color }) => (
    <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 4 }}>
            <span style={{ color: '#667085' }}>{label}</span>
            <span style={{ color: '#101828' }}>{value}%</span>
        </div>
        <div style={{ height: 4, width: '100%', background: '#f2f4f7', borderRadius: 100, overflow: 'hidden' }}>
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                style={{ height: '100%', background: color, borderRadius: 100 }}
            />
        </div>
    </div>
);

const ConfidenceMeter = ({ label, value, color }) => (
    <div style={{ padding: 10, background: '#fcfcfd', border: '1px solid #eaecf0', borderRadius: 10 }}>
        <p style={{ fontSize: 8, fontWeight: 900, color: '#667085', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 6, marginTop: 0 }}>{label}</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ flex: 1, height: 5, background: '#f2f4f7', borderRadius: 100, overflow: 'hidden' }}>
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    style={{ height: '100%', background: color, borderRadius: 100 }}
                />
            </div>
            <span style={{ fontSize: 9, fontWeight: 900, color: '#101828' }}>{value}%</span>
        </div>
    </div>
);

export default DetailPanel;
