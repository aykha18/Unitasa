import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Plus, Trash2, Send, LayoutList, Calendar as CalendarIcon, Rocket, Settings, Edit2 } from 'lucide-react';
import { Button, Modal } from '../components/ui';
import Toast from '../components/ui/Toast';
import CalendarView from '../components/social/CalendarView';

interface SocialAccount {
  id: number;
  platform: string;
  username: string;
  name: string;
  avatar_url?: string;
  settings: {
    approval_required?: boolean;
    [key: string]: any;
  };
}

interface ScheduleRule {
  id: number;
  name: string;
  frequency: string;
  time_of_day: string;
  platforms: string[];
  is_active: boolean;
  days_of_week?: string[];
  next_run_at?: string;
}

interface ScheduledPost {
  id: string;
  content: string;
  platform: string;
  scheduled_at: string;
  status: 'pending' | 'posted' | 'failed';
}

type Frequency = 'daily' | 'weekly' | 'monthly';
type GenerationMode = 'automatic' | 'manual';

const getPlatformLimit = (platform: string) => {
  switch(platform.toLowerCase()) {
    case 'twitter': return 280;
    case 'instagram': return 2200;
    case 'linkedin': return 3000;
    case 'facebook': return 63206;
    default: return 280;
  }
};

const SchedulePostsPage: React.FC = () => {
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    content: '',
    platform: 'twitter',
    scheduled_time: ''
  });
  const [useRecurring, setUseRecurring] = useState(false);
  const [frequency, setFrequency] = useState<Frequency>('daily');
  const [generationMode, setGenerationMode] = useState<GenerationMode>('automatic');
  const [autopost, setAutopost] = useState(true);
  const [timezone, setTimezone] = useState('UTC');
  const [timeOfDay, setTimeOfDay] = useState('09:00');
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>([1,3,5]);
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('professional');
  const [contentType, setContentType] = useState('educational');
  const [drafts, setDrafts] = useState<any[]>([]);
  const [historyPosts, setHistoryPosts] = useState<any[]>([]);
  const [historyTab, setHistoryTab] = useState<'posted' | 'failed'>('posted');
  const [postedOffset, setPostedOffset] = useState(0);
  const [failedOffset, setFailedOffset] = useState(0);
  const [toast, setToast] = useState<{ show: boolean; title: string; message: string; type: 'success' | 'error' | 'warning' | 'info' }>({ 
    show: false, 
    title: '', 
    message: '', 
    type: 'info' 
  });
  
  // Phase 2 State
  const [recurrenceConfig, setRecurrenceConfig] = useState<{ type: 'date' | 'nth_weekday', nth?: number, weekday?: number }>({ type: 'date' });
  const [skipDates, setSkipDates] = useState<string[]>([]);
  const [themePreset, setThemePreset] = useState<string>('custom');
  const [contentVariation, setContentVariation] = useState({ creativity: 50, humor: 30, length: 50 });
  const [skipDateInput, setSkipDateInput] = useState('');
  
  // Phase 3 State
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');
  const [showCampaignForm, setShowCampaignForm] = useState(false);
  const [campaignData, setCampaignData] = useState({
    name: '',
    target_audience: '',
    content_requirements: ''
  });

  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showManageRules, setShowManageRules] = useState(false);
  const [rules, setRules] = useState<ScheduleRule[]>([]);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; postId: string | null; postContent?: string }>({ 
    isOpen: false, 
    postId: null 
  });
  
  const [editModal, setEditModal] = useState<{ isOpen: boolean; post: ScheduledPost | null }>({
    isOpen: false,
    post: null
  });
  const [editFormData, setEditFormData] = useState({
    content: '',
    scheduled_time: ''
  });

  // API Configuration
  const getApiBaseUrl = () => {
    if (process.env.REACT_APP_API_URL &&
        !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app')) {
      return process.env.REACT_APP_API_URL;
    }

    if (process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost') {
      return '';
    }

    return 'http://localhost:8001';
  };

  const fetchHistory = async (status: 'posted' | 'failed', offset: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${getApiBaseUrl()}/api/v1/social/history?status=${status}&limit=5&offset=${offset}`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      if (res.status === 401) {
        window.location.href = '/signin';
        return;
      }
      if (res.ok) {
        const h = await res.json();
        setHistoryPosts(h.history_posts || []);
      }
    } catch (e) {
      console.error('Error fetching history', e);
    }
  };

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/accounts`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      
      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const fetchRules = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/schedule/rules`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      if (response.ok) {
        const data = await response.json();
        setRules(data.rules || []);
      }
    } catch (error) {
      console.error('Error fetching rules:', error);
    }
  };

  const handleDeleteRule = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this rule?')) return;
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/schedule/rules/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      
      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Rule deleted successfully', type: 'success' });
        fetchRules();
      } else {
        setToast({ show: true, title: 'Error', message: 'Failed to delete rule', type: 'error' });
      }
    } catch (error) {
      console.error('Error deleting rule:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to delete rule', type: 'error' });
    }
  };

  const toggleApproval = async (accountId: number, current: boolean) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/accounts/${accountId}/settings`, {
        method: 'PATCH',
        headers: { 
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ approval_required: !current })
      });
      
      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Settings updated', type: 'success' });
        fetchAccounts();
      } else {
        setToast({ show: true, title: 'Error', message: 'Failed to update settings', type: 'error' });
      }
    } catch (e) {
      setToast({ show: true, title: 'Error', message: 'Failed to update settings', type: 'error' });
    }
  };

  // Fetch scheduled posts
  const fetchScheduledPosts = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setScheduledPosts(data.scheduled_posts || []);
      }
      const draftsRes = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled/drafts`, {
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      
      if (draftsRes.status === 401) {
         // Already handled above, but good to be safe
         return;
      }

      if (draftsRes.ok) {
        const d = await draftsRes.json();
        setDrafts(d.draft_posts || []);
      }
    } catch (error) {
      console.error('Error fetching scheduled posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatApiError = (error: any): string => {
    if (!error) return 'An unknown error occurred';
    if (typeof error.detail === 'string') return error.detail;
    if (Array.isArray(error.detail)) {
      return error.detail.map((err: any) => err.msg || JSON.stringify(err)).join('\n');
    }
    if (typeof error.detail === 'object') {
      return JSON.stringify(error.detail);
    }
    return 'An error occurred';
  };

  // Schedule a new post
  const handleSchedulePost = async () => {
    let contentToPost = formData.content;

    // Handle automatic generation
    if (generationMode === 'automatic' && !contentToPost) {
      if (!topic && generationMode === 'automatic') {
        // Allow topic to be optional if user wants random content? 
        // But for now let's be safe or just proceed. 
        // Actually, existing generator allows empty topic.
      }
      
      setLoading(true);
      try {
        const token = localStorage.getItem('access_token');
        let clientId = localStorage.getItem('current_client_id');
        if (clientId && (clientId.startsWith('"') || clientId.startsWith('{'))) {
            try { clientId = JSON.parse(clientId); } catch (e) {}
        }

        const genRes = await fetch(`${getApiBaseUrl()}/api/v1/social/content/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : '',
            },
            body: JSON.stringify({
                feature_key: 'automated_social_posting',
                platform: formData.platform,
                content_type: contentType,
                tone,
                topic,
                client_id: clientId
            })
        });
        
        if (genRes.status === 401) {
            window.location.href = '/signin';
            return;
        }
        
        if (genRes.ok) {
            const data = await genRes.json();
            if (data.content && data.content.length > 0) {
                contentToPost = data.content[0].content;
                setFormData(prev => ({ ...prev, content: contentToPost }));
            } else {
                throw new Error('No content generated');
            }
        } else {
            throw new Error('Failed to generate content');
        }
      } catch (e) {
        setLoading(false);
        setToast({ show: true, title: 'Generation Error', message: 'Failed to generate content. Please try again.', type: 'error' });
        return;
      }
      setLoading(false);
    }

    if (!contentToPost || !formData.scheduled_time) {
      setToast({ show: true, title: 'Validation Error', message: 'Please fill in all fields', type: 'error' });
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          content: contentToPost,
          platforms: [formData.platform],
          scheduled_at: formData.scheduled_time,
          timezone_offset_minutes: new Date().getTimezoneOffset()
        }),
      });

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Post scheduled successfully!', type: 'success' });
        setFormData({ content: '', platform: 'twitter', scheduled_time: '' });
        setShowForm(false);
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setToast({ show: true, title: 'Error', message: formatApiError(error), type: 'error' });
      }
    } catch (error) {
      console.error('Error scheduling post:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to schedule post. Please try again.', type: 'error' });
    }
  };

  const handleLaunchCampaign = async () => {
    if (!campaignData.name || !campaignData.target_audience || !campaignData.content_requirements) {
      setToast({ show: true, title: 'Error', message: 'Please fill in all campaign fields', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      
      // Parse JSON fields if they are JSON strings, otherwise treat as text description
      let audience = {};
      try {
        audience = JSON.parse(campaignData.target_audience);
      } catch (e) {
        audience = { description: campaignData.target_audience };
      }

      let requirements = {};
      try {
        requirements = JSON.parse(campaignData.content_requirements);
      } catch (e) {
        requirements = { description: campaignData.content_requirements };
      }

      const response = await fetch(`${getApiBaseUrl()}/api/v1/ai/campaign/launch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          campaign_name: campaignData.name,
          target_audience: audience,
          content_requirements: requirements,
          campaign_config: {}
        }),
      });

      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Campaign launched successfully!', type: 'success' });
        setShowCampaignForm(false);
        setCampaignData({ name: '', target_audience: '', content_requirements: '' });
        // Optionally fetch campaigns or update view
      } else {
        const error = await response.json();
        setToast({ show: true, title: 'Error', message: error.detail || 'Failed to launch campaign', type: 'error' });
      }
    } catch (error) {
      console.error('Error launching campaign:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to launch campaign. Please try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/schedule/rules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          name: 'Recurring schedule',
          platforms: [formData.platform],
          frequency,
          time_of_day: timeOfDay,
          timezone,
          generation_mode: generationMode,
          autopost,
          days_of_week: frequency === 'weekly' ? daysOfWeek : undefined,
          content_seed: generationMode === 'manual' ? formData.content : undefined,
          topic: generationMode === 'automatic' ? topic : undefined,
          tone: generationMode === 'automatic' ? tone : undefined,
          content_type: generationMode === 'automatic' ? contentType : undefined,
          recurrence_config: useRecurring ? (
            recurrenceConfig.type === 'nth_weekday'
              ? { type: 'nth_weekday', nth: recurrenceConfig.nth, weekday: recurrenceConfig.weekday }
              : { type: 'date' }
          ) : undefined,
          skip_dates: useRecurring ? skipDates : undefined,
          theme_preset: useRecurring ? themePreset : undefined,
          content_variation: useRecurring && generationMode === 'automatic' ? contentVariation : undefined
        })
      });
      
      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Schedule rule created!', type: 'success' });
        setShowForm(false);
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setToast({ show: true, title: 'Error', message: formatApiError(error), type: 'error' });
      }
    } catch (error) {
      console.error('Error creating rule:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to create rule. Please try again.', type: 'error' });
    }
  };

  const approveDraft = async (id: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled/${id}/approve`, {
        method: 'POST',
        headers: { 'Authorization': token ? `Bearer ${token}` : '' }
      });
      if (res.ok) {
        setToast({ show: true, title: 'Success', message: 'Draft approved!', type: 'success' });
        fetchScheduledPosts();
      } else {
        setToast({ show: true, title: 'Error', message: 'Failed to approve draft', type: 'error' });
      }
    } catch (e) {
      console.error(e);
      setToast({ show: true, title: 'Error', message: 'Failed to approve draft', type: 'error' });
    }
  };

  // Edit scheduled post
  const handleEditClick = (post: ScheduledPost) => {
    // Format date for datetime-local input (YYYY-MM-DDTHH:mm)
    let formattedDate = '';
    if (post.scheduled_at) {
      const date = new Date(post.scheduled_at);
      const localDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
      formattedDate = localDate.toISOString().slice(0, 16);
    }

    setEditFormData({
      content: post.content,
      scheduled_time: formattedDate
    });
    setEditModal({
      isOpen: true,
      post: post
    });
  };

  const handleUpdatePost = async () => {
    if (!editModal.post) return;
    
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled/${editModal.post.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          content: editFormData.content,
          scheduled_at: editFormData.scheduled_time
        }),
      });

      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Post updated successfully!', type: 'success' });
        setEditModal({ isOpen: false, post: null });
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        setToast({ show: true, title: 'Error', message: formatApiError(error), type: 'error' });
      }
    } catch (error) {
      console.error('Error updating post:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to update post. Please try again.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Delete scheduled post
  const handleDeleteClick = (post: ScheduledPost) => {
    setDeleteConfirmation({
      isOpen: true,
      postId: post.id,
      postContent: post.content
    });
  };

  const confirmDelete = async () => {
    if (!deleteConfirmation.postId) return;
    const postId = deleteConfirmation.postId;
    setDeleteConfirmation({ isOpen: false, postId: null });

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (response.status === 401) {
        window.location.href = '/signin';
        return;
      }

      if (response.ok) {
        setToast({ show: true, title: 'Success', message: 'Post deleted successfully!', type: 'success' });
        fetchScheduledPosts();
      } else {
        setToast({ show: true, title: 'Error', message: 'Failed to delete post', type: 'error' });
      }
    } catch (error) {
      console.error('Error deleting post:', error);
      setToast({ show: true, title: 'Error', message: 'Failed to delete post. Please try again.', type: 'error' });
    }
  };
  
  const handleDateClick = (date: Date) => {
    // Pre-fill the form with the selected date
    const localDate = new Date(date);
    localDate.setMinutes(localDate.getMinutes() - localDate.getTimezoneOffset());
    const isoString = localDate.toISOString().slice(0, 16); // format: YYYY-MM-DDTHH:mm
    
    setFormData(prev => ({ ...prev, scheduled_time: isoString }));
    setUseRecurring(false); // Switch to one-off post mode
    setShowForm(true);
    
    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  const handlePostClick = (post: ScheduledPost) => {
      // In future, could open edit modal. For now, just show content in toast or log
      console.log('Clicked post:', post);
      handleDeleteClick(post);
  };

  useEffect(() => {
    fetchScheduledPosts();
    fetchAccounts();
    fetchHistory('posted', 0);
    fetchRules();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Calendar className="w-8 h-8 mr-3 text-indigo-600" />
                Schedule Posts
              </h1>
              <p className="text-gray-600 mt-2">Plan and schedule your social media content</p>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex bg-gray-100 p-1 rounded-lg mr-2">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                  title="List View"
                >
                  <LayoutList className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('calendar')}
                  className={`p-2 rounded-md transition-colors ${viewMode === 'calendar' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'}`}
                  title="Calendar View"
                >
                  <CalendarIcon className="w-4 h-4" />
                </button>
              </div>
              <Button
                variant="ghost"
                onClick={() => {
                  window.history.pushState({}, '', '/dashboard');
                  window.dispatchEvent(new Event('navigate'));
                }}
              >
                Back to Dashboard
              </Button>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowForm(true);
                  setUseRecurring(false);
                }}
              >
                <Plus className="w-4 h-4 mr-2" />
                New Post
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                   setShowForm(true);
                   setUseRecurring(true);
                }}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <Clock className="w-4 h-4 mr-2" />
                Schedule Recurring
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowManageRules(true)}
                className="ml-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50"
              >
                <LayoutList className="w-4 h-4 mr-2" />
                Manage Rules
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowCampaignForm(true)}
                className="ml-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50"
              >
                <Rocket className="w-4 h-4 mr-2" />
                Launch Campaign
              </Button>
              <Button
                variant="ghost"
                onClick={() => setShowSettings(true)}
                className="ml-2 text-gray-500 hover:text-gray-700"
                title="Settings"
              >
                <Settings className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Manage Rules Modal */}
        {showManageRules && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900 flex items-center">
                  <LayoutList className="w-6 h-6 mr-2 text-indigo-600" />
                  Manage Recurring Rules
                </h2>
                <button
                  onClick={() => setShowManageRules(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="p-6">
                {rules.length === 0 ? (
                  <div className="text-center py-12">
                    <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No recurring rules</h3>
                    <p className="mt-1 text-sm text-gray-500">Get started by creating a new recurring schedule.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Frequency</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platforms</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Next Run</th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {rules.map((rule) => (
                          <tr key={rule.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{rule.name}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {rule.frequency} at {rule.time_of_day}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <div className="flex space-x-2">
                                {rule.platforms.map(p => (
                                  <span key={p} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 capitalize">
                                    {p}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {rule.next_run_at ? new Date(rule.next_run_at).toLocaleString() : 'Pending'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <button
                                onClick={() => handleDeleteRule(rule.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
              <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900 flex items-center">
                  <Settings className="w-6 h-6 mr-2 text-indigo-600" />
                  Approval Settings
                </h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="p-6">
                <p className="text-sm text-gray-600 mb-4">
                  Enable approval requirements for posts scheduled on specific platforms.
                </p>
                <div className="space-y-4">
                  {accounts.length === 0 ? (
                    <p className="text-center text-gray-500 py-4">No accounts connected</p>
                  ) : (
                    accounts.map(acc => (
                      <div key={acc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                           {acc.avatar_url && <img src={acc.avatar_url} alt="" className="w-8 h-8 rounded-full" />}
                           <div>
                             <p className="font-medium text-gray-900">{acc.username}</p>
                             <p className="text-xs text-gray-500 capitalize">{acc.platform}</p>
                           </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            className="sr-only peer"
                            checked={acc.settings?.approval_required || false}
                            onChange={() => toggleApproval(acc.id, acc.settings?.approval_required || false)}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Campaign Modal */}
        {showCampaignForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900 flex items-center">
                  <Rocket className="w-6 h-6 mr-2 text-indigo-600" />
                  Launch AI Marketing Campaign
                </h2>
                <button
                  onClick={() => setShowCampaignForm(false)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
                  <input
                    type="text"
                    value={campaignData.name}
                    onChange={(e) => setCampaignData(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="e.g. Q1 Product Launch"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Audience (Description or JSON)</label>
                  <textarea
                    value={campaignData.target_audience}
                    onChange={(e) => setCampaignData(prev => ({ ...prev, target_audience: e.target.value }))}
                    rows={4}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Describe your target audience or paste JSON configuration..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content Requirements (Description or JSON)</label>
                  <textarea
                    value={campaignData.content_requirements}
                    onChange={(e) => setCampaignData(prev => ({ ...prev, content_requirements: e.target.value }))}
                    rows={4}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Describe content requirements (topic, tone, etc.)..."
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                  <Button
                    variant="outline"
                    onClick={() => setShowCampaignForm(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleLaunchCampaign}
                    className="bg-indigo-600 hover:bg-indigo-700"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Launching...
                      </>
                    ) : (
                      <>
                        <Rocket className="w-4 h-4 mr-2" />
                        Launch Campaign
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Form */}
        {showForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Schedule New Post</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <label className="inline-flex items-center">
                  <input type="checkbox" checked={useRecurring} onChange={(e) => setUseRecurring(e.target.checked)} className="mr-2" />
                  Recurring Schedule
                </label>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-700">Mode</span>
                  <select value={generationMode} onChange={(e) => setGenerationMode(e.target.value as GenerationMode)} className="px-3 py-2 border rounded-lg">
                    <option value="automatic">Automatic</option>
                    <option value="manual">Manual</option>
                  </select>
                </div>
                <label className="inline-flex items-center">
                  <input type="checkbox" checked={autopost} onChange={(e) => setAutopost(e.target.checked)} className="mr-2" />
                  Auto-post
                </label>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows={4}
                  placeholder="What's on your mind?"
                />
                <div className={`mt-1 text-sm text-right ${formData.content.length > getPlatformLimit(formData.platform) ? 'text-red-600 font-bold' : 'text-gray-500'}`}>
                  {formData.content.length} / {getPlatformLimit(formData.platform)} chars
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Platform
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData(prev => ({ ...prev, platform: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="twitter">Twitter</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                  </select>
                </div>

                {!useRecurring && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Schedule Time
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.scheduled_time}
                      onChange={(e) => setFormData(prev => ({ ...prev, scheduled_time: e.target.value }))}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                )}
              </div>

              {useRecurring && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                    <div className="flex space-x-2">
                      {(['daily','weekly','monthly'] as Frequency[]).map(f => (
                        <button
                          key={f}
                          onClick={() => setFrequency(f)}
                          className={`px-3 py-2 rounded-lg border ${frequency===f?'bg-indigo-600 text-white border-indigo-600':'bg-white text-gray-700 border-gray-300'}`}
                        >
                          {f.charAt(0).toUpperCase()+f.slice(1)}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Time of Day</label>
                    <input
                      type="time"
                      value={timeOfDay}
                      onChange={(e) => setTimeOfDay(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                    <select
                      value={timezone}
                      onChange={(e) => setTimezone(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="UTC">UTC</option>
                      <option value="Asia/Kolkata">Asia/Kolkata</option>
                      <option value="America/New_York">America/New_York</option>
                      <option value="Europe/London">Europe/London</option>
                    </select>
                  </div>
                  {frequency === 'weekly' && (
                    <div className="md:col-span-3">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Days of Week</label>
                      <div className="flex flex-wrap gap-2">
                        {[0,1,2,3,4,5,6].map(d => (
                          <button
                            key={d}
                            onClick={() => {
                              setDaysOfWeek(prev => prev.includes(d) ? prev.filter(x=>x!==d) : [...prev, d]);
                            }}
                            className={`px-3 py-2 rounded-lg border ${
                              daysOfWeek.includes(d) ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-300'
                            }`}
                          >
                            {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d]}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {generationMode === 'automatic' && (
                    <div className="md:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
                        <input
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Tone</label>
                        <select
                          value={tone}
                          onChange={(e) => setTone(e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                          <option value="professional">Professional</option>
                          <option value="friendly">Friendly</option>
                          <option value="bold">Bold</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
                        <select
                          value={contentType}
                          onChange={(e) => setContentType(e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                          <option value="educational">Educational</option>
                          <option value="benefit_focused">Benefit Focused</option>
                          <option value="social_proof">Social Proof</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {useRecurring && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Advanced Recurrence</label>
                    <div className="flex items-center space-x-3 mb-3">
                      <label className="inline-flex items-center">
                        <input
                          type="radio"
                          checked={recurrenceConfig.type === 'date'}
                          onChange={() => setRecurrenceConfig({ type: 'date' })}
                          className="mr-2"
                        />
                        By Date
                      </label>
                      <label className="inline-flex items-center">
                        <input
                          type="radio"
                          checked={recurrenceConfig.type === 'nth_weekday'}
                          onChange={() => setRecurrenceConfig({ type: 'nth_weekday', nth: recurrenceConfig.nth || 1, weekday: recurrenceConfig.weekday ?? 1 })}
                          className="mr-2"
                        />
                        Nth Weekday
                      </label>
                    </div>
                    {recurrenceConfig.type === 'nth_weekday' && (
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Nth</label>
                          <select
                            value={recurrenceConfig.nth || 1}
                            onChange={(e) => setRecurrenceConfig(prev => ({ ...prev, nth: parseInt(e.target.value, 10) }))}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                          >
                            {[1,2,3,4,5].map(n => (<option key={n} value={n}>{n}</option>))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Weekday</label>
                          <select
                            value={recurrenceConfig.weekday ?? 1}
                            onChange={(e) => setRecurrenceConfig(prev => ({ ...prev, weekday: parseInt(e.target.value, 10) }))}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                          >
                            {[0,1,2,3,4,5,6].map(d => (<option key={d} value={d}>{['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d]}</option>))}
                          </select>
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Skip Dates</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="date"
                        value={skipDateInput}
                        onChange={(e) => setSkipDateInput(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      <Button
                        onClick={() => {
                          if (skipDateInput) {
                            setSkipDates(prev => Array.from(new Set([...prev, skipDateInput])));
                            setSkipDateInput('');
                          }
                        }}
                        className="bg-indigo-600 hover:bg-indigo-700"
                      >
                        Add
                      </Button>
                    </div>
                    {skipDates.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {skipDates.map((d) => (
                          <span key={d} className="px-2 py-1 text-sm rounded-full border border-gray-300">
                            <span className="mr-2">{d}</span>
                            <button
                              onClick={() => setSkipDates(prev => prev.filter(x => x !== d))}
                              className="text-red-600"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Theme Preset</label>
                    <select
                      value={themePreset}
                      onChange={(e) => setThemePreset(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="custom">Custom</option>
                      <option value="professional">Professional</option>
                      <option value="friendly">Friendly</option>
                      <option value="bold">Bold</option>
                      <option value="emoji_heavy">Emoji Heavy</option>
                      <option value="hashtag_light">Hashtag Light</option>
                    </select>
                  </div>
                </div>
              )}

              {useRecurring && generationMode === 'automatic' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Creativity</label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={contentVariation.creativity}
                      onChange={(e) => setContentVariation(prev => ({ ...prev, creativity: parseInt(e.target.value, 10) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Humor</label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={contentVariation.humor}
                      onChange={(e) => setContentVariation(prev => ({ ...prev, humor: parseInt(e.target.value, 10) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Length</label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={contentVariation.length}
                      onChange={(e) => setContentVariation(prev => ({ ...prev, length: parseInt(e.target.value, 10) }))}
                      className="w-full"
                    />
                  </div>
                </div>
              )}

              <div className="flex space-x-3">
                {!useRecurring ? (
                  <Button onClick={handleSchedulePost} className="bg-indigo-600 hover:bg-indigo-700">
                    <Send className="w-4 h-4 mr-2" />
                    Schedule Post
                  </Button>
                ) : (
                  <Button onClick={handleCreateRule} className="bg-indigo-600 hover:bg-indigo-700">
                    <Send className="w-4 h-4 mr-2" />
                    Create Rule
                  </Button>
                )}
                <Button
                  onClick={() => setShowForm(false)}
                  variant="outline"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Scheduled Posts List */}
        {viewMode === 'calendar' ? (
          <CalendarView
            posts={scheduledPosts}
            onDateClick={handleDateClick}
            onPostClick={handlePostClick}
          />
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Scheduled Posts</h2>
              <p className="text-gray-600 text-sm mt-1">Your upcoming scheduled content</p>
            </div>

            <div className="p-6">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2">Loading scheduled posts...</p>
                </div>
              ) : scheduledPosts.length === 0 ? (
                <div className="text-center py-12">
                  <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No scheduled posts</h3>
                  <p className="text-gray-600 mb-4">Start scheduling your content to reach your audience at the perfect time.</p>
                  <Button onClick={() => setShowForm(true)} className="bg-indigo-600 hover:bg-indigo-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Schedule Your First Post
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {scheduledPosts.map((post) => (
                    <div key={post.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            post.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            post.status === 'posted' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {post.status}
                          </span>
                          <span className="text-sm text-gray-600 capitalize">{post.platform}</span>
                        </div>
                        <p className="text-gray-900 mb-2">{post.content}</p>
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="w-4 h-4 mr-1" />
                          {new Date(post.scheduled_at).toLocaleString()}
                        </div>
                      </div>
                      {post.status === 'pending' && (
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => handleEditClick(post)}
                            variant="outline"
                            size="sm"
                            className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            onClick={() => handleDeleteClick(post)}
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        )}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mt-8">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Awaiting Approval</h2>
            <p className="text-gray-600 text-sm mt-1">Drafts generated from schedule rules</p>
          </div>
          <div className="p-6">
            {drafts.length === 0 ? (
              <div className="text-center py-12 text-gray-600">No drafts</div>
            ) : (
              <div className="space-y-4">
                {drafts.map((post) => (
                  <div key={post.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-sm text-gray-600 capitalize">{post.platform}</span>
                        </div>
                        <p className="text-gray-900 mb-2">{post.content}</p>
                        <div className="flex items-center text-sm text-gray-600">
                          Draft created {new Date(post.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          onClick={() => handleDeleteClick(post)}
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                        <Button
                          onClick={() => approveDraft(post.id)}
                          className="bg-green-600 hover:bg-green-700"
                          size="sm"
                        >
                          Approve
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Post History */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mt-8 mb-8">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Post History</h2>
                <p className="text-gray-600 text-sm mt-1">Logs of posted and failed content</p>
              </div>
              <div className="flex bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => { setHistoryTab('posted'); fetchHistory('posted', postedOffset); }}
                  className={`px-3 py-2 rounded-md transition-colors ${historyTab === 'posted' ? 'bg-white shadow-sm text-green-700' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  Successful
                </button>
                <button
                  onClick={() => { setHistoryTab('failed'); fetchHistory('failed', failedOffset); }}
                  className={`ml-2 px-3 py-2 rounded-md transition-colors ${historyTab === 'failed' ? 'bg-white shadow-sm text-red-700' : 'text-gray-600 hover:text-gray-800'}`}
                >
                  Failed
                </button>
              </div>
            </div>
          </div>
          <div className="p-6">
            {historyPosts.length === 0 ? (
              <div className="text-center py-12 text-gray-600">No history available</div>
            ) : (
              <>
                <div className="space-y-4">
                  {historyPosts.map((post) => (
                    <div key={post.id} className={`border rounded-lg p-4 ${post.status === 'failed' ? 'border-red-200 bg-red-50' : 'border-gray-200'}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              post.status === 'posted' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {post.status.toUpperCase()}
                            </span>
                            <span className="text-sm text-gray-600 capitalize">{post.platform}</span>
                          </div>
                          <p className="text-gray-900 mb-2">{post.content}</p>
                          <div className="flex flex-col text-sm text-gray-600">
                            <span>
                              <Clock className="w-3 h-3 inline mr-1" />
                              {historyTab === 'posted'
                                ? `Posted: ${post.posted_at ? new Date(post.posted_at).toLocaleString() : '-'}`
                                : `Failed: ${post.failed_at ? new Date(post.failed_at).toLocaleString() : '-'}`}
                            </span>
                            {historyTab === 'failed' && post.failure_reason && (
                              <span className="text-red-600 mt-1 font-medium">Error: {post.failure_reason}</span>
                            )}
                            {historyTab === 'posted' && post.post_url && (
                              <a href={post.post_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline mt-1">
                                View Post
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-6">
                  <Button
                    variant="outline"
                    onClick={() => {
                      if (historyTab === 'posted') {
                        const newOffset = Math.max(0, postedOffset - 5);
                        setPostedOffset(newOffset);
                        fetchHistory('posted', newOffset);
                      } else {
                        const newOffset = Math.max(0, failedOffset - 5);
                        setFailedOffset(newOffset);
                        fetchHistory('failed', newOffset);
                      }
                    }}
                    disabled={(historyTab === 'posted' ? postedOffset : failedOffset) === 0}
                  >
                    Previous
                  </Button>
                  <Button
                    onClick={() => {
                      if (historyTab === 'posted') {
                        const newOffset = postedOffset + 5;
                        setPostedOffset(newOffset);
                        fetchHistory('posted', newOffset);
                      } else {
                        const newOffset = failedOffset + 5;
                        setFailedOffset(newOffset);
                        fetchHistory('failed', newOffset);
                      }
                    }}
                    disabled={historyPosts.length < 5}
                    className="bg-indigo-600 hover:bg-indigo-700"
                  >
                    Next
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      <Modal
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false, postId: null })}
        title="Delete Post"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => setDeleteConfirmation({ isOpen: false, postId: null })}
            >
              Cancel
            </Button>
            <Button
              className="bg-red-600 hover:bg-red-700 text-white"
              onClick={confirmDelete}
            >
              Delete
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Are you sure you want to delete this post? This action cannot be undone.
          </p>
          {deleteConfirmation.postContent && (
            <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
              <p className="text-sm text-gray-800 italic">"{deleteConfirmation.postContent}"</p>
            </div>
          )}
        </div>
      </Modal>

      <Modal
        isOpen={editModal.isOpen}
        onClose={() => setEditModal({ isOpen: false, post: null })}
        title="Edit Post"
        footer={
          <>
            <Button
              variant="outline"
              onClick={() => setEditModal({ isOpen: false, post: null })}
            >
              Cancel
            </Button>
            <Button
              className="bg-indigo-600 hover:bg-indigo-700 text-white"
              onClick={handleUpdatePost}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content
            </label>
            <textarea
              value={editFormData.content}
              onChange={(e) => setEditFormData(prev => ({ ...prev, content: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              rows={4}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Schedule Time
            </label>
            <input
              type="datetime-local"
              value={editFormData.scheduled_time}
              onChange={(e) => setEditFormData(prev => ({ ...prev, scheduled_time: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </Modal>

      <Toast
        {...toast}
        onClose={() => setToast(prev => ({ ...prev, show: false }))}
      />
    </div>
  );
};

export default SchedulePostsPage;
