import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui';
import {
  Twitter,
  Plus,
  BarChart3,
  Calendar,
  Settings,
  Zap,
  Users,
  TrendingUp,
  MessageSquare,
  Heart,
  Repeat,
  ExternalLink,
  Facebook,
  Youtube,
  Instagram,
  Send,
  Globe
} from 'lucide-react';

interface SocialAccount {
  id: number;
  platform: string;
  username: string;
  name: string;
  profile_url: string;
  avatar_url: string;
  follower_count: number;
  is_active: boolean;
  last_synced_at: string;
}

interface Campaign {
  id: number;
  name: string;
  status: string;
  platforms: string[];
  total_posts: number;
  total_engagements: number;
  created_at: string;
}

interface AnalyticsData {
  summary: {
    total_posts: number;
    total_engagements: number;
    total_followers_gained: number;
    engagement_rate: number;
  };
  platform_breakdown: {
    [key: string]: {
      posts: number;
      engagements: number;
      followers_gained: number;
      engagement_rate: number;
    };
  };
}

const SocialDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'accounts' | 'campaigns' | 'analytics' | 'settings'>('overview');
  const [connectedAccounts, setConnectedAccounts] = useState<SocialAccount[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load accounts, campaigns, and analytics in parallel
      const [accountsRes, campaignsRes, analyticsRes] = await Promise.all([
        fetch('/api/v1/social/accounts'),
        fetch('/api/v1/social/campaigns'),
        fetch('/api/v1/social/analytics')
      ]);

      const accounts = await accountsRes.json();
      const campaigns = await campaignsRes.json();
      const analytics = await analyticsRes.json();

      setConnectedAccounts(accounts.accounts || []);
      setCampaigns(campaigns.campaigns || []);
      setAnalytics(analytics);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectAccount = async (platform: string) => {
    try {
      // Get OAuth URL
      const response = await fetch(`/api/v1/social/auth/${platform}/url?user_id=1`);
      const data = await response.json();

      // Store code verifier for later
      sessionStorage.setItem('oauth_code_verifier', data.code_verifier);
      sessionStorage.setItem('oauth_state', data.state);

      // Check if this is demo mode
      if (data.demo_mode) {
        alert(`Demo Mode: ${data.message}\n\nIn production, this would redirect to ${platform} for authentication.`);
        return;
      }

      // Redirect to OAuth
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Failed to get OAuth URL:', error);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'twitter':
        return <Twitter className="w-5 h-5" />;
      case 'facebook':
        return <Facebook className="w-5 h-5" />;
      case 'youtube':
        return <Youtube className="w-5 h-5" />;
      case 'instagram':
        return <Instagram className="w-5 h-5" />;
      case 'telegram':
        return <Send className="w-5 h-5" />;
      case 'reddit':
        return <MessageSquare className="w-5 h-5" />;
      case 'mastodon':
      case 'bluesky':
        return <Globe className="w-5 h-5" />;
      case 'pinterest':
        return <Heart className="w-5 h-5" />;
      default:
        return <Plus className="w-5 h-5" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'twitter':
        return 'bg-blue-500';
      case 'linkedin':
        return 'bg-blue-700';
      case 'medium':
        return 'bg-black';
      case 'facebook':
        return 'bg-blue-600';
      case 'youtube':
        return 'bg-red-600';
      case 'instagram':
        return 'bg-pink-500';
      case 'telegram':
        return 'bg-blue-400';
      case 'reddit':
        return 'bg-orange-500';
      case 'mastodon':
        return 'bg-purple-600';
      case 'bluesky':
        return 'bg-sky-500';
      case 'pinterest':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Social Media Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage your automated social media presence</p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center">
                <Zap className="w-4 h-4 mr-2" />
                Quick Post
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'accounts', label: 'Accounts', icon: Users },
              { id: 'campaigns', label: 'Campaigns', icon: Calendar },
              { id: 'analytics', label: 'Analytics', icon: TrendingUp },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center px-1 py-2 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <MessageSquare className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Posts</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics?.summary.total_posts || 0}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Heart className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Engagements</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics?.summary.total_engagements || 0}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Followers Gained</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics?.summary.total_followers_gained || 0}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Engagement Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {analytics?.summary.engagement_rate || 0}%
                    </p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Connected Accounts Preview */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Connected Accounts</h3>
                <button
                  onClick={() => setActiveTab('accounts')}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Manage All →
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {connectedAccounts.slice(0, 3).map(account => (
                  <div key={account.id} className="flex items-center p-4 border rounded-lg">
                    <img
                      src={account.avatar_url}
                      alt={account.name}
                      className="w-10 h-10 rounded-full mr-3"
                    />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{account.name}</p>
                      <p className="text-sm text-gray-500">{account.username}</p>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${account.is_active ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  </div>
                ))}
                {connectedAccounts.length === 0 && (
                  <div className="col-span-full text-center py-8">
                    <p className="text-gray-500 mb-4">No accounts connected yet</p>
                    <button
                      onClick={() => setActiveTab('accounts')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Connect Your First Account
                    </button>
                  </div>
                )}
              </div>
            </Card>

            {/* Recent Campaigns */}
            <Card className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Active Campaigns</h3>
                <button
                  onClick={() => setActiveTab('campaigns')}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View All →
                </button>
              </div>
              <div className="space-y-4">
                {campaigns.filter(c => c.status === 'active').slice(0, 3).map(campaign => (
                  <div key={campaign.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{campaign.name}</h4>
                      <p className="text-sm text-gray-500">
                        {campaign.total_posts} posts • {campaign.total_engagements} engagements
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {campaign.platforms.map(platform => (
                        <div key={platform} className={`w-6 h-6 rounded-full flex items-center justify-center ${getPlatformColor(platform)}`}>
                          {getPlatformIcon(platform)}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
                {campaigns.filter(c => c.status === 'active').length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">No active campaigns</p>
                    <button
                      onClick={() => setActiveTab('campaigns')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                    >
                      Create Your First Campaign
                    </button>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'accounts' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Connected Accounts</h2>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Connect Account
              </button>
            </div>

            {/* Platform Connection Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'Twitter', platform: 'twitter', description: 'Post tweets and engage with conversations' },
                { name: 'Facebook Page', platform: 'facebook', description: 'Manage Facebook pages and engage with audiences' },
                { name: 'YouTube', platform: 'youtube', description: 'Upload videos and manage channel content' },
                { name: 'Instagram', platform: 'instagram', description: 'Share photos and stories with your audience' },
                { name: 'Telegram', platform: 'telegram', description: 'Send messages and manage Telegram channels' },
                { name: 'Reddit', platform: 'reddit', description: 'Post to subreddits and engage with communities' },
                { name: 'Mastodon', platform: 'mastodon', description: 'Decentralized social networking' },
                { name: 'Bluesky', platform: 'bluesky', description: 'Open social media platform' },
                { name: 'Pinterest', platform: 'pinterest', description: 'Share visual content and drive traffic' },
                { name: 'LinkedIn', platform: 'linkedin', description: 'Professional networking and thought leadership' },
                { name: 'Medium', platform: 'medium', description: 'Long-form content publishing' }
              ].map(({ name, platform, description }) => {
                const isConnected = connectedAccounts.some(acc => acc.platform === platform);

                return (
                  <Card key={platform} className="p-6">
                    <div className="flex items-center mb-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-3 ${getPlatformColor(platform)}`}>
                        {getPlatformIcon(platform)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{name}</h3>
                        <span className={`text-xs px-2 py-1 rounded-full ${isConnected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                          {isConnected ? 'Connected' : 'Not Connected'}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">{description}</p>
                    {!isConnected && (
                      <button
                        onClick={() => handleConnectAccount(platform)}
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Connect {name}
                      </button>
                    )}
                    {isConnected && (
                      <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                        Manage Account
                      </button>
                    )}
                  </Card>
                );
              })}
            </div>

            {/* Connected Accounts List */}
            {connectedAccounts.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Connected Accounts</h3>
                <div className="space-y-4">
                  {connectedAccounts.map(account => (
                    <div key={account.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center">
                        <img
                          src={account.avatar_url}
                          alt={account.name}
                          className="w-12 h-12 rounded-full mr-4"
                        />
                        <div>
                          <h4 className="font-medium text-gray-900">{account.name}</h4>
                          <p className="text-sm text-gray-500">{account.username}</p>
                          <p className="text-xs text-gray-400">
                            {account.follower_count.toLocaleString()} followers
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs ${account.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {account.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button className="text-gray-400 hover:text-gray-600">
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Campaigns</h2>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Create Campaign
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {campaigns.map(campaign => (
                <Card key={campaign.id} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                      campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {campaign.status}
                    </span>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Posts:</span>
                      <span className="font-medium">{campaign.total_posts}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Engagements:</span>
                      <span className="font-medium">{campaign.total_engagements}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex space-x-1">
                      {campaign.platforms.map(platform => (
                        <div key={platform} className={`w-6 h-6 rounded-full flex items-center justify-center ${getPlatformColor(platform)}`}>
                          {getPlatformIcon(platform)}
                        </div>
                      ))}
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      Manage →
                    </button>
                  </div>
                </Card>
              ))}

              {campaigns.length === 0 && (
                <div className="col-span-full text-center py-12">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
                  <p className="text-gray-500 mb-6">Create your first automated social media campaign</p>
                  <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                    Create Campaign
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>

            {analytics ? (
              <div className="space-y-6">
                {/* Platform Breakdown */}
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Performance</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Object.entries(analytics.platform_breakdown).map(([platform, stats]) => (
                      <div key={platform} className="p-4 border rounded-lg">
                        <div className="flex items-center mb-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-3 ${getPlatformColor(platform)}`}>
                            {getPlatformIcon(platform)}
                          </div>
                          <h4 className="font-medium text-gray-900 capitalize">{platform}</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Posts:</span>
                            <span className="font-medium">{stats.posts}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Engagements:</span>
                            <span className="font-medium">{stats.engagements}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Engagement Rate:</span>
                            <span className="font-medium">{stats.engagement_rate}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            ) : (
              <Card className="p-12 text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No analytics data yet</h3>
                <p className="text-gray-500">Start posting and engaging to see your performance metrics</p>
              </Card>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Settings</h2>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Automation Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Auto-posting</h4>
                    <p className="text-sm text-gray-600">Automatically publish scheduled content</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Auto-engagement</h4>
                    <p className="text-sm text-gray-600">Automatically like, comment, and follow relevant accounts</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Email notifications</h4>
                    <p className="text-sm text-gray-600">Get notified about campaign performance and issues</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialDashboard;

// Export empty object to make this a module
export {};