import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Target, Eye, CheckCircle, AlertTriangle, RefreshCw, ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface AnalyticsOverviewProps {
  analytics: {
    totalLeads: number;
    campaignsActive: number;
    engagementRate: number;
    conversionRate: number;
    pageViews?: number;
    assessmentsStarted?: number;
    assessmentsCompleted?: number;
    trends?: {
      totalLeads?: { change_percent: number; trend: string };
      assessmentsCompleted?: { change_percent: number; trend: string };
      conversions?: { change_percent: number; trend: string };
    };
  };
}

const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ analytics }) => {
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const metrics = [
    {
      title: 'Total Leads',
      value: analytics.totalLeads.toString(),
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      trend: analytics.trends?.totalLeads,
      subtitle: 'New prospects captured'
    },
    {
      title: 'Page Views',
      value: (analytics.pageViews || 0).toLocaleString(),
      icon: Eye,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      subtitle: 'Total website visits'
    },
    {
      title: 'Assessments',
      value: `${analytics.assessmentsCompleted || 0}/${analytics.assessmentsStarted || 0}`,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      trend: analytics.trends?.assessmentsCompleted,
      subtitle: 'Completed/Started'
    },
    {
      title: 'Conversion Rate',
      value: `${analytics.conversionRate}%`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      trend: analytics.trends?.conversions,
      subtitle: 'Lead to customer'
    },
    {
      title: 'Active Campaigns',
      value: analytics.campaignsActive.toString(),
      icon: Target,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      subtitle: 'Currently running'
    },
    {
      title: 'Engagement Rate',
      value: `${analytics.engagementRate}%`,
      icon: BarChart3,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      subtitle: 'User interaction rate'
    },
  ];

  const getTrendIcon = (trend?: { trend: string; change_percent: number }) => {
    if (!trend) return null;

    const { trend: trendDirection, change_percent } = trend;
    const isPositive = trendDirection === 'up';

    return (
      <div className={`flex items-center text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
        {Math.abs(change_percent)}%
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Analytics Overview</h2>
          <p className="text-gray-600 text-sm">Real-time performance metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center text-xs text-gray-500">
            <RefreshCw className="w-3 h-3 mr-1" />
            Updated {lastUpdated.toLocaleTimeString()}
          </div>
          <BarChart3 className="w-6 h-6 text-gray-400" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {metrics.map((metric, index) => (
          <div key={index} className="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 ${metric.bgColor} rounded-lg flex items-center justify-center`}>
                <metric.icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              {metric.trend && getTrendIcon(metric.trend)}
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
            <div className="text-sm font-medium text-gray-900 mb-1">{metric.title}</div>
            <div className="text-xs text-gray-600">{metric.subtitle}</div>
          </div>
        ))}
      </div>

      {/* Quick Insights */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <TrendingUp className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">Lead Generation</div>
              <div className="text-xs text-gray-600">
                {analytics.totalLeads > 10 ? 'Strong performance' : 'Room for improvement'}
              </div>
            </div>
          </div>

          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <CheckCircle className="w-4 h-4 text-green-600" />
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">Assessment Completion</div>
              <div className="text-xs text-gray-600">
                {analytics.assessmentsCompleted && analytics.assessmentsStarted &&
                 (analytics.assessmentsCompleted / analytics.assessmentsStarted) > 0.7
                  ? 'Excellent completion rate' : 'Monitor completion flow'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsOverview;