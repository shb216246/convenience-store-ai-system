import { useState, useEffect } from 'react';
import { TrendingUp, Package, Minus, Plus, ChevronDown, ChevronUp, ShoppingCart, AlertCircle, Loader2, RefreshCw, Sparkles, DollarSign } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { API_ENDPOINTS } from '../config';
import { LoadingSkeleton } from './LoadingSkeleton';

type OrderItem = {
  id: number;
  product_name: string;
  current_stock: number;
  safe_stock: number;
  order_quantity: number;
  unit_price: number;
  total_cost: number;
  reason: string;
  priority: string;
};

type OrderRecommendation = {
  id: number;
  recommendation_date: string;
  total_items: number;
  total_cost: number;
  created_at: string;
  status: string;
};

export function OrderRecommendations() {
  const [orders, setOrders] = useState<OrderRecommendation[]>([]);
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isItemsLoading, setIsItemsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());
  const [hasChanges, setHasChanges] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);

  // 발주 대기 목록 로드
  const loadOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.ordersPending);
      if (!response.ok) throw new Error('Failed to fetch orders');
      const data = await response.json();
      setOrders(data.orders || []);
    } catch (error) {
      console.error('Failed to load orders:', error);
      toast.error('발주 추천 데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 발주 품목 로드
  const loadOrderItems = async (orderId: number) => {
    setIsItemsLoading(true);
    setSelectedOrderId(orderId);
    setHasChanges(false);
    try {
      const response = await fetch(`http://localhost:8000/api/recommendations/${orderId}/items`);
      const data = await response.json();
      setOrderItems(data.items || []);
    } catch (error) {
      console.error('발주 품목 로드 실패:', error);
      setOrderItems([]);
    } finally {
      setIsItemsLoading(false);
    }
  };

  // 수량 업데이트 (로컬)
  const updateQuantity = (itemId: number, newQuantity: number) => {
    if (newQuantity < 0) return;

    setOrderItems(prev => prev.map(item => {
      if (item.id === itemId) {
        const newTotalCost = item.unit_price * newQuantity;
        return { ...item, order_quantity: newQuantity, total_cost: newTotalCost };
      }
      return item;
    }));
    setHasChanges(true);
  };

  // 수량 저장 (서버)
  const saveQuantityChanges = async () => {
    if (!selectedOrderId) return;

    try {
      for (const item of orderItems) {
        await fetch(`http://localhost:8000/api/recommendations/${selectedOrderId}/items/${item.id}?quantity=${item.order_quantity}`, {
          method: 'PUT',
        });
      }

      alert('수량이 저장되었습니다!');
      setHasChanges(false);
      await loadOrders();
      await loadOrderItems(selectedOrderId);
    } catch (error) {
      console.error('수량 저장 실패:', error);
      alert('수량 저장에 실패했습니다.');
    }
  };

  // 새 발주 추천 생성
  const generateNewRecommendation = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('http://localhost:8000/api/scheduler/run-now', {
        method: 'POST',
      });

      if (response.ok) {
        alert('발주 추천이 생성되었습니다!');
        await loadOrders();
      }
    } catch (error) {
      console.error('발주 추천 생성 실패:', error);
      alert('발주 추천 생성에 실패했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  // 발주 실행
  const executeOrder = async () => {
    if (!selectedOrderId) return;

    try {
      const response = await fetch(`${API_ENDPOINTS.orders}/${selectedOrderId}/execute`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to execute order');

      const data = await response.json();
      toast.success(`발주 #${selectedOrderId}가 성공적으로 실행되었습니다!`);
      setShowExecuteModal(false);
      loadOrders(); // Reload orders
    } catch (error) {
      console.error('Failed to execute order:', error);
      toast.error('발주 실행에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 발주 실행 버튼 클릭
  const handleExecuteClick = () => {
    if (hasChanges) {
      alert('변경 사항을 먼저 저장해주세요!');
      return;
    }
    setShowExecuteModal(true);
  };

  // 상세 정보 토글
  const toggleItemDetail = (itemId: number) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  useEffect(() => {
    loadOrders();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-slate-500">발주 대기 목록 로딩 중...</span>
      </div>
    );
  }

  const selectedOrder = orders.find(o => o.id === selectedOrderId);
  const totalCost = orderItems.reduce((sum, item) => sum + item.total_cost, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">발주 관리</h2>
          <p className="text-sm text-slate-500 mt-1">AI 추천 발주 목록을 확인하고 실행하세요</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadOrders}
            className="px-4 py-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>
          <button
            onClick={generateNewRecommendation}
            disabled={isGenerating}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                생성 중...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                새 발주 추천 생성
              </>
            )}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">발주 대기</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{orders.length}</p>
            </div>
            <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">총 발주 금액</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">
                {orders.reduce((sum, o) => sum + o.total_cost, 0).toLocaleString()}원
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">총 품목 수</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">
                {orders.reduce((sum, o) => sum + o.total_items, 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-emerald-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Orders List */}
      {orders.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center">
          <AlertCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">발주 대기 중인 항목이 없습니다</h3>
          <p className="text-slate-500 mb-6">새 발주 추천을 생성하거나 내일 아침 6시 자동 생성을 기다려주세요.</p>
          <button
            onClick={generateNewRecommendation}
            disabled={isGenerating}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            발주 추천 생성하기
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 발주 목록 */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50">
              <h3 className="font-semibold text-slate-900">발주 추천 목록</h3>
            </div>
            <div className="divide-y divide-slate-200">
              {orders.map((order) => (
                <button
                  key={order.id}
                  onClick={() => loadOrderItems(order.id)}
                  className={`w-full p-4 text-left hover:bg-slate-50 transition-colors ${selectedOrderId === order.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                    }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-slate-900">{order.id}번 발주</span>
                    <span className="text-xs text-slate-500">{order.recommendation_date}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-slate-900 font-semibold">{order.total_items}개 품목</span>
                    <span className="font-semibold text-blue-600">{order.total_cost.toLocaleString()}원</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 발주 품목 테이블 */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">
                {selectedOrder ? `${selectedOrder.id}번 발주 상세` : '발주 품목'}
              </h3>
              {selectedOrder && (
                <div className="flex gap-2">
                  {hasChanges && (
                    <button
                      onClick={saveQuantityChanges}
                      className="px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition-colors"
                    >
                      💾 변경사항 저장
                    </button>
                  )}
                  <button
                    onClick={handleExecuteClick}
                    disabled={hasChanges}
                    className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-base font-bold rounded-lg hover:from-blue-700 hover:to-blue-800 shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <ShoppingCart className="w-5 h-5" />
                    발주 실행
                  </button>
                </div>
              )}
            </div>

            {isItemsLoading ? (
              <div className="p-12 text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-sm text-slate-500">품목 로딩 중...</p>
              </div>
            ) : orderItems.length === 0 ? (
              <div className="p-12 text-center">
                <Package className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-500">발주 추천을 선택하세요</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50 text-xs text-slate-500 uppercase">
                    <tr>
                      <th className="px-4 py-3 text-left">상품</th>
                      <th className="px-4 py-3 text-right">재고</th>
                      <th className="px-4 py-3 text-right">발주 수량</th>
                      <th className="px-4 py-3 text-right">단가</th>
                      <th className="px-4 py-3 text-right">합계</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-sm">
                    {orderItems.map((item, index) => (
                      <motion.tr
                        key={item.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="hover:bg-slate-50"
                      >
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium text-slate-900">{item.product_name}</div>
                            <button
                              onClick={() => toggleItemDetail(item.id)}
                              className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 mt-1"
                            >
                              {expandedItems.has(item.id) ? (
                                <>
                                  <ChevronUp className="w-3 h-3" />
                                  상세 숨기기
                                </>
                              ) : (
                                <>
                                  <ChevronDown className="w-3 h-3" />
                                  발주 근거 보기
                                </>
                              )}
                            </button>
                            {expandedItems.has(item.id) && (
                              <div className="mt-3 p-4 bg-gradient-to-br from-blue-50 to-slate-50 rounded-lg text-xs space-y-2 border border-blue-100">
                                <div className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                  <AlertCircle className="w-4 h-4" />
                                  발주 분석 상세
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                  <div className="bg-white p-2 rounded">
                                    <span className="text-slate-500">현재 재고</span>
                                    <div className={`text-base font-bold ${item.current_stock === 0 ? 'text-red-600' : 'text-slate-900'}`}>
                                      {item.current_stock}개
                                    </div>
                                  </div>
                                  <div className="bg-white p-2 rounded">
                                    <span className="text-slate-500">안전 재고</span>
                                    <div className="text-base font-bold text-slate-900">{item.safe_stock}개</div>
                                  </div>
                                </div>
                                <div className="bg-white p-2 rounded">
                                  <span className="text-slate-500">발주 이유</span>
                                  <div className="font-medium text-slate-900 mt-1">{item.reason}</div>
                                </div>
                                <div className="bg-white p-2 rounded">
                                  <span className="text-slate-500">우선순위</span>
                                  <div className={`inline-flex items-center gap-1 mt-1 px-2 py-1 rounded-full text-xs font-bold ${item.priority === 'high' ? 'bg-red-100 text-red-700' :
                                    item.priority === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                                    }`}>
                                    {item.priority === 'high' ? '🔴 높음' : item.priority === 'medium' ? '🟡 중간' : '🟢 낮음'}
                                  </div>
                                </div>
                                <div className="bg-white p-2 rounded">
                                  <span className="text-slate-500">재고 부족량</span>
                                  <div className="text-base font-bold text-red-600">
                                    {Math.max(0, item.safe_stock - item.current_stock)}개 부족
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className={item.current_stock === 0 ? 'text-red-600 font-semibold' : 'text-slate-600'}>
                            {item.current_stock}
                          </span>
                          <span className="text-slate-400">/{item.safe_stock}</span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => updateQuantity(item.id, Math.max(0, item.order_quantity - 1))}
                              className="w-7 h-7 flex items-center justify-center bg-slate-100 hover:bg-slate-200 rounded text-slate-700 transition-colors"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <input
                              type="number"
                              value={item.order_quantity}
                              onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 0)}
                              className="w-16 px-2 py-1 text-center border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-blue-600"
                              min="0"
                            />
                            <button
                              onClick={() => updateQuantity(item.id, item.order_quantity + 1)}
                              className="w-7 h-7 flex items-center justify-center bg-slate-100 hover:bg-slate-200 rounded text-slate-700 transition-colors"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                            <span className="ml-1 text-slate-500">개</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-600">
                          {item.unit_price.toLocaleString()}원
                        </td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">
                          {item.total_cost.toLocaleString()}원
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-slate-50 font-semibold">
                    <tr>
                      <td className="px-4 py-3" colSpan={4}>총 {orderItems.length}개 품목</td>
                      <td className="px-4 py-3 text-right text-blue-600">
                        {totalCost.toLocaleString()}원
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Execute Confirmation Modal */}
      <AnimatePresence>
        {showExecuteModal && selectedOrder && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowExecuteModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
            >
              {/* Header */}
              <div className="p-6" style={{ background: 'linear-gradient(to right, #2563eb, #1d4ed8)' }}>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}>
                    <ShoppingCart className="w-6 h-6" style={{ color: 'white' }} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold" style={{ color: 'white' }}>발주 실행 확인</h3>
                    <p className="text-sm" style={{ color: 'white', opacity: 0.9 }}>최종 확인 후 실행됩니다</p>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 space-y-4">
                <div className="bg-slate-50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600">발주 번호</span>
                    <span className="font-bold text-slate-900">#{selectedOrder.id}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-600">품목 수</span>
                    <span className="font-bold text-slate-900">{orderItems.length}개</span>
                  </div>
                  <div className="flex items-center justify-between border-t border-slate-200 pt-3">
                    <span className="text-slate-600 flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      총 발주 금액
                    </span>
                    <span className="text-2xl font-bold text-blue-600">{totalCost.toLocaleString()}원</span>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-amber-800">
                      <p className="font-semibold mb-1">발주 실행 시 다음 작업이 수행됩니다:</p>
                      <ul className="list-disc list-inside space-y-1 text-xs">
                        <li>재고가 자동으로 업데이트됩니다</li>
                        <li>발주 기록이 저장됩니다</li>
                        <li>실행 후에는 취소할 수 없습니다</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <p className="text-center text-slate-600 font-medium">
                  정말 발주를 실행하시겠습니까?
                </p>
              </div>

              {/* Actions */}
              <div className="p-6 bg-slate-50 flex gap-3">
                <button
                  onClick={() => setShowExecuteModal(false)}
                  className="flex-1 px-4 py-3 bg-white border-2 border-slate-300 text-slate-900 rounded-lg hover:bg-slate-100 font-bold transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={executeOrder}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 font-bold shadow-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                >
                  <ShoppingCart className="w-5 h-5" />
                  발주 실행
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}