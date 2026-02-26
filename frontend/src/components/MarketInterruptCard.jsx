import React from 'react';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, TrendingDown, Clock, ChevronRight, MessageSquare } from 'lucide-react';

const MarketInterruptCard = ({ item }) => {
    return (
        <div className="card-container border-2 border-[#eaecf0] bg-white pt-8 pb-6 px-8 relative overflow-hidden">
            <div className="accent-strip strip-market" />

            {/* Background Graphic */}
            <div className="absolute top-[-20px] right-[-20px] opacity-[0.03] select-none pointer-events-none">
                <TrendingDown size={200} />
            </div>

            <header className="mb-8 relative z-10">
                <div className="flex items-center gap-2 mb-3">
                    <span className="badge badge-blue">Market Interrupt</span>
                    <span className="text-[10px] font-black text-[#667085] uppercase tracking-widest flex items-center gap-1">
                        <Clock size={10} /> 09:00 AM
                    </span>
                </div>
                <h2 className="text-xl font-black text-[#101828] mb-2">Significant UK Market Movement Detected</h2>
                <p className="text-sm text-[#475467] font-medium leading-relaxed max-w-lg">
                    Broad sector volatility observed following London opening. {item.asset} has breached 1.4% downside threshold.
                </p>
            </header>

            <div className="grid grid-cols-3 gap-6 mb-8 relative z-10">
                <div className="p-4 bg-[#fcfcfd] rounded-xl border border-[#eaecf0]">
                    <p className="text-[10px] font-bold text-[#667085] uppercase mb-1">FTSE 100</p>
                    <p className="text-base font-black text-[#d92d20]">{item.movement}%</p>
                </div>
                <div className="p-4 bg-[#fcfcfd] rounded-xl border border-[#eaecf0]">
                    <p className="text-[10px] font-bold text-[#667085] uppercase mb-1">Gilts 10Y</p>
                    <p className="text-base font-black text-[#101828]">4.12% <span className="text-[#12b76a] text-[10px]">↑</span></p>
                </div>
                <div className="p-4 bg-[#fcfcfd] rounded-xl border border-[#eaecf0]">
                    <p className="text-[10px] font-bold text-[#667085] uppercase mb-1">Brent Oil</p>
                    <p className="text-base font-black text-[#101828]">$82.45</p>
                </div>
            </div>

            <div className="space-y-3 relative z-10">
                <p className="text-[10px] font-black text-[#667085] uppercase tracking-widest pl-1">Affected Clients</p>
                {item.affected_clients.map((affected, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-white border border-[#eaecf0] rounded-xl hover:border-[#1570ef] transition-all group cursor-pointer shadow-sm">
                        <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${affected.urgency === 5 ? 'bg-red-500' : 'bg-yellow-500'}`} />
                            <span className="text-sm font-bold text-[#101828]">{affected.client_name}</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <button className="flex items-center gap-1.5 text-[10px] font-bold text-[#667085] group-hover:text-[#1570ef] transition-colors">
                                <MessageSquare size={12} />
                                Discuss
                            </button>
                            <ChevronRight size={14} className="text-[#98a2b3]" />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MarketInterruptCard;
