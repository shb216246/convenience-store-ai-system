import { useState, useEffect } from 'react';
import { TrendingUp, Package, CheckCircle, Clock, XCircle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { API_ENDPOINTS } from '../config';

type OrderHistory = {
    id: number;
    recommendation_date: string;
    total_items: number;
    total_cost: number;
    status: string;
    created_at: string;
    executed_at: string | null;
};

type OrderStatistics = {
    month: string;
    summary: {
        total_orders: number;
        total_items: number;
        total_cost: number;
        executed_count: number;
        pending_count: number;
    };
    daily_data: Array<{
        date: string;
        cost: number;
        count: number;
    }>;
};

export function OrderHistory() {
    const [history, setHistory] = useState<OrderHistory[]>([]);
    const [statistics, setStatistics] = useState<OrderStatistics | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [selectedMonth, setSelectedMonth] = useState<string>(
        new Date().toISOString().slice(0, 7)
    );

    const loadHistory = async () => {
        setIsLoading(true);
        try {
            const params = new URLSearchParams();
            if (statusFilter !== 'all') {
                params.append('status', statusFilter);
            }
            const response = await fetch(`${API_ENDPOINTS.orderHistory}?${params}`);
            if (!response.ok) throw new Error('Failed to fetch order history');
            const data = await response.json();
            setHistory(data.history || []);
        } catch (error) {
            console.error('Failed to load history:', error);
            toast.error('발주 이력을 불러오는데 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    const loadStatistics = async () => {
        try {
            const response = await fetch(`${API_ENDPOINTS.orderStatistics}?month=${selectedMonth}`);
            if (!response.ok) throw new Error('Failed to fetch statistics');
            const data = await response.json();
            setStatistics(data);
        } catch (error) {
            console.error('Failed to load statistics:', error);
            toast.error('통계 데이터를 불러오는데 실패했습니다.');
        }
    };

    useEffect(() => {
        loadHistory();
        loadStatistics();
    }, [statusFilter, selectedMonth]);

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'executed':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                        <CheckCircle className="w-3 h-3" />
                        실행됨
                    </span>
                );
            case 'pending':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-semibold">
                        <Clock className="w-3 h-3" />
                        대기중
                    </span>
                );
            case 'cancelled':
                return (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-semibold">
                        <XCircle className="w-3 h-3" />
                        취소됨
                    </span>
                );
            default:
                return <span className="text-slate-500 text-xs">{status}</span>;
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                <span className="ml-2 text-slate-500">발주 이력 로딩 중...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">발주 이력</h2>
                    <p className="text-sm text-slate-500 mt-1">과거 발주 내역 및 통계를 확인하세요</p>
                </div>
                <div className="flex gap-2">
                    <select
                        value={selectedMonth}
                        onChange={(e) => setSelectedMonth(e.target.value)}
                        className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 bg-white font-medium"
                    >
                        {Array.from({ length: 6 }, (_, i) => {
                            const date = new Date();
                            date.setMonth(date.getMonth() - i);
                            const value = date.toISOString().slice(0, 7);
                            return (
                                <option key={value} value={value}>
                                    {date.getFullYear()}년 {date.getMonth() + 1}월
                                </option>
                            );
                        })}
                    </select>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 bg-white font-medium"
                    >
                        <option value="all">전체</option>
                        <option value="executed">실행됨</option>
                        <option value="pending">대기중</option>
                        <option value="cancelled">취소됨</option>
                    </select>
                </div>
            </div>

            {/* Statistics Cards */}
            {statistics && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-slate-600 font-medium">총 발주 건수</p>
                                <p className="text-3xl font-bold text-slate-900 mt-2">
                                    {statistics.summary.total_orders}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                                <Package className="w-6 h-6 text-blue-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-slate-600 font-medium">총 발주 금액</p>
                                <p className="text-3xl font-bold text-slate-900 mt-2">
                                    {(statistics.summary.total_cost / 10000).toFixed(0)}
                                    <span className="text-lg text-slate-600 ml-1">만원</span>
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-green-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-slate-600 font-medium">실행 완료</p>
                                <p className="text-3xl font-bold text-green-600 mt-2">
                                    {statistics.summary.executed_count}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                                <CheckCircle className="w-6 h-6 text-green-600" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-slate-600 font-medium">대기중</p>
                                <p className="text-3xl font-bold text-amber-600 mt-2">
                                    {statistics.summary.pending_count}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center">
                                <Clock className="w-6 h-6 text-amber-600" />
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Daily Chart - SIMPLE VERSION */}
            {statistics && statistics.daily_data.length > 0 && (
                <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-900 mb-6">일별 발주 금액</h3>
                    <div style={{ height: '250px', display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
                        {statistics.daily_data.map((day, index) => {
                            const maxCost = Math.max(...statistics.daily_data.map(d => d.cost));
                            const heightPercent = maxCost > 0 ? (day.cost / maxCost) * 100 : 0;

                            return (
                                <div key={index} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                                    <div style={{ width: '100%', height: '200px', position: 'relative', display: 'flex', alignItems: 'flex-end' }}>
                                        <div
                                            style={{
                                                width: '100%',
                                                height: `${heightPercent}%`,
                                                backgroundColor: '#3b82f6',
                                                borderRadius: '6px 6px 0 0',
                                                minHeight: day.cost > 0 ? '4px' : '0',
                                                position: 'relative',
                                                transition: 'all 0.3s'
                                            }}
                                            title={`${day.cost.toLocaleString()}원 (${day.count}건)`}
                                        >
                                            <div style={{
                                                position: 'absolute',
                                                top: '-30px',
                                                left: '50%',
                                                transform: 'translateX(-50%)',
                                                backgroundColor: '#1e293b',
                                                color: 'white',
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                fontSize: '11px',
                                                whiteSpace: 'nowrap',
                                                opacity: 0,
                                                pointerEvents: 'none'
                                            }}
                                                className="hover-tooltip">
                                                {day.cost.toLocaleString()}원
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#0f172a' }}>
                                            {new Date(day.date).getDate()}일
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* History Table */}
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
                <div className="p-4 border-b border-slate-200 bg-slate-50">
                    <h3 className="font-bold text-slate-900">발주 내역</h3>
                </div>

                {history.length === 0 ? (
                    <div className="p-12 text-center">
                        <Package className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-slate-900 mb-2">발주 이력이 없습니다</h3>
                        <p className="text-slate-500">조건을 변경하거나 새 발주를 생성해보세요.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">발주 ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">발주 날짜</th>
                                    <th className="px-6 py-3 text-right text-xs font-semibold text-slate-600 uppercase">품목 수</th>
                                    <th className="px-6 py-3 text-right text-xs font-semibold text-slate-600 uppercase">발주 금액</th>
                                    <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 uppercase">상태</th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase">실행 일시</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {history.map((order) => (
                                    <tr key={order.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <span className="font-bold text-blue-600">#{order.id}</span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-900 font-medium">
                                            {order.recommendation_date}
                                        </td>
                                        <td className="px-6 py-4 text-right text-slate-900 font-semibold">
                                            {order.total_items}개
                                        </td>
                                        <td className="px-6 py-4 text-right font-bold text-blue-600">
                                            {order.total_cost.toLocaleString()}원
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            {getStatusBadge(order.status)}
                                        </td>
                                        <td className="px-6 py-4 text-slate-600 text-sm">
                                            {order.executed_at || '-'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style>{`
        div:hover .hover-tooltip {
          opacity: 1 !important;
        }
      `}</style>
        </div>
    );
}
