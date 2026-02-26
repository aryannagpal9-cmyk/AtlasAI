import React from 'react';
import { motion } from 'framer-motion';
import { Mail, CheckCircle, X, Info, AlertTriangle, ChevronRight, Clock, Shield, Zap } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const urgencyLevels = {
    1: { color: 'bg-blue-500', label: 'Low' },
    2: { color: 'bg-green-500', label: 'Moderate' },
    3: { color: 'bg-yellow-500', label: 'Heightened' },
    4: { color: 'bg-orange-500', label: 'High' },
    5: { color: 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]', label: 'Critical' }
};

const typeBadges = {
    market_risk: 'badge-blue',
    tax_opportunity: 'badge-green',
    compliance_exposure: 'badge-amber'
};

const RiskEventCard = ({ event, onClick }) => {
    const { id, type, urgency, deterministic_classification, created_at, clients } = event;

    const urgencyConfig = urgencyLevels[urgency] || urgencyLevels[3];

    return (
        <motion.div
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -2 }}
            onClick={onClick}
            className="bg-white rounded-[24px] p-6 border border-[#eaecf0] card-shadow cursor-pointer group transition-all"
        >
            <div className="flex justify-between items-start mb-6">
                <div className="flex gap-4 items-center">
                    <div className="flex flex-col items-center">
                        <div className={`w-3 h-3 rounded-full ${urgencyConfig.color} mb-1`} />
                        <div className="h-4 w-[1px] bg-[#eaecf0]" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-black text-[#101828] tracking-tight group-hover:text-[#1570ef] transition-colors font-sans">
                                {clients?.first_name} {clients?.last_name}
                            </h3>
                            <span className={`badge ${typeBadges[type] || 'badge-blue'}`}>
                                {type.replace('_', ' ')}
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#667085] uppercase tracking-wider">
                                <Clock size={12} />
                                {formatDistanceToNow(new Date(created_at))} ago
                            </div>
                            <div className="w-1 h-1 bg-[#eaecf0] rounded-full" />
                            <div className="flex items-center gap-1 text-[11px] font-bold text-[#667085] uppercase tracking-wider">
                                Urgency: {urgencyConfig.label}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-2 hover:bg-[#f9fafb] rounded-lg text-[#98a2b3] group-hover:text-[#1570ef] transition-all">
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>

            <div className="pl-7">
                <p className="text-sm text-[#475467] font-medium leading-relaxed mb-6 line-clamp-2">
                    {deterministic_classification.reason}
                </p>

                <div className="flex items-center justify-between pt-5 border-t border-[#f2f4f7]">
                    <div className="flex gap-3">
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-[#f9fafb] rounded-full border border-[#eaecf0]">
                            <Shield size={12} className="text-[#667085]" />
                            <span className="text-[10px] font-bold text-[#667085] uppercase tracking-wider">Suitability Clear</span>
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-[#f9fafb] rounded-full border border-[#eaecf0]">
                            <Zap size={12} className="text-[#667085]" />
                            <span className="text-[10px] font-bold text-[#667085] uppercase tracking-wider">Market-Linked</span>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <button className="px-4 py-2 text-xs font-bold text-[#344054] hover:bg-[#f9fafb] rounded-xl transition-colors">
                            Dismiss
                        </button>
                        <button className="px-4 py-2 text-xs font-bold text-white bg-[#101828] hover:bg-[#1d2939] rounded-xl shadow-sm transition-all">
                            Action
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default RiskEventCard;
