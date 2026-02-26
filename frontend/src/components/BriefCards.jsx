import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Clock, MapPin, User, Sparkles, ChevronRight, Shield, Zap, CheckCircle, ChevronDown, Target, Activity, Info } from 'lucide-react';

export const MorningBriefCard = ({ item }) => {
    return (
        <div className="card-elevated bg-white">
            <div className="accent-strip strip-meeting" />
            <div className="p-6 pl-8">
                <header className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-[#f9f5ff] border border-[#d6bbfb] flex items-center justify-center text-[#7f56d9] shadow-sm">
                            <Sparkles size={20} />
                        </div>
                        <div>
                            <h3 className="text-[14px] font-black text-[#101828] uppercase tracking-wider">Morning Proactiveness</h3>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[10px] font-bold text-[#7f56d9] uppercase tracking-widest">Focus: Outreach Prep</span>
                                <div className="w-1 h-1 rounded-full bg-[#d0d5dd]" />
                                <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-tighter">Evaluated 12m ago</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest">{item.timestamp}</span>
                        <div className="flex items-center gap-1.5 mt-1 text-[#7f56d9]">
                            <Clock size={10} />
                            <span className="text-[9px] font-black uppercase tracking-tighter">Queue: 3 Items</span>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-2 gap-6 mb-8">
                    <div className="space-y-3">
                        <p className="text-[9px] font-black text-[#98a2b3] uppercase tracking-[0.2em] mb-4">Priority Outreach</p>
                        <div className="flex items-center justify-between p-3 bg-[#fcfdfe] border border-[#eaecf0] rounded-xl hover:border-[#7f56d9] transition-all cursor-pointer group shadow-sm">
                            <div className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_4px_rgba(239,68,68,0.5)]" />
                                <span className="text-xs font-bold text-[#344054]">David Richardson</span>
                            </div>
                            <ChevronRight size={14} className="text-[#98a2b3] group-hover:text-[#7f56d9]" />
                        </div>
                        <div className="flex items-center justify-between p-3 bg-[#fcfdfe] border border-[#eaecf0] rounded-xl hover:border-[#7f56d9] transition-all cursor-pointer group shadow-sm">
                            <div className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-orange-500 shadow-[0_0_4px_rgba(247,144,9,0.5)]" />
                                <span className="text-xs font-bold text-[#344054]">Sarah Jennings</span>
                            </div>
                            <ChevronRight size={14} className="text-[#98a2b3] group-hover:text-[#7f56d9]" />
                        </div>
                    </div>

                    <div className="bg-[#f9f5ff]/30 border border-[#e9d7fe] rounded-xl p-4">
                        <p className="text-[9px] font-black text-[#7f56d9] uppercase tracking-[0.2em] mb-3">Today's Directive</p>
                        <p className="text-[11px] text-[#6941c6] font-medium leading-relaxed italic">
                            "Execute defensive shifts for energy-exposed mandates. Prioritize Jennings ISA review for year-end compliance."
                        </p>
                    </div>
                </div>

                {/* Intelligence Trace Footer */}
                <div className="flex justify-between items-center px-1 py-3 border-t border-[#f2f4f7]">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                            <Activity size={10} className="text-[#12b76a]" />
                            <span className="text-[8px] font-black text-[#667085] uppercase tracking-tighter">Log Ready</span>
                        </div>
                        <span className="text-[8px] font-bold text-[#98a2b3] uppercase tracking-tighter">ID: {item.id}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-[8px] font-black text-[#7f56d9] uppercase tracking-widest cursor-pointer hover:underline">Full System Output {'->'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export const MeetingBriefCard = ({ item, onDetail }) => {
    return (
        <div className="card-elevated bg-white">
            <div className="accent-strip strip-meeting" />
            <div className="p-8 pl-10">
                <header className="flex justify-between items-start mb-8">
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#f9f5ff] border border-[#d6bbfb] rounded-lg">
                                <Clock size={12} className="text-[#7f56d9]" />
                                <span className="text-[10px] font-black text-[#7f56d9] uppercase tracking-[0.1em]">{item.meeting_time}</span>
                            </div>
                            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[#fff1f3] border border-[#fda29b] rounded-lg animate-pulse">
                                <Activity size={12} className="text-[#d92d20]" />
                                <span className="text-[10px] font-black text-[#b42318] uppercase tracking-[0.1em]">Starts in {item.countdown}</span>
                            </div>
                        </div>
                        <h3 className="text-3xl font-black text-[#101828] tracking-tight mb-1">{item.client.first_name} {item.client.last_name}</h3>
                        <p className="text-[11px] font-bold text-[#667085] uppercase tracking-[0.3em]">Command Central // Prep Briefing</p>
                    </div>
                    <div className="w-16 h-16 rounded-2xl bg-[#fcfdfe] border border-[#eaecf0] flex items-center justify-center text-[#7f56d9] shadow-sm shrink-0 scale-110">
                        <Calendar size={32} />
                    </div>
                </header>

                {/* Content Matrix (Density) */}
                <div className="grid grid-cols-2 gap-8 mb-8">
                    {/* Left: Progress/Confidence */}
                    <div className="space-y-4 p-5 bg-[#fcfdfe] border border-[#eaecf0] rounded-2xl shadow-inner">
                        <div className="flex justify-between items-end mb-2">
                            <div>
                                <p className="text-[9px] font-black text-[#101828] uppercase tracking-widest">Risk Alignment</p>
                                <p className="text-[8px] text-[#98a2b3] lowercase">deterministic verify: pass</p>
                            </div>
                            <span className="text-lg font-black text-[#12b76a]">94%</span>
                        </div>
                        <div className="mini-bar-bg relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent w-full animate-[pulse_2s_infinite]" />
                            <div className="mini-bar-fill bg-[#12b76a]" style={{ width: '94%' }} />
                        </div>
                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#f2f4f7]">
                            <div>
                                <p className="text-[8px] font-black text-[#98a2b3] uppercase tracking-widest">Sentiment</p>
                                <p className="text-[10px] font-bold text-[#101828]">Defensive</p>
                            </div>
                            <div>
                                <p className="text-[8px] font-black text-[#98a2b3] uppercase tracking-widest">Last Contact</p>
                                <p className="text-[10px] font-bold text-[#101828]">4 days ago</p>
                            </div>
                        </div>
                    </div>

                    {/* Right: Talking Points (Density) */}
                    <div className="space-y-4">
                        <p className="text-[9px] font-black text-[#98a2b3] uppercase tracking-[0.2em] ml-1">Key Talking Directives</p>
                        <div className="space-y-3">
                            <div className="p-3 bg-white border border-[#eaecf0] rounded-xl flex gap-3 shadow-sm hover:border-[#7f56d9] transition-colors cursor-pointer group">
                                <CheckCircle size={14} className="text-[#12b76a] mt-0.5" />
                                <div className="flex-1">
                                    <p className="text-[11px] font-bold text-[#101828] leading-tight">Review ISA Rebalance</p>
                                    <p className="text-[9px] text-[#667085] mt-1 line-clamp-1">Deterministic tax opt. ready for sign-off.</p>
                                </div>
                                <ChevronRight size={14} className="text-[#d0d5dd] group-hover:text-[#7f56d9]" />
                            </div>
                            <div className="p-3 bg-white border border-[#eaecf0] rounded-xl flex gap-3 shadow-sm hover:border-[#7f56d9] transition-colors cursor-pointer group">
                                <Info size={14} className="text-[#1570ef] mt-0.5" />
                                <div className="flex-1">
                                    <p className="text-[11px] font-bold text-[#101828] leading-tight">FTSE Volatility Response</p>
                                    <p className="text-[9px] text-[#667085] mt-1 line-clamp-1">Proactive empathy protocol suggested.</p>
                                </div>
                                <ChevronRight size={14} className="text-[#d0d5dd] group-hover:text-[#7f56d9]" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Metadata Trace Footer */}
                <div className="flex justify-between items-center mb-8 px-1 py-4 border-y border-[#f2f4f7]">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <Activity size={12} className="text-[#7f56d9]" />
                            <span className="text-[9px] font-black text-[#667085] uppercase tracking-tighter">Sync: STABLE v4.2</span>
                        </div>
                        <div className="flex items-center gap-2 border-l border-[#eaecf0] pl-6">
                            <Shield size={12} className="text-[#12b76a]" />
                            <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-tighter italic">Compliance guardrails verified</span>
                        </div>
                    </div>
                    <span className="text-[9px] font-bold text-[#98a2b3] uppercase tracking-tighter">TRACE_LOG:MTG_881B</span>
                </div>

                <div className="flex gap-4">
                    <button className="flex-1 py-4 bg-[#101828] text-white rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-[#1d2939] transition-all shadow-xl flex items-center justify-center gap-3">
                        <Target size={18} />
                        Open Prep Cockpit
                    </button>
                    <button className="px-8 py-4 bg-white border-2 border-[#eaecf0] text-[#344054] rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-[#f8f9fb] transition-all">
                        Mark Reviewed
                    </button>
                </div>
            </div>
        </div>
    );
};
