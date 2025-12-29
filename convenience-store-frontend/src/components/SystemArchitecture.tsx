import { Database, Brain, Cloud, Smartphone, ArrowRight, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export function SystemArchitecture() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white shadow-lg"
      >
        <h3 className="mb-2">시스템 아키텍처</h3>
        <p className="text-sm text-purple-100">
          편의점 AI 자동 발주 시스템의 전체 구조와 데이터 흐름을 확인하세요
        </p>
      </motion.div>

      {/* Architecture Diagram */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm"
      >
        <div className="space-y-8">
          {/* Step 1: POS System */}
          <div className="flex flex-col items-center">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="w-full max-w-md bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl p-6 border-2 border-slate-300 shadow-lg hover:shadow-xl transition-all cursor-pointer"
            >
              <div className="flex items-center gap-3 mb-3">
                <motion.div 
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  className="w-10 h-10 bg-slate-300 rounded-lg flex items-center justify-center"
                >
                  <Database className="w-6 h-6 text-slate-700" />
                </motion.div>
                <h4 className="text-slate-900">POS 시스템</h4>
              </div>
              <p className="text-sm text-slate-600 mb-2">수동 CSV 추출</p>
              <div className="bg-white rounded-lg p-3 text-xs text-slate-600 font-mono">
                상품명, 판매수량, 날짜, 재고
              </div>
            </motion.div>
            <div className="my-4">
              <ArrowDownIcon />
            </div>
          </div>

          {/* Step 2: CSV Upload */}
          <div className="flex flex-col items-center">
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
              whileHover={{ scale: 1.1 }}
              className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg"
            >
              <span className="text-sm text-blue-700">CSV 업로드</span>
            </motion.div>
            <div className="my-4">
              <ArrowDownIcon />
            </div>
          </div>

          {/* Step 3: AI System */}
          <div className="flex flex-col items-center">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              whileHover={{ scale: 1.02, y: -5 }}
              className="w-full bg-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl p-6 border-2 border-blue-700 shadow-xl hover:shadow-2xl transition-all"
            >
              <div className="flex items-center gap-3 mb-4">
                <motion.div 
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 bg-white rounded-lg flex items-center justify-center"
                >
                  <Brain className="w-6 h-6 text-blue-600" />
                </motion.div>
                <h4 className="text-white">우리 AI 시스템</h4>
              </div>

              <div className="space-y-4">
                {/* Vector DB */}
                <motion.div 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.9 }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white bg-opacity-20 backdrop-blur rounded-xl p-4 border border-white border-opacity-30 hover:bg-opacity-30 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="w-5 h-5 text-white" />
                    <h5 className="text-white">Vector DB (RAG)</h5>
                  </div>
                  <p className="text-xs text-blue-100">
                    과거 판매 데이터 임베딩 저장
                  </p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    <motion.span 
                      whileHover={{ scale: 1.1 }}
                      className="px-2 py-1 bg-blue-500 bg-opacity-50 text-white text-xs rounded"
                    >
                      판매 패턴
                    </motion.span>
                    <motion.span 
                      whileHover={{ scale: 1.1 }}
                      className="px-2 py-1 bg-blue-500 bg-opacity-50 text-white text-xs rounded"
                    >
                      시계열 데이터
                    </motion.span>
                  </div>
                </motion.div>

                {/* LLM Agent */}
                <motion.div 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.0 }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white bg-opacity-20 backdrop-blur rounded-xl p-4 border border-white border-opacity-30 hover:bg-opacity-30 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <Zap className="w-5 h-5 text-white" />
                    </motion.div>
                    <h5 className="text-white">LLM Agent</h5>
                  </div>
                  <p className="text-xs text-blue-100 mb-2">GPT-4, Claude 기반</p>
                  <div className="space-y-1 text-xs text-white">
                    {['데이터 분석', '발주 추천', '자연어 대화'].map((item, index) => (
                      <motion.div 
                        key={item}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.1 + index * 0.1 }}
                        className="flex items-center gap-2"
                      >
                        <div className="w-1.5 h-1.5 bg-white rounded-full" />
                        {item}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>

                {/* External APIs */}
                <motion.div 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.1 }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white bg-opacity-20 backdrop-blur rounded-xl p-4 border border-white border-opacity-30 hover:bg-opacity-30 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Cloud className="w-5 h-5 text-white" />
                    <h5 className="text-white">External APIs</h5>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-2">
                    {['날씨 (무료)', '공휴일 (무료)', '상권 분석'].map((api, index) => (
                      <motion.div
                        key={api}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 1.2 + index * 0.1 }}
                        whileHover={{ scale: 1.1 }}
                        className="bg-cyan-500 bg-opacity-50 text-white text-xs rounded px-2 py-1 text-center"
                      >
                        {api}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              </div>
            </motion.div>
            <div className="my-4">
              <ArrowDownIcon />
            </div>
          </div>

          {/* Step 4: Web Interface */}
          <div className="flex flex-col items-center">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="w-full max-w-md bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl p-6 border-2 border-purple-300 shadow-lg hover:shadow-xl transition-all cursor-pointer"
            >
              <div className="flex items-center gap-3 mb-3">
                <motion.div 
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  className="w-10 h-10 bg-purple-300 rounded-lg flex items-center justify-center"
                >
                  <Smartphone className="w-6 h-6 text-purple-700" />
                </motion.div>
                <h4 className="text-slate-900">웹/앱 인터페이스</h4>
              </div>
              <div className="space-y-2">
                {[
                  { label: '챗봇 (자연어)', emoji: '💬' },
                  { label: '발주 승인', emoji: '✓' },
                  { label: '대시보드', emoji: '📊' }
                ].map((item, index) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.6 + index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="bg-white rounded-lg p-3 flex items-center justify-between"
                  >
                    <span className="text-sm text-slate-700">{item.label}</span>
                    <span className="text-xs text-slate-500">{item.emoji}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          { icon: Brain, title: "RAG 기반 분석", description: "Vector DB에 저장된 과거 데이터를 활용하여 유사한 판매 패턴을 찾아 정확한 예측을 수행합니다", color: "blue" },
          { icon: Zap, title: "LLM 에이전트", description: "GPT-4와 Claude를 활용하여 복잡한 데이터를 분석하고 자연어로 대화하며 최적의 발주를 추천합니다", color: "purple" },
          { icon: Cloud, title: "외부 데이터 통합", description: "날씨, 공휴일, 상권 분석 등 외부 API 데이터를 실시간으로 수집하여 더 정확한 예측을 제공합니다", color: "cyan" },
          { icon: Smartphone, title: "직관적 인터페이스", description: "복잡한 AI 시스템을 누구나 쉽게 사용할 수 있도록 설계된 사용자 친화적 인터페이스를 제공합니다", color: "pink" }
        ].map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8 + index * 0.1 }}
          >
            <FeatureCard {...feature} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function ArrowDownIcon() {
  return (
    <motion.div 
      animate={{ y: [0, 5, 0] }}
      transition={{ duration: 1.5, repeat: Infinity }}
      className="flex flex-col items-center"
    >
      <div className="w-0.5 h-8 bg-slate-300" />
      <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent border-t-slate-300" />
    </motion.div>
  );
}

type FeatureCardProps = {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  color: 'blue' | 'purple' | 'cyan' | 'pink';
};

function FeatureCard({ icon: Icon, title, description, color }: FeatureCardProps) {
  const colorClasses = {
    blue: 'from-blue-600 to-blue-700',
    purple: 'from-purple-600 to-purple-700',
    cyan: 'from-cyan-600 to-cyan-700',
    pink: 'from-pink-600 to-pink-700',
  };

  return (
    <motion.div 
      whileHover={{ scale: 1.05, y: -5 }}
      className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all cursor-pointer"
    >
      <motion.div 
        whileHover={{ rotate: 360 }}
        transition={{ duration: 0.5 }}
        className={`w-12 h-12 bg-gradient-to-br ${colorClasses[color]} rounded-xl flex items-center justify-center mb-4 shadow-lg`}
      >
        <Icon className="w-6 h-6 text-white" />
      </motion.div>
      <h4 className="text-slate-900 mb-2">{title}</h4>
      <p className="text-sm text-slate-600">{description}</p>
    </motion.div>
  );
}