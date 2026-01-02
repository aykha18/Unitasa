import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui';
import { ArrowLeft, User, CreditCard, Shield, Bell } from 'lucide-react';
import DashboardHeader from './Dashboard/components/DashboardHeader';

const SettingsPage: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  // Custom navigation function
  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new Event('navigate'));
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

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader user={user} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center">
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

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Settings Sidebar */}
          <div className="space-y-1">
            <button className="w-full flex items-center px-4 py-3 bg-white text-primary-600 border-l-4 border-primary-600 shadow-sm font-medium">
              <User className="w-5 h-5 mr-3" />
              Profile
            </button>
            <button className="w-full flex items-center px-4 py-3 bg-white text-gray-600 hover:bg-gray-50 shadow-sm font-medium transition-colors">
              <CreditCard className="w-5 h-5 mr-3" />
              Billing & Subscription
            </button>
            <button className="w-full flex items-center px-4 py-3 bg-white text-gray-600 hover:bg-gray-50 shadow-sm font-medium transition-colors">
              <Shield className="w-5 h-5 mr-3" />
              Security
            </button>
            <button className="w-full flex items-center px-4 py-3 bg-white text-gray-600 hover:bg-gray-50 shadow-sm font-medium transition-colors">
              <Bell className="w-5 h-5 mr-3" />
              Notifications
            </button>
          </div>

          {/* Settings Content */}
          <div className="md:col-span-3 space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-6">Profile Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    defaultValue={user.first_name || ''}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    disabled
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    defaultValue={user.last_name || ''}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    disabled
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    defaultValue={user.email || ''}
                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                    disabled
                  />
                </div>
              </div>
              
              <div className="mt-6 flex justify-end">
                <Button variant="primary">
                  Save Changes
                </Button>
              </div>
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-6">Preferences</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                    <p className="text-sm text-gray-500">Receive emails about your campaign progress</p>
                  </div>
                  <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                    <input type="checkbox" name="toggle" id="toggle" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                    <label htmlFor="toggle" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
