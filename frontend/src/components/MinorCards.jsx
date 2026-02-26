import React from 'react';
import { Mail, Send, Edit3, X, Eye, Clock, TrendingDown, TrendingUp, Activity, AlertTriangle, ChevronRight, MessageSquare, Target, Zap } from 'lucide-react';

export const DraftCard = ({ item, onDetail }) => {
    return (
        <div className="card-elevated bg-white">
            <div className="accent-strip strip-draft" />

            <div className="p-6 pl-8">
                <header className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-[#f2f4f7] border border-[#eaecf0] flex items-center justify-center text-[#667085] shadow-sm">
                            <Mail size={20} />
                        </div>
                        <div>
                            <h3 className="text-[14px] font-black text-[#101828] uppercase tracking-wider mb-0.5">Draft Intelligence Prepared</h3>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold text-[#667085] uppercase tracking-widest">{item.client.first_name} {item.client.last_name}</span>
                                <div className="w-1 h-1 rounded-full bg-[#d0d5dd]" />
                                <span className="text-[9px] font-black text-[#475467] uppercase tracking-tighter bg-[#f2f4f7] px-1.5 py-0.5 rounded-md self-center">{item.tone}</span>
                            </div>
                        </div>
                    </div>
                    <span className="text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest">{item.timestamp}</span>
                </header>

                <div className="grid grid-cols-3 gap-6 mb-6">
                    <div className="col-span-2 bg-[#fcfdfe] border border-[#eaecf0] p-4 rounded-xl shadow-inner group transition-all hover:bg-white">
                        <p className="text-[10px] font-black text-[#101828] uppercase tracking-widest mb-2 flex items-center gap-2">
                            <MessageSquare size={12} className="text-[#667085]" />
                            Subject: {item.subject}
                        </p>
                        <p className="text-[12px] text-[#475467] font-medium italic leading-relaxed line-clamp-2">
                            "{item.body}"
                        </p>
                    </div>
                    <div className="metric-grid h-fit self-center">
                        <div className="mini-metric">
                            <p className="mini-metric-label">Tone Match</p>
                            <p className="mini-metric-value text-[#12b76a]">98%</p>
                        </div>
                        <div className="mini-metric">
                            <p className="mini-metric-label">Length</p>
                            <p className="mini-metric-value">124w</p>
                        </div>
                    </div>
                </div>

                {/* Metadata Footer */}
                <div className="flex justify-between items-center mb-6 px-1">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-1.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-[#667085]" />
                            <span className="text-[8px] font-black text-[#667085] uppercase tracking-tighter">Draft Template STABLE</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Target size={12} className="text-[#98a2b3]" />
                            <span className="text-[8px] font-bold text-[#98a2b3] uppercase tracking-tighter">ID: {item.trace_id}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Clock size={12} className="text-[#98a2b3]" />
                            <span className="text-[8px] font-bold text-[#98a2b3] uppercase tracking-tighter">Generated 2h ago</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 text-[9px] font-black text-[#667085] uppercase tracking-widest cursor-pointer hover:text-[#101828]">
                        Full Trace Log {'->'}
                    </div>
                </div>

                <div className="flex items-center justify-between pt-6 border-t border-[#f2f4f7]">
                    <div className="flex gap-6">
                        <button
                            onClick={() => onDetail(item)}
                            className="flex items-center gap-2 text-[11px] font-black uppercase tracking-wider text-[#667085] hover:text-[#101828] transition-colors"
                        >
                            <Eye size={14} />
                            Review Analysis
                        </button>
                        <button className="flex items-center gap-2 text-[11px] font-black uppercase tracking-wider text-[#667085] hover:text-[#101828] transition-colors">
                            <Edit3 size={14} />
                            Edit Draft
                        </button>
                    </div>
                    <div className="flex gap-3">
                        <button className="px-4 py-2 text-[11px] font-black uppercase tracking-wider text-white bg-[#101828] hover:bg-[#1d2939] rounded-xl shadow-lg transition-all flex items-center gap-2">
                            <Send size={14} />
                            Send Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export const MarketInterruptCard = ({ item }) => {
    return (
        <div className="card-elevated bg-white relative overflow-hidden">
            <div className="accent-strip strip-market" />

            <div className="p-8 pl-10">
                <header className="mb-8 relative z-10 flex justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3 mb-4">
                            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#fef3f2] border border-[#fee4e2] rounded-lg">
                                <AlertTriangle size={12} className="text-[#d92d20]" />
                                <span className="text-[10px] font-black text-[#b42318] uppercase tracking-[0.1em]">Market Interrupt</span>
                            </div>
                            <span className="text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest">{item.timestamp}</span>
                        </div>
                        <h2 className="text-3xl font-black text-[#101828] tracking-tight mb-2">Significant UK Market Movement Detected</h2>
                        <p className="text-sm text-[#475467] font-medium leading-relaxed max-w-lg">
                            Trigger: {item.asset} fell {item.movement}% below baseline within 60m session window. Deterministic monitoring active for sector contagion.
                        </p>
                    </div>
                    <div className="w-16 h-16 rounded-2xl bg-[#fef3f2] border border-[#fee4e2] flex items-center justify-center text-[#d92d20] shadow-sm animate-pulse">
                        <Activity size={32} />
                    </div>
                </header>

                <div className="grid grid-cols-4 gap-4 mb-8 relative z-10">
                    <MetricBox label="FTSE 100" value={`${item.movement}%`} isDown />
                    <MetricBox label="Gilts 10Y" value="4.12%" isUp />
                    <MetricBox label="Energy" value="+3.2%" isUp />
                    <MetricBox label="GBP/USD" value="1.26" isDown />
                </div>

                <div className="grid grid-cols-2 gap-8 mb-8 relative z-10">
                    <div>
                        <p className="text-[10px] font-black text-[#667085] uppercase tracking-[0.2em] mb-4">Affected Portfolios</p>
                        <div className="space-y-2">
                            {item.affected_clients.map((affected, idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-white border border-[#eaecf0] rounded-xl hover:bg-[#f9fafb] transition-all cursor-pointer group shadow-sm">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-1.5 h-1.5 rounded-full ${affected.urgency === 5 ? 'bg-[#d92d20]' : 'bg-[#f79009]'}`} />
                                        <span className="text-xs font-bold text-[#101828]">{affected.client_name}</span>
                                    </div>
                                    <ChevronRight size={14} className="text-[#98a2b3]" />
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="space-y-4">
                        <div className="p-5 bg-[#fcfdfe] border border-[#eaecf0] rounded-2xl shadow-inner h-full flex flex-col justify-center">
                            <p className="text-[9px] font-black text-[#101828] uppercase tracking-[0.2em] mb-3">System Confidence</p>
                            <div className="flex items-end justify-between mb-2">
                                <span className="text-[10px] font-bold text-[#667085] uppercase tracking-widest">Signal Source: Bloomberg</span>
                                <span className="text-lg font-black text-[#12b76a]">100%</span>
                            </div>
                            <div className="mini-bar-bg">
                                <div className="mini-bar-fill bg-[#12b76a]" style={{ width: '100%' }} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Metadata Trace Footer */}
                <div className="flex justify-between items-center px-1 py-4 border-t border-[#f2f4f7]">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <Activity size={12} className="text-[#d92d20]" />
                            <span className="text-[9px] font-black text-[#667085] uppercase tracking-tighter">Event Propagated: LN-04</span>
                        </div>
                        <div className="flex items-center gap-2 border-l border-[#eaecf0] pl-6 text-[#98a2b3]">
                            <Target size={12} />
                            <span className="text-[9px] font-bold uppercase tracking-tighter">TRACE_LOG: {item.trace_id}</span>
                        </div>
                    </div>
                    <div className="text-[9px] font-black text-[#1570ef] uppercase tracking-widest cursor-pointer hover:underline">
                        Audit Analysis {'->'}
                    </div>
                </div>
            </div>
        </div>
    );
};

const MetricBox = ({ label, value, isDown, isUp }) => (
    <div className="p-4 bg-[#fcfdfe] border border-[#eaecf0] rounded-xl shadow-inner">
        <p className="text-[9px] font-black text-[#667085] uppercase tracking-widest mb-1">{label}</p>
        <div className="flex items-center gap-1.5">
            <p className={`text-lg font-black ${isDown ? 'text-[#d92d20]' : isUp ? 'text-[#12b76a]' : 'text-[#101828]'}`}>
                {value}
            </p>
            {isDown && <TrendingDown size={14} className="text-[#d92d20]" />}
            {isUp && <TrendingUp size={14} className="text-[#12b76a]" />}
        </div>
    </div>
);
