import { useState } from 'react';
import { motion } from 'framer-motion';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Dashboard } from './components/Dashboard';
import { ChatInterface } from './components/ChatInterface';
import { OrderRecommendations } from './components/OrderRecommendations';
import { OrderHistory } from './components/OrderHistory';
import { LayoutDashboard, MessageSquare, ShoppingCart, History } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

type Tab = 'dashboard' | 'chat' | 'orders' | 'history';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  const tabs = [
    { id: 'dashboard' as Tab, label: '대시보드', icon: LayoutDashboard },
    { id: 'chat' as Tab, label: 'AI 챗봇', icon: MessageSquare },
    { id: 'orders' as Tab, label: '발주 추천', icon: ShoppingCart },
    { id: 'history' as Tab, label: '발주 이력', icon: History },
  ];

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />

        {/* Header */}
        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-white border-b border-slate-200 shadow-sm"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <motion.div
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.5 }}
                  className="w-10 h-10 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-200"
                >
                  <ShoppingCart className="w-6 h-6 text-white" />
                </motion.div>
                <div>
                  <h1 className="text-slate-900">편의점 AI 자동 발주 시스템</h1>
                  <p className="text-xs text-slate-500">Intelligent Order Management</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="px-3 py-1 bg-green-50 border border-green-200 rounded-full"
                >
                  <span className="text-xs text-green-700">● 시스템 정상</span>
                </motion.div>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Navigation */}
        <nav className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex gap-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <motion.button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors relative ${activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                      }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{tab.label}</span>
                    {activeTab === tab.id && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600"
                      />
                    )}
                  </motion.button>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <motion.main
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        >
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'orders' && <OrderRecommendations />}
          {activeTab === 'history' && <OrderHistory />}
        </motion.main>
      </div>
    </QueryClientProvider>
  );
}