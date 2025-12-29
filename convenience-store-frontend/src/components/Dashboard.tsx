import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Package, AlertTriangle, Zap, Cloud, Calendar } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { API_ENDPOINTS } from '../config';
import { LoadingSkeleton } from './LoadingSkeleton';

interface Stats {
  today_sales: number;
  sales_change: number;
  pending_orders: number;
  low_stock_items: number;
  processing_speed: number;
}

interface SalesData {
  date: string;
  sales: number;
  orders: number;
}

interface Product {
  name: string;
  sales: number;
  trend: number;
  stock: number;
}

interface Category {
  name: string;
  value: number;
  color: string;
}

export function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    today_sales: 0,
    sales_change: 0,
    pending_orders: 0,
    low_stock_items: 0,
    processing_speed: 1.2
  });
  const [salesData, setSalesData] = useState<SalesData[]>([]);
  const [topProducts, setTopProducts] = useState<Product[]>([]);
  const [categoryData, setCategoryData] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch stats
        const statsRes = await fetch(API_ENDPOINTS.stats);
        if (!statsRes.ok) throw new Error('Failed to fetch stats');
        const statsData = await statsRes.json();
        setStats(statsData);

        // Fetch sales data (last 7 days)
        const salesRes = await fetch(`${API_ENDPOINTS.salesData}?days=7`);
        if (!salesRes.ok) throw new Error('Failed to fetch sales data');
        const salesData = await salesRes.json();
        setSalesData(salesData.data || []);

        // Fetch top products
        const productsRes = await fetch(`${API_ENDPOINTS.products}?limit=5`);
        if (!productsRes.ok) throw new Error('Failed to fetch products');
        const productsData = await productsRes.json();
        setTopProducts(productsData.products || []);

        // Fetch categories
        const categoriesRes = await fetch(API_ENDPOINTS.categories);
        if (!categoriesRes.ok) throw new Error('Failed to fetch categories');
        const categoriesData = await categoriesRes.json();
        setCategoryData(categoriesData.data || []);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        toast.error('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // 30초마다 자동 새로고침
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-500">데이터 로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: "오늘 매출",
            value: `${stats.today_sales.toLocaleString()}원`,
            change: `${stats.sales_change >= 0 ? '+' : ''}${stats.sales_change}%`,
            trend: stats.sales_change >= 0 ? "up" : "down",
            icon: TrendingUp,
            color: "blue"
          },
          {
            title: "발주 대기",
            value: `${stats.pending_orders}건`,
            change: "",
            trend: "up",
            icon: Package,
            color: "cyan"
          },
          {
            title: "재고 부족 알림",
            value: `${stats.low_stock_items}개 상품`,
            change: "",
            trend: "up",
            icon: AlertTriangle,
            color: "amber"
          },
          {
            title: "AI 처리 속도",
            value: `${stats.processing_speed}초`,
            change: "",
            trend: "down",
            icon: Zap,
            color: "purple"
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <StatCard {...stat} />
          </motion.div>
        ))}
      </div>

      {/* External Data Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            icon: Cloud,
            label: "오늘 날씨",
            value: `${['맑음', '흐림', '비'][Math.floor(Math.random() * 3)]}, ${Math.floor(Math.random() * 10) + 10}°C`,
            color: "blue",
            demo: true
          },
          {
            icon: Calendar,
            label: "내일 예정",
            value: new Date(Date.now() + 86400000).getDay() === 0 || new Date(Date.now() + 86400000).getDay() === 6 ? "주말 (영업시간 변경)" : "평일 (정상 영업)",
            color: "purple",
            demo: false
          },
          {
            icon: TrendingUp,
            label: "상권 지수",
            value: `${['높음', '보통', '낮음'][Math.floor(Math.random() * 3)]} (${Math.floor(Math.random() * 20) + 80}/100)`,
            color: "green",
            demo: true
          }
        ].map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 + index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
            className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer relative"
          >
            {item.demo && (
              <span className="absolute top-2 right-2 text-[10px] px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full font-medium">
                데모
              </span>
            )}
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 bg-${item.color}-50 rounded-lg flex items-center justify-center`}>
                <item.icon className={`w-5 h-5 text-${item.color}-600`} />
              </div>
              <div>
                <p className="text-xs text-slate-500">{item.label}</p>
                <p className="text-slate-900 font-medium">{item.value}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Trend */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          whileHover={{ y: -5 }}
          className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all"
        >
          <h3 className="text-slate-900 mb-4">주간 매출 추이</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={salesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Line
                type="monotone"
                dataKey="sales"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Category Distribution */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.7 }}
          whileHover={{ y: -5 }}
          className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all"
        >
          <h3 className="text-slate-900 mb-4">카테고리별 매출</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Top Products */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        whileHover={{ y: -5 }}
        className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all"
      >
        <h3 className="text-slate-900 mb-4">인기 상품 TOP 5</h3>
        <div className="space-y-3">
          {topProducts.map((product, index) => (
            <motion.div
              key={product.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 + index * 0.1 }}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-slate-300">#{index + 1}</span>
                <div>
                  <p className="font-medium text-slate-900">{product.name}</p>
                  <p className="text-sm text-slate-500">판매량: {product.sales}개</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`flex items-center gap-1 ${product.trend >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                  {product.trend >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="font-medium">{Math.abs(product.trend)}%</span>
                </div>
                <p className="text-xs text-slate-500">재고: {product.stock}개</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ElementType;
  color: 'blue' | 'cyan' | 'amber' | 'purple';
}

function StatCard({ title, value, change, trend, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    cyan: 'bg-cyan-50 text-cyan-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600'
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm hover:shadow-lg transition-all cursor-pointer">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {change && (
            <div className={`flex items-center gap-1 mt-2 ${trend === 'up' ? 'text-emerald-600' : 'text-blue-600'}`}>
              {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span className="text-sm font-medium">{change}</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}