import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui';
import { 
  ArrowLeft, 
  User, 
  CreditCard, 
  Shield, 
  Bell, 
  Check, 
  Zap, 
  Crown,
  AlertCircle
} from 'lucide-react';
import DashboardHeader from './Dashboard/components/DashboardHeader';
import { pricingService, PricingPlan } from '../services/pricingService';

type TabType = 'profile' | 'billing' | 'security' | 'notifications';

const SettingsPage: React.FC = () => {
  const { user, isAuthenticated, isLoading, updateProfile, changePassword } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [saveStatus, setSaveStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });
  const [isSaving, setIsSaving] = useState(false);
  
  // Pricing Plans State
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(false);

  // Profile Form State
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    company: ''
  });

  // Password Form State
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        company: user.company || ''
      });
    }
  }, [user]);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoadingPlans(true);
        const data = await pricingService.getAllPlans();
        setPlans(data);
      } catch (error) {
        console.error('Failed to load plans', error);
      } finally {
        setLoadingPlans(false);
      }
    };

    if (activeTab === 'billing') {
      fetchPlans();
    }
  }, [activeTab]);

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveStatus({ type: null, message: '' });

    try {
      const success = await updateProfile(profileData);
      if (success) {
        setSaveStatus({ type: 'success', message: 'Profile updated successfully' });
      } else {
        setSaveStatus({ type: 'error', message: 'Failed to update profile' });
      }
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'An unexpected error occurred' });
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setSaveStatus({ type: 'error', message: 'New passwords do not match' });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setSaveStatus({ type: 'error', message: 'Password must be at least 8 characters' });
      return;
    }

    setIsSaving(true);
    setSaveStatus({ type: null, message: '' });

    try {
      const success = await changePassword(passwordData.current_password, passwordData.new_password);
      if (success) {
        setSaveStatus({ type: 'success', message: 'Password changed successfully' });
        setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      } else {
        setSaveStatus({ type: 'error', message: 'Failed to change password. Please check your current password.' });
      }
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'An unexpected error occurred' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    navigate('/login');
    return null;
  }

  const getPlanName = (tier: string) => {
    switch (tier) {
      case 'co_creator': return 'Co-Creator';
      case 'enterprise': return 'Enterprise';
      case 'pro': return 'Pro';
      case 'free_trial': return 'Free Trial';
      default: return 'Free Plan';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader user={user} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/dashboard')}
              className="mr-4 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Settings Sidebar */}
          <div className="space-y-1">
            <button 
              onClick={() => { setActiveTab('profile'); setSaveStatus({ type: null, message: '' }); }}
              className={`w-full flex items-center px-4 py-3 shadow-sm font-medium transition-colors ${
                activeTab === 'profile' 
                  ? 'bg-white text-primary-600 border-l-4 border-primary-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
              }`}
            >
              <User className="w-5 h-5 mr-3" />
              Profile
            </button>
            <button 
              onClick={() => { setActiveTab('billing'); setSaveStatus({ type: null, message: '' }); }}
              className={`w-full flex items-center px-4 py-3 shadow-sm font-medium transition-colors ${
                activeTab === 'billing' 
                  ? 'bg-white text-primary-600 border-l-4 border-primary-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
              }`}
            >
              <CreditCard className="w-5 h-5 mr-3" />
              Billing & Subscription
            </button>
            <button 
              onClick={() => { setActiveTab('security'); setSaveStatus({ type: null, message: '' }); }}
              className={`w-full flex items-center px-4 py-3 shadow-sm font-medium transition-colors ${
                activeTab === 'security' 
                  ? 'bg-white text-primary-600 border-l-4 border-primary-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
              }`}
            >
              <Shield className="w-5 h-5 mr-3" />
              Security
            </button>
            <button 
              onClick={() => { setActiveTab('notifications'); setSaveStatus({ type: null, message: '' }); }}
              className={`w-full flex items-center px-4 py-3 shadow-sm font-medium transition-colors ${
                activeTab === 'notifications' 
                  ? 'bg-white text-primary-600 border-l-4 border-primary-600' 
                  : 'bg-white text-gray-600 hover:bg-gray-50 border-l-4 border-transparent'
              }`}
            >
              <Bell className="w-5 h-5 mr-3" />
              Notifications
            </button>
          </div>

          {/* Settings Content */}
          <div className="md:col-span-3 space-y-6">
            
            {saveStatus.message && (
              <div className={`p-4 rounded-md ${saveStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                <div className="flex">
                  <div className="flex-shrink-0">
                    {saveStatus.type === 'success' ? (
                      <Check className="h-5 w-5 text-green-400" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-400" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium">{saveStatus.message}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-6">Profile Information</h2>
                <form onSubmit={handleProfileSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        First Name
                      </label>
                      <input
                        type="text"
                        value={profileData.first_name}
                        onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Last Name
                      </label>
                      <input
                        type="text"
                        value={profileData.last_name}
                        onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Company Name
                      </label>
                      <input
                        type="text"
                        value={profileData.company}
                        onChange={(e) => setProfileData({...profileData, company: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email Address
                      </label>
                      <input
                        type="email"
                        value={user.email}
                        disabled
                        className="w-full border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                      <p className="mt-1 text-xs text-gray-500">Email cannot be changed directly.</p>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex justify-end">
                    <Button variant="primary" type="submit" disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && (
              <div className="space-y-6">
                {/* Current Plan Card */}
                <div className="bg-white shadow rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-medium text-gray-900">Current Plan</h2>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      user.is_co_creator 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {getPlanName(user.subscription_tier)}
                    </span>
                  </div>
                  
                  <div className="border-t border-gray-200 pt-4">
                    <div className="flex items-center justify-between py-2">
                      <span className="text-gray-600">Status</span>
                      <span className="text-gray-900 font-medium">Active</span>
                    </div>
                    {user.trial_end_date && !user.is_co_creator && (
                      <div className="flex items-center justify-between py-2">
                        <span className="text-gray-600">Trial Ends</span>
                        <span className="text-gray-900 font-medium">
                          {new Date(user.trial_end_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Upgrade Options */}
                {!user.is_co_creator && (
                  <>
                    {loadingPlans ? (
                      <div className="animate-pulse bg-gray-200 h-64 rounded-lg mb-6"></div>
                    ) : plans.find(p => p.name === 'co_creator') ? (
                      (() => {
                        const plan = plans.find(p => p.name === 'co_creator')!;
                        return (
                          <div className="bg-gradient-to-br from-purple-600 to-indigo-700 rounded-lg shadow-lg p-6 text-white mb-6">
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="flex items-center mb-2">
                                  <Crown className="w-6 h-6 mr-2 text-yellow-300" />
                                  <h3 className="text-xl font-bold">{plan.display_name}</h3>
                                </div>
                                <p className="text-purple-100 mb-4 max-w-lg">
                                  {plan.description || 'Join our exclusive founding member program. Get lifetime access, influence our roadmap, and enjoy priority support.'}
                                </p>
                                <div className="space-y-2 mb-6">
                                  {(plan.features || [
                                    'Lifetime access (No monthly fees)',
                                    'Priority integration support',
                                    'Direct founder access'
                                  ]).map((feature, idx) => (
                                    <div key={idx} className="flex items-center text-sm">
                                      <Check className="w-4 h-4 mr-2 text-green-300" />
                                      {feature}
                                    </div>
                                  ))}
                                </div>
                              </div>
                              <div className="hidden md:block">
                                <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                                  <div className="text-center">
                                    <div className="text-xs uppercase tracking-wide text-purple-200">Limited Time</div>
                                    <div className="text-3xl font-bold text-white mt-1">
                                      {pricingService.formatPrice(plan.price_inr, 'INR')}
                                    </div>
                                    <div className="text-xs text-purple-200 mt-1">one-time payment</div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            <Button 
                              className="w-full sm:w-auto bg-white text-purple-700 hover:bg-gray-100 font-semibold border-none"
                              onClick={() => navigate('/co-creator')}
                            >
                              View Program Details
                            </Button>
                          </div>
                        );
                      })()
                    ) : (
                      // Fallback if API fails or plan not found
                      <div className="bg-gradient-to-br from-purple-600 to-indigo-700 rounded-lg shadow-lg p-6 text-white mb-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center mb-2">
                              <Crown className="w-6 h-6 mr-2 text-yellow-300" />
                              <h3 className="text-xl font-bold">Become a Co-Creator</h3>
                            </div>
                            <p className="text-purple-100 mb-4 max-w-lg">
                              Join our exclusive founding member program. Get lifetime access, influence our roadmap, and enjoy priority support.
                            </p>
                            <div className="space-y-2 mb-6">
                              <div className="flex items-center text-sm">
                                <Check className="w-4 h-4 mr-2 text-green-300" />
                                Lifetime access (No monthly fees)
                              </div>
                              <div className="flex items-center text-sm">
                                <Check className="w-4 h-4 mr-2 text-green-300" />
                                Priority integration support
                              </div>
                              <div className="flex items-center text-sm">
                                <Check className="w-4 h-4 mr-2 text-green-300" />
                                Direct founder access
                              </div>
                            </div>
                          </div>
                          <div className="hidden md:block">
                            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                              <div className="text-center">
                                <div className="text-xs uppercase tracking-wide text-purple-200">Limited Time</div>
                                <div className="text-3xl font-bold text-white mt-1">{pricingService.formatPrice(29999, 'INR')}</div>
                                <div className="text-xs text-purple-200 mt-1">one-time payment</div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <Button 
                          className="w-full sm:w-auto bg-white text-purple-700 hover:bg-gray-100 font-semibold border-none"
                          onClick={() => navigate('/co-creator')}
                        >
                          View Program Details
                        </Button>
                      </div>
                    )}
                  </>
                )}
                
                {/* Other Plans */}
                {user.subscription_tier !== 'co_creator' && !user.is_co_creator && (
                  plans.length > 0 ? (
                    plans
                      .filter(p => p.name !== 'co_creator' && p.name !== 'free' && p.name !== 'free_trial' && p.name !== user.subscription_tier)
                      .map(plan => (
                        <div key={plan.id} className="bg-white shadow rounded-lg p-6 border border-gray-200 mb-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center mb-2">
                                <Zap className="w-5 h-5 mr-2 text-blue-600" />
                                <h3 className="text-lg font-bold text-gray-900">{plan.display_name}</h3>
                              </div>
                              <p className="text-gray-600 text-sm mb-2">
                                {plan.description}
                              </p>
                              <div className="text-sm font-semibold text-gray-900">
                                {pricingService.formatPrice(plan.price_inr, 'INR')}
                              </div>
                            </div>
                            <Button 
                              variant="outline"
                              onClick={() => toast.success(`Upgrade to ${plan.display_name} coming soon! Check out our Co-Creator program for the best value.`, { icon: '🚀' })}
                          >
                            Upgrade to {plan.display_name}
                            </Button>
                          </div>
                        </div>
                      ))
                  ) : (
                    // Fallback if plans not loaded
                     <div className="bg-white shadow rounded-lg p-6 border border-gray-200">
                       <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center mb-2">
                              <Zap className="w-5 h-5 mr-2 text-blue-600" />
                              <h3 className="text-lg font-bold text-gray-900">Pro Plan</h3>
                            </div>
                            <p className="text-gray-600 text-sm">
                              For growing businesses needing more power.
                            </p>
                          </div>
                          <Button 
                            variant="outline"
                            onClick={() => toast.success("Pro plan upgrade coming soon! Check out our Co-Creator program for the best value.", { icon: '🚀' })}
                        >
                          Upgrade to Pro
                          </Button>
                       </div>
                     </div>
                  )
                )}
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-6">Security Settings</h2>
                <form onSubmit={handlePasswordSubmit}>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Current Password
                      </label>
                      <input
                        type="password"
                        required
                        value={passwordData.current_password}
                        onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        New Password
                      </label>
                      <input
                        type="password"
                        required
                        minLength={8}
                        value={passwordData.new_password}
                        onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                      <p className="mt-1 text-xs text-gray-500">Must be at least 8 characters long.</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        required
                        minLength={8}
                        value={passwordData.confirm_password}
                        onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                        className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-6 flex justify-end">
                    <Button variant="primary" type="submit" disabled={isSaving}>
                      {isSaving ? 'Updating...' : 'Update Password'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-6">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-gray-100">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                      <p className="text-sm text-gray-500">Receive emails about your campaign progress</p>
                    </div>
                    <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                      <input type="checkbox" defaultChecked name="toggle" id="toggle1" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                      <label htmlFor="toggle1" className="toggle-label block overflow-hidden h-6 rounded-full bg-primary-600 cursor-pointer"></label>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between py-3 border-b border-gray-100">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Weekly Reports</h3>
                      <p className="text-sm text-gray-500">Receive a weekly summary of your performance</p>
                    </div>
                    <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                      <input type="checkbox" defaultChecked name="toggle" id="toggle2" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                      <label htmlFor="toggle2" className="toggle-label block overflow-hidden h-6 rounded-full bg-primary-600 cursor-pointer"></label>
                    </div>
                  </div>

                  <div className="flex items-center justify-between py-3">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Marketing Updates</h3>
                      <p className="text-sm text-gray-500">Receive news about new features and updates</p>
                    </div>
                    <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                      <input type="checkbox" name="toggle" id="toggle3" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                      <label htmlFor="toggle3" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 flex justify-end">
                   <Button variant="outline" onClick={() => setSaveStatus({ type: 'success', message: 'Preferences saved (simulated)' })}>
                     Save Preferences
                   </Button>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </main>
      
      <style>{`
        .toggle-checkbox:checked {
          right: 0;
          border-color: #68D391;
        }
        .toggle-checkbox:checked + .toggle-label {
          background-color: #68D391;
        }
        .toggle-checkbox {
            right: 0;
            z-index: 1;
            border-color: #CBD5E0;
            transition: all 0.3s;
        }
        .toggle-label {
            width: 2.5rem;
            height: 1.5rem;
        }
        .toggle-checkbox:checked {
            right: 0;
            border-color: #4F46E5;
        }
        .toggle-checkbox:checked + .toggle-label {
            background-color: #4F46E5;
        }
      `}</style>
    </div>
  );
};

export default SettingsPage;
