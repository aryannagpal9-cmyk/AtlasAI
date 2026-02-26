import React from 'react';
import { Mail, Send, Edit3, X, Eye, Clock } from 'lucide-react';

const DraftCard = ({ item, onAction, onDetail }) => {
    return (
        <div className="card-container relative pl-1">
            <div className="accent-strip strip-draft" />
            <div className="p-6">
                <header className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-[#f2f4f7] flex items-center justify-center text-[#667085]">
                            <Mail size={18} />
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-[#101828]">Draft Prepared – {item.client.first_name} {item.client.last_name}</h3>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="badge badge-grey">{item.tone}</span>
                            </div>
                        </div>
                    </div>
                    <span className="text-[10px] font-bold text-[#98a2b3] uppercase tracking-widest flex items-center gap-1">
                        <Clock size={10} /> 09:30 AM
                    </span>
                </header>

                <div className="mb-6 space-y-1">
                    <p className="text-[10px] font-black text-[#667085] uppercase tracking-widest">Subject: {item.subject}</p>
                    <p className="text-sm text-[#475467] font-medium italic line-clamp-2">
                        "{item.body}"
                    </p>
                </div>

                <div className="flex items-center justify-between pt-5 border-t border-[#f2f4f7]">
                    <div className="flex gap-4">
                        <button
                            onClick={() => onDetail(item)}
                            className="flex items-center gap-2 text-xs font-black text-[#667085] hover:text-[#101828] transition-colors"
                        >
                            <Eye size={14} />
                            Review
                        </button>
                        <button className="flex items-center gap-2 text-xs font-black text-[#667085] hover:text-[#101828] transition-colors">
                            <Edit3 size={14} />
                            Edit
                        </button>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onAction(item.id, 'dismiss')}
                            className="px-3 py-1.5 text-xs font-bold text-[#667085] hover:bg-[#f9fafb] rounded-lg transition-colors"
                        >
                            Dismiss
                        </button>
                        <button className="px-3 py-1.5 text-xs font-bold text-white bg-[#101828] hover:bg-[#1d2939] rounded-lg shadow-sm transition-all flex items-center gap-2">
                            <Send size={12} />
                            Approve & Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DraftCard;
