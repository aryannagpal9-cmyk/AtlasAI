import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, User, Shield, Zap, Mail, CheckCircle, ChevronRight, AlertCircle, Info } from 'lucide-react';

const MeetingBriefCard = ({ brief, onDraft, onReview }) => {
    const { clients, meeting_time, sections } = brief;

    return (
        <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-[32px] p-8 border border-[#eaecf0] card-shadow overflow-hidden relative"
        >
            <div className="absolute top-0 right-0 p-8">
                <div className="w-12 h-12 rounded-2xl bg-[#f9fafb] flex items-center justify-center text-[#98a2b3]">
                    <Calendar size={24} />
                </div>
            </div>

            <header className="mb-10">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] font-black text-[#1570ef] uppercase tracking-[0.2em]">Upcoming Meeting</span>
                    <div className="w-1 h-1 bg-[#eaecf0] rounded-full" />
                    <span className="text-[10px] font-black text-[#667085] uppercase tracking-[0.2em]">{meeting_time}</span>
                </div>
                <h3 className="text-3xl font-black text-[#101828] tracking-tight">{clients?.first_name} {clients?.last_name}</h3>
            </header>

            <div className="grid grid-cols-2 gap-10 mb-10">
                <section>
                    <h4 className="text-[10px] font-black text-[#667085] uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Shield size={14} className="text-[#101828]" />
                        Risk Alignment Status
                    </h4>
                    <div className="p-4 rounded-2xl bg-[#eff8ff] border border-[#b2ddff]">
                        <p className="text-xs text-[#175cd3] font-bold leading-relaxed">
                            Portfolio remains within 5% variance of target risk model.
                            No immediate rebalancing required.
                        </p>
                    </div>
                </section>

                <section>
                    <h4 className="text-[10px] font-black text-[#667085] uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Zap size={14} className="text-[#f79009]" />
                        Behavioural Reminders
                    </h4>
                    <div className="p-4 rounded-2xl bg-[#fffaf0] border border-[#fedf89]">
                        <p className="text-xs text-[#b54708] font-bold leading-relaxed">
                            Client previously expressed concern about UK inflation.
                            Ready stats on Gilt performance.
                        </p>
                    </div>
                </section>
            </div>

            <div className="space-y-6 mb-10">
                <section>
                    <h4 className="text-[10px] font-black text-[#667085] uppercase tracking-widest mb-4">Suggested Talking Points</h4>
                    <ul className="space-y-3">
                        <li className="flex gap-3 text-sm text-[#475467] font-medium leading-relaxed">
                            <CheckCircle size={16} className="text-[#039855] shrink-0 mt-0.5" />
                            Review of ISA/SIPP tax allowances before April deadline.
                        </li>
                        <li className="flex gap-3 text-sm text-[#475467] font-medium leading-relaxed">
                            <CheckCircle size={16} className="text-[#039855] shrink-0 mt-0.5" />
                            Discussion on FTSE 100 dividend yields relative to cash.
                        </li>
                    </ul>
                </section>
            </div>

            <div className="flex gap-3 pt-8 border-t border-[#eaecf0]">
                <button
                    onClick={onDraft}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-[#101828] text-white rounded-xl text-xs font-bold hover:bg-[#1d2939] transition-all shadow-sm"
                >
                    <Mail size={16} />
                    Generate Draft
                </button>
                <button
                    onClick={onReview}
                    className="flex-1 py-3 bg-white border border-[#d0d5dd] text-[#344054] rounded-xl text-xs font-bold hover:bg-[#f9fafb] transition-all shadow-sm"
                >
                    Mark Reviewed
                </button>
            </div>
        </motion.div>
    );
};

export default MeetingBriefCard;
