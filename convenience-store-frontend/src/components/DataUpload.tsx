import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Download, Database, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

type UploadStatus = 'idle' | 'processing' | 'success' | 'error';
type UploadResult = {
  rows_processed: number;
  errors: string[];
  total_errors: number;
};

export function DataUpload() {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [fileName, setFileName] = useState<string>('');
  const [uploadType, setUploadType] = useState<'sales' | 'inventory'>('sales');
  const [result, setResult] = useState<UploadResult | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setUploadStatus('processing');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = uploadType === 'sales'
        ? `${API_BASE}/api/data/upload/sales`
        : `${API_BASE}/api/data/upload/inventory`;

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
        setUploadStatus('success');
      } else {
        setUploadStatus('error');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus('error');
    }
  };

  const resetUpload = () => {
    setUploadStatus('idle');
    setFileName('');
    setResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-6 text-white shadow-lg"
      >
        <h3 className="text-xl font-bold mb-2">데이터 업로드</h3>
        <p className="text-sm text-blue-100">
          판매 데이터나 재고 데이터를 CSV로 업로드하면 자동으로 MySQL과 RAG 벡터 스토어에 저장됩니다
        </p>
      </motion.div>

      {/* Upload Type Selection */}
      <div className="flex gap-4">
        <button
          onClick={() => setUploadType('sales')}
          className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${uploadType === 'sales'
              ? 'border-blue-600 bg-blue-50 text-blue-600'
              : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
            }`}
        >
          <TrendingUp className="w-5 h-5 mx-auto mb-1" />
          <p className="text-sm font-medium">판매 데이터</p>
        </button>
        <button
          onClick={() => setUploadType('inventory')}
          className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${uploadType === 'inventory'
              ? 'border-blue-600 bg-blue-50 text-blue-600'
              : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
            }`}
        >
          <Database className="w-5 h-5 mx-auto mb-1" />
          <p className="text-sm font-medium">재고 데이터</p>
        </button>
      </div>

      {/* Upload Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Box */}
        <div className="bg-white rounded-xl p-8 border-2 border-dashed border-slate-300 hover:border-blue-400 transition-colors">
          <AnimatePresence mode="wait">
            {uploadStatus === 'idle' && (
              <motion.label
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="cursor-pointer flex flex-col items-center justify-center h-64"
              >
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900 mb-2">CSV 파일 업로드</h4>
                <p className="text-sm text-slate-500 text-center mb-4">
                  {uploadType === 'sales' ? '판매 데이터' : '재고 데이터'} CSV 파일을 선택하세요
                </p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg text-sm shadow-lg">
                  파일 선택
                </div>
              </motion.label>
            )}

            {uploadStatus === 'processing' && (
              <motion.div
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-64"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4"
                >
                  <FileText className="w-8 h-8 text-blue-600" />
                </motion.div>
                <h4 className="text-lg font-bold text-slate-900 mb-2">업로드 중...</h4>
                <p className="text-sm text-slate-500">{fileName}</p>
              </motion.div>
            )}

            {uploadStatus === 'success' && result && (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center h-64"
              >
                <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900 mb-2">업로드 완료!</h4>
                <div className="text-center mb-4">
                  <p className="text-sm text-slate-600">{fileName}</p>
                  <p className="text-lg font-bold text-blue-600 mt-2">{result.rows_processed}개 레코드 처리</p>
                  {result.total_errors > 0 && (
                    <p className="text-sm text-amber-600 mt-1">{result.total_errors}개 오류</p>
                  )}
                </div>
                <button
                  onClick={resetUpload}
                  className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-all"
                >
                  다른 파일 업로드
                </button>
              </motion.div>
            )}

            {uploadStatus === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-64"
              >
                <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mb-4">
                  <AlertCircle className="w-8 h-8 text-red-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900 mb-2">업로드 실패</h4>
                <p className="text-sm text-slate-500 mb-4">파일 형식을 확인해주세요</p>
                <button
                  onClick={resetUpload}
                  className="px-6 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200"
                >
                  다시 시도
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Instructions */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
            <h4 className="text-lg font-bold text-slate-900 mb-4">
              {uploadType === 'sales' ? '판매 데이터' : '재고 데이터'} CSV 형식
            </h4>
            <div className="space-y-3 text-sm">
              {uploadType === 'sales' ? (
                <>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">1</div>
                    <div>
                      <p className="font-medium text-slate-900">product_name</p>
                      <p className="text-xs text-slate-500">상품명 (예: 삼각김밥)</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">2</div>
                    <div>
                      <p className="font-medium text-slate-900">quantity_sold</p>
                      <p className="text-xs text-slate-500">판매 수량 (숫자)</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">3</div>
                    <div>
                      <p className="font-medium text-slate-900">sale_price</p>
                      <p className="text-xs text-slate-500">판매 가격 (숫자)</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">4</div>
                    <div>
                      <p className="font-medium text-slate-900">sale_date</p>
                      <p className="text-xs text-slate-500">판매 날짜 (YYYY-MM-DD)</p>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">1</div>
                    <div>
                      <p className="font-medium text-slate-900">product_name</p>
                      <p className="text-xs text-slate-500">상품명</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">2</div>
                    <div>
                      <p className="font-medium text-slate-900">category</p>
                      <p className="text-xs text-slate-500">카테고리</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">3</div>
                    <div>
                      <p className="font-medium text-slate-900">quantity</p>
                      <p className="text-xs text-slate-500">재고 수량</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs">4</div>
                    <div>
                      <p className="font-medium text-slate-900">unit_price</p>
                      <p className="text-xs text-slate-500">단가</p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Database className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900 mb-1">자동 처리</p>
                <p className="text-xs text-blue-700">
                  업로드된 데이터는 MySQL 데이터베이스와 ChromaDB 벡터 스토어에 자동으로 저장되어
                  AI 분석에 즉시 활용됩니다.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Details */}
      {uploadStatus === 'success' && result && result.errors.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-amber-50 border border-amber-200 rounded-xl p-6"
        >
          <h4 className="text-lg font-bold text-amber-900 mb-3">처리 중 발생한 오류</h4>
          <div className="space-y-2">
            {result.errors.map((error, index) => (
              <p key={index} className="text-sm text-amber-700">• {error}</p>
            ))}
            {result.total_errors > result.errors.length && (
              <p className="text-sm text-amber-600 mt-2">
                외 {result.total_errors - result.errors.length}개 오류...
              </p>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}