import React from 'react';
import { BarChart3, TrendingUp, Users, Target } from 'lucide-react';

interface AnalyticsOverviewProps {
  analytics: {
    totalLeads: number;
    campaignsActive: number;
    engagementRate: number;
    conversionRate: number;
  };
}

const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ analytics }) => {
  const metrics = [
    {
      title: 'Total Leads',
      value: analytics.totalLeads.toString(),
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Active Campaigns',
      value: analytics.campaignsActive.toString(),
      icon: Target,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Engagement Rate',
      value: `${analytics.engagementRate}%`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Conversion Rate',
      value: `${analytics.conversionRate}%`,
      icon: BarChart3,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Analytics Overview</h2>
          <p className="text-gray-600 text-sm">Your performance at a glance</p>
        </div>
        <BarChart3 className="w-6 h-6 text-gray-400" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="p-4 rounded-lg border border-gray-200">
            <div className={`w-10 h-10 ${metric.bgColor} rounded-lg flex items-center justify-center mb-3`}>
              <metric.icon className={`w-5 h-5 ${metric.color}`} />
            </div>
            <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
            <div className="text-sm text-gray-600">{metric.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalyticsOverview;