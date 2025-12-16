import React, { useEffect, useState } from 'react';
import { Eye, MousePointer, Clock, TrendingUp, Users, Target } from 'lucide-react';

interface AnalyticsData {
  pageViews: number;
  uniqueVisitors: number;
  avgSessionDuration: number;
  bounceRate: number;
  conversionRate: number;
  topPages: Array<{ path: string; views: number; change: number }>;
  userFlow: Array<{ step: string; users: number; conversion: number }>;
  deviceBreakdown: Array<{ device: string; percentage: number; color: string }>;
}

const AnalyticsTracker: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    pageViews: 1247,
    uniqueVisitors: 892,
    avgSessionDuration: 184,
    bounceRate: 32.4,
    conversionRate: 4.7,
    topPages: [
      { path: '/', views: 892, change: 12.5 },
      { path: '/assessment', views: 234, change: 8.3 },
      { path: '/pricing', views: 156, change: -2.1 },
      { path: '/about', views: 98, change: 15.7 },
      { path: '/contact', views: 67, change: 5.2 }
    ],
    userFlow: [
      { step: 'Landing Page', users: 1000, conversion: 100 },
      { step: 'Assessment Start', users: 247, conversion: 24.7 },
      { step: 'Assessment Complete', users: 189, conversion: 18.9 },
      { step: 'Sign Up', users: 67, conversion: 6.7 },
      { step: 'Payment', users: 23, conversion: 2.3 }
    ],
    deviceBreakdown: [
      { device: 'Desktop', percentage: 58.3, color: 'bg-blue-500' },
      { device: 'Mobile', percentage: 32.1, color: 'bg-green-500' },
      { device: 'Tablet', percentage: 9.6, color: 'bg-purple-500' }
    ]
  });

  const [isVisible, setIsVisible] = useState(false);

  // Simulate real-time analytics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setAnalyticsData(prev => ({
        ...prev,
        pageViews: prev.pageViews + Math.floor(Math.random() * 5),
        uniqueVisitors: prev.uniqueVisitors + Math.floor(Math.random() * 3),
        avgSessionDuration: Math.max(120, Math.min(300, prev.avgSessionDuration + (Math.random() - 0.5) * 10)),
        bounceRate: Math.max(20, Math.min(50, prev.bounceRate + (Math.random() - 0.5) * 2)),
        conversionRate: Math.max(2, Math.min(8, prev.conversionRate + (Math.random() - 0.5) * 0.5))
      }));
    }, 3000);

    // Show analytics after 2 seconds
    const showTimer = setTimeout(() => setIsVisible(true), 2000);

    return () => {
      clearInterval(interval);
      clearTimeout(showTimer);
    };
  }, []);

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="font-semibold text-gray-900">Live Analytics</span>
          </div>
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Eye className="w-4 h-4 text-blue-600 mr-1" />
              <span className="text-xs text-gray-600">Views</span>
            </div>
            <div className="text-lg font-bold text-gray-900">{analyticsData.pageViews.toLocaleString()}</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Users className="w-4 h-4 text-green-600 mr-1" />
              <span className="text-xs text-gray-600">Visitors</span>
            </div>
            <div className="text-lg font-bold text-gray-900">{analyticsData.uniqueVisitors.toLocaleString()}</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Clock className="w-4 h-4 text-purple-600 mr-1" />
              <span className="text-xs text-gray-600">Avg Time</span>
            </div>
            <div className="text-lg font-bold text-gray-900">{formatDuration(analyticsData.avgSessionDuration)}</div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Target className="w-4 h-4 text-orange-600 mr-1" />
              <span className="text-xs text-gray-600">Conversion</span>
            </div>
            <div className="text-lg font-bold text-gray-900">{formatPercentage(analyticsData.conversionRate)}</div>
          </div>
        </div>

        {/* Device Breakdown */}
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Device Breakdown</div>
          <div className="space-y-2">
            {analyticsData.deviceBreakdown.map((device, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{device.device}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${device.color}`}
                      style={{ width: `${device.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {formatPercentage(device.percentage)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Pages */}
        <div className="border-t border-gray-200 pt-3">
          <div className="text-sm font-medium text-gray-700 mb-2">Top Pages</div>
          <div className="space-y-1">
            {analyticsData.topPages.slice(0, 3).map((page, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-gray-600 truncate flex-1">{page.path}</span>
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">{page.views}</span>
                  <span className={`text-xs ${page.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {page.change >= 0 ? '+' : ''}{page.change}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 pt-3 mt-3">
          <div className="text-xs text-gray-500 text-center">
            Real-time data • Updates every 3s
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsTracker;