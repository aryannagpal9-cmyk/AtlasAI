import React from 'react';
import { motion } from 'framer-motion';
import { X, Shield, Activity, Zap, CheckCircle, Send, Target, BarChart3, Clock, Brain, TrendingDown, Globe, Users } from 'lucide-react';

const DetailPanel = ({ context, onClose }) => {
    if (!context) return null;

    const d = context.drawerData || {};
    const isDraft = d.isDraft || context.type === 'draft';
    const isMarketInterrupt = d.isMarketInterrupt || context.type === 'market_interrupt';

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
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

            {/* Tabs */}
            <div style={{ padding: '0 24px', borderBottom: '1px solid #f2f4f7', background: '#fcfdfe', display: 'flex', gap: 20 }}>
                {['Intelligence', 'Discussion', 'Directives'].map(tab => (
                    <button key={tab} style={{ padding: '8px 0', fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#667085', border: 'none', background: 'transparent', borderBottom: '2px solid transparent', cursor: 'pointer' }}>
                        {tab}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 28 }}>
                {isDraft ? (
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
                        style={{ width: '100%', height: 40, paddingLeft: 14, paddingRight: 44, background: '#f8f9fb', border: '1px solid #eaecf0', borderRadius: 10, fontSize: 12, fontWeight: 500, outline: 'none', boxSizing: 'border-box' }}
                    />
                    <button style={{ position: 'absolute', right: 6, top: '50%', transform: 'translateY(-50%)', width: 28, height: 28, background: '#101828', color: 'white', border: 'none', borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                        <Send size={12} />
                    </button>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    {isDraft ? (
                        <button style={{ flex: 1, padding: '10px 0', background: '#101828', color: 'white', border: 'none', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
                            Finalize & Send
                        </button>
                    ) : (
                        <>
                            <button style={{ flex: 1, padding: '10px 0', background: '#101828', color: 'white', border: 'none', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
                                Prepare Action
                            </button>
                            <button style={{ flex: 1, padding: '10px 0', background: 'white', color: '#344054', border: '1px solid #d0d5dd', borderRadius: 10, fontSize: 9, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.18em', cursor: 'pointer' }}>
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

        {/* Memory for draft */}
        {drawerData.memory && drawerData.memory.length > 0 && (
            <section style={{ paddingTop: 12, borderTop: '1px solid #f2f4f7' }}>
                <SectionTitle icon={<Brain size={13} color="#7f56d9" />} label="Context Memory" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {drawerData.memory.map((m, i) => (
                        <MemoryItem key={i} date={m.date} text={m.text} />
                    ))}
                </div>
            </section>
        )}

        {/* Trace for draft */}
        {drawerData.trace && drawerData.trace.length > 0 && (
            <section style={{ paddingTop: 12, borderTop: '1px solid #f2f4f7' }}>
                <SectionTitle icon={<Shield size={13} color="#12b76a" />} label="Draft Trace" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {drawerData.trace.map((step, idx) => (
                        <div key={idx} style={{ display: 'flex', gap: 8, fontSize: 10, color: '#475467', fontWeight: 500, alignItems: 'center' }}>
                            <CheckCircle size={11} color="#12b76a" style={{ flexShrink: 0 }} />
                            {step}
                        </div>
                    ))}
                </div>
            </section>
        )}
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
