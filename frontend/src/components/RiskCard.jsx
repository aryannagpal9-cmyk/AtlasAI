import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    MessageSquare, CheckCircle, X, ChevronRight,
    Send, Info, Shield, Zap, AlertTriangle, Clock, TrendingDown, Eye, Activity, Target
} from 'lucide-react';

const RiskCard = ({ item, onDetail }) => {
    const [isDiscussing, setIsDiscussing] = useState(false);
    const [messages, setMessages] = useState(item.discussion || []);
    const [inputValue, setInputValue] = useState("");

    const handleSendMessage = () => {
        if (!inputValue.trim()) return;
        setMessages([...messages, { role: 'user', content: inputValue }]);
        setInputValue("");
        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'atlas',
                content: "Deterministic analysis confirms David's Financials concentration is the primary driver of this volatility gap. Would you like a Sector Shift draft prepared?"
            }]);
        }, 800);
    };

    const isCritical = item.urgency === 5;

    return (
        <div className={`card-elevated ${isCritical ? 'pulse-critical' : ''}`}>
            {/* Accent Strip */}
            <div className="accent-strip strip-market" />

            <div className="p-6 pl-8">
                {/* Header */}
                <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-[#eff8ff] border border-[#d1e9ff] flex items-center justify-center text-[#1570ef] shadow-sm">
                            <Shield size={20} />
                        </div>
                        <div>
                            <h3 className="text-base font-black text-[#101828] leading-none mb-1">{item.client.first_name} {item.client.last_name}</h3>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-[#1570ef] uppercase tracking-wider">Market Risk</span>
                                <div className="w-1 h-1 rounded-full bg-[#d0d5dd]" />
                                <span className="text-[10px] font-black text-[#667085] uppercase tracking-wider bg-[#f2f4f7] px-1.5 py-0.5 rounded">Urgency {item.urgency}</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest">{item.timestamp}</span>
                        {isCritical && (
                            <div className="flex items-center gap-1.5 mt-1">
                                <Activity size={10} className="text-[#d92d20]" />
                                <span className="text-[9px] font-black text-[#d92d20] uppercase tracking-tighter animate-pulse">Critical Trace Active</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Content Grid (2 Columns) */}
                <div className="grid grid-cols-2 gap-8 mb-6">
                    {/* Left: Summary & Main Deltas */}
                    <div className="space-y-4">
                        <p className="text-[13px] text-[#344054] font-medium leading-relaxed">
                            {item.summary}
                        </p>
                        <div className="flex flex-wrap gap-2">
                            <div className="data-chip">
                                <TrendingDown size={10} className="text-[#d92d20]" />
                                FTSE: {item.market_deltas.ftse}
                            </div>
                            <div className="data-chip">
                                <Zap size={10} className="text-[#f79009]" />
                                Energy: {item.market_deltas.energy}
                            </div>
                            <div className="data-chip border-[#1570ef]/30 bg-[#eff8ff]">
                                <Activity size={10} className="text-[#1570ef]" />
                                Gap: {item.market_deltas.vol_gap}
                            </div>
                        </div>
                    </div>

                    {/* Right: Technical Trace Summary (Data Density) */}
                    <div className="metric-grid">
                        <div className="mini-metric">
                            <p className="mini-metric-label">Vol Ratio</p>
                            <p className="mini-metric-value">1.42x</p>
                        </div>
                        <div className="mini-metric">
                            <p className="mini-metric-label">Sector WT</p>
                            <p className="mini-metric-value">42.8%</p>
                        </div>
                        <div className="mini-metric">
                            <p className="mini-metric-label">Conf Score</p>
                            <p className="mini-metric-value">98%</p>
                        </div>
                        <div className="mini-metric">
                            <p className="mini-metric-label">Sync Age</p>
                            <p className="mini-metric-value">4.2ms</p>
                        </div>
                    </div>
                </div>

                {/* Intelligence Trace Log */}
                {item.trace && (
                    <div className="mb-6 bg-[#fcfdfe] border border-[#eaecf0] rounded-xl overflow-hidden">
                        <div className="px-4 py-2 bg-white border-b border-[#eaecf0] flex justify-between items-center">
                            <p className="text-[9px] font-black text-[#101828] uppercase tracking-[0.2em]">Internal Intelligence Trace</p>
                            <span className="text-[8px] font-mono text-[#98a2b3]">Sentinel v4.2 // Node: LN-04</span>
                        </div>
                        <div className="p-4 space-y-2">
                            {item.trace.map((step, idx) => (
                                <div key={idx} className="flex items-center gap-3 text-[11px] font-medium text-[#475467]">
                                    <div className="w-1 h-1 rounded-full bg-[#d0d5dd]" />
                                    <span className="text-[#98a2b3] w-4">{idx + 1}.</span>
                                    {step}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Metadata Footer */}
                <div className="flex justify-between items-center mb-6 px-1">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-[#12b76a] shadow-[0_0_4px_#12b76a]" />
                            <span className="text-[9px] font-black text-[#667085] uppercase tracking-tighter">Deterministic Verified</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Target size={12} className="text-[#98a2b3]" />
                            <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-tighter">ID: {item.trace_id}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Clock size={12} className="text-[#98a2b3]" />
                            <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-tighter">Analyzed 120s ago</span>
                        </div>
                    </div>
                    <div className="text-[9px] font-black text-[#1570ef] uppercase tracking-widest cursor-pointer hover:underline underline-offset-4">
                        Deep Audit {'->'}
                    </div>
                </div>

                {/* Discussion */}
                <AnimatePresence>
                    {isDiscussing && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden border-t border-[#eaecf0] -mx-8 px-8 pt-6 mb-6 bg-[#fcfdfe]"
                        >
                            <div className="space-y-4 mb-6 flex flex-col">
                                {messages.map((msg, idx) => (
                                    <div key={idx} className={msg.role === 'atlas' ? 'message-atlas' : 'message-user'}>
                                        {msg.content}
                                    </div>
                                ))}
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Interrogate this deterministic signal..."
                                    className="discuss-input"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                />
                                <button
                                    onClick={handleSendMessage}
                                    className="p-2 bg-[#101828] text-white rounded-lg hover:bg-[#1d2939] transition-colors shadow-sm"
                                >
                                    <Send size={14} />
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Actions */}
                <div className="flex items-center justify-between pt-6 border-t border-[#eaecf0]">
                    <div className="flex gap-6">
                        <button
                            onClick={() => setIsDiscussing(!isDiscussing)}
                            className={`flex items-center gap-2 text-[11px] font-black uppercase tracking-wider transition-colors ${isDiscussing ? 'text-[#1570ef]' : 'text-[#667085] hover:text-[#101828]'}`}
                        >
                            <MessageSquare size={14} />
                            Discuss Signal
                        </button>
                        <button
                            onClick={() => onDetail(item)}
                            className="flex items-center gap-2 text-[11px] font-black uppercase tracking-wider text-[#667085] hover:text-[#101828] transition-colors"
                        >
                            <Eye size={14} />
                            Full Audit Trace
                        </button>
                    </div>
                    <div className="flex gap-3">
                        <button className="px-4 py-2 text-[11px] font-black uppercase tracking-wider text-[#101828] border border-[#d0d5dd] hover:bg-[#f8f9fb] rounded-xl transition-all">
                            Dismiss
                        </button>
                        <button className="px-4 py-2 text-[11px] font-black uppercase tracking-wider text-white bg-[#101828] hover:bg-[#1d2939] rounded-xl shadow-lg transition-all">
                            Prepare Outcome
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RiskCard;
