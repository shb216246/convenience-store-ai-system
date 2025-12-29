import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
    type?: 'card' | 'text' | 'chart' | 'table';
    count?: number;
}

export function LoadingSkeleton({ type = 'card', count = 1 }: LoadingSkeletonProps) {
    const renderSkeleton = () => {
        switch (type) {
            case 'card':
                return (
                    <div className="bg-white rounded-xl p-6 border border-slate-200 animate-pulse">
                        <div className="h-4 bg-slate-200 rounded w-1/3 mb-4"></div>
                        <div className="h-8 bg-slate-200 rounded w-1/2 mb-2"></div>
                        <div className="h-3 bg-slate-200 rounded w-1/4"></div>
                    </div>
                );

            case 'text':
                return (
                    <div className="animate-pulse space-y-2">
                        <div className="h-4 bg-slate-200 rounded w-full"></div>
                        <div className="h-4 bg-slate-200 rounded w-5/6"></div>
                        <div className="h-4 bg-slate-200 rounded w-4/6"></div>
                    </div>
                );

            case 'chart':
                return (
                    <div className="bg-white rounded-xl p-6 border border-slate-200 animate-pulse">
                        <div className="h-4 bg-slate-200 rounded w-1/4 mb-4"></div>
                        <div className="h-64 bg-slate-200 rounded"></div>
                    </div>
                );

            case 'table':
                return (
                    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden animate-pulse">
                        <div className="h-12 bg-slate-200"></div>
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="h-16 bg-white border-t border-slate-200 flex items-center px-6 gap-4">
                                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                            </div>
                        ))}
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <>
            {[...Array(count)].map((_, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                >
                    {renderSkeleton()}
                </motion.div>
            ))}
        </>
    );
}
