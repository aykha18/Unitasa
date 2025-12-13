import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Plus, Trash2, Send } from 'lucide-react';
import { Button } from '../components/ui';

interface ScheduledPost {
  id: string;
  content: string;
  platform: string;
  scheduled_time: string;
  status: 'pending' | 'posted' | 'failed';
}

const SchedulePostsPage: React.FC = () => {
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    content: '',
    platform: 'twitter',
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

      if (response.ok) {
        const data = await response.json();
        setScheduledPosts(data.posts || []);
      }
    } catch (error) {
      console.error('Error fetching scheduled posts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Schedule a new post
  const handleSchedulePost = async () => {
    if (!formData.content || !formData.scheduled_time) {
      alert('Please fill in all fields');
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
          content: formData.content,
          platform: formData.platform,
          scheduled_time: formData.scheduled_time
        }),
      });

      if (response.ok) {
        alert('Post scheduled successfully!');
        setFormData({ content: '', platform: 'twitter', scheduled_time: '' });
        setShowForm(false);
        fetchScheduledPosts();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to schedule post'}`);
      }
    } catch (error) {
      console.error('Error scheduling post:', error);
      alert('Failed to schedule post. Please try again.');
    }
  };

  // Delete scheduled post
  const handleDeletePost = async (postId: string) => {
    if (!window.confirm('Are you sure you want to delete this scheduled post?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${getApiBaseUrl()}/api/v1/social/scheduled/${postId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });

      if (response.ok) {
        alert('Post deleted successfully!');
        fetchScheduledPosts();
      } else {
        alert('Failed to delete post');
      }
    } catch (error) {
      console.error('Error deleting post:', error);
      alert('Failed to delete post. Please try again.');
    }
  };

  useEffect(() => {
    fetchScheduledPosts();
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
            <Button
              onClick={() => setShowForm(!showForm)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Schedule New Post
            </Button>
          </div>
        </div>

        {/* Schedule Form */}
        {showForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Schedule New Post</h2>
            <div className="space-y-4">
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
              </div>

              <div className="flex space-x-3">
                <Button onClick={handleSchedulePost} className="bg-indigo-600 hover:bg-indigo-700">
                  <Send className="w-4 h-4 mr-2" />
                  Schedule Post
                </Button>
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
                          {new Date(post.scheduled_time).toLocaleString()}
                        </div>
                      </div>
                      {post.status === 'pending' && (
                        <Button
                          onClick={() => handleDeletePost(post.id)}
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulePostsPage;