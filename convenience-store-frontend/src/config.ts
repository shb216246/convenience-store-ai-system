export const config = {
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    appName: import.meta.env.VITE_APP_NAME || '편의점 AI 자동 발주 시스템',
} as const;

export const API_ENDPOINTS = {
    // Dashboard
    stats: `${config.apiUrl}/api/stats/summary`,
    salesData: `${config.apiUrl}/api/stats/sales/trend`,
    products: `${config.apiUrl}/api/stats/products/top`,
    categories: `${config.apiUrl}/api/stats/category/distribution`,

    // Chat
    chat: `${config.apiUrl}/api/chat`,

    // Orders
    orders: `${config.apiUrl}/api/recommendations`,
    ordersPending: `${config.apiUrl}/api/orders/pending`,
    orderHistory: `${config.apiUrl}/api/orders/history`,
    orderStatistics: `${config.apiUrl}/api/orders/statistics`,
} as const;
