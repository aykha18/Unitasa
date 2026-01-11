import React, { useState, useEffect } from 'react';
import { Users, DollarSign, Calendar, TrendingUp, Mail, Phone, CheckCircle, Clock, Settings, User as UserIcon, Edit, Save, X } from 'lucide-react';
import PaymentTest from '../components/test/PaymentTest';
import config from '../config/environment';
import { useToast, ToastProvider } from '../hooks/useToast';
import Modal from '../components/ui/Modal';

interface DashboardStats {
  totalLeads: number;
  assessmentsCompleted: number;
  consultationsBooked: number;
  paymentsCompleted: number;
  totalRevenueUSD: number;
  totalRevenueINR: number;
  conversionRate: number;
}

interface Lead {
  id: number;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  crm_system?: string;
  assessment_score?: number;
  consultation_booked: boolean;
  payment_completed: boolean;
  created_at: string;
}

interface PricingPlan {
  id: number;
  name: string;
  display_name: string;
  price_usd: number;
  price_inr: number;
  features: string[];
  description: string;
  is_active: boolean;
}

interface User {
  id: number;
  email: string;
  full_name: string;
  subscription_tier: string;
  is_co_creator: boolean;
}

const AdminDashboardContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'plans' | 'users'>('overview');
  const [stats, setStats] = useState<DashboardStats>({
    totalLeads: 0,
    assessmentsCompleted: 0,
    consultationsBooked: 0,
    paymentsCompleted: 0,
    totalRevenueUSD: 0,
    totalRevenueINR: 0,
    conversionRate: 0,
  });
  
  const [leads, setLeads] = useState<Lead[]>([]);
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [editingPlan, setEditingPlan] = useState<PricingPlan | null>(null);
  const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);
  const [pendingUpgrade, setPendingUpgrade] = useState<{userId: number, planName: string} | null>(null);

  const { showSuccess, showError } = useToast();

  // Simple password protection (in production, use proper auth)
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Change this password to something secure
    if (password === 'unitasa2025') {
      setIsAuthenticated(true);
      fetchDashboardData();
    } else {
      showError('Incorrect password');
    }
  };

  const apiUrl = config.apiBaseUrl;

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch stats
      const statsResponse = await fetch(`${apiUrl}/api/v1/admin/stats`, {
        headers: { 'Authorization': `Bearer ${password}` },
      });
      if (statsResponse.ok) setStats(await statsResponse.json());

      // Fetch leads
      const leadsResponse = await fetch(`${apiUrl}/api/v1/admin/leads`, {
        headers: { 'Authorization': `Bearer ${password}` },
      });
      if (leadsResponse.ok) setLeads((await leadsResponse.json()).leads || []);

      // Fetch plans
      const plansResponse = await fetch(`${apiUrl}/api/v1/admin/plans`, {
        headers: { 'Authorization': `Bearer ${password}` },
      });
      if (plansResponse.ok) setPlans(await plansResponse.json());

      // Fetch users
      const usersResponse = await fetch(`${apiUrl}/api/v1/admin/users`, {
        headers: { 'Authorization': `Bearer ${password}` },
      });
      if (usersResponse.ok) setUsers(await usersResponse.json());

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePlan = async (plan: PricingPlan) => {
    try {
      const response = await fetch(`${apiUrl}/api/v1/admin/plans/${plan.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${password}`,
        },
        body: JSON.stringify({
          price_usd: plan.price_usd,
          price_inr: plan.price_inr,
          display_name: plan.display_name,
          description: plan.description,
        }),
      });

      if (response.ok) {
        setPlans(plans.map(p => p.id === plan.id ? plan : p));
        setEditingPlan(null);
        showSuccess('Plan updated successfully');
      } else {
        const errorData = await response.json().catch(() => ({}));
        showError('Failed to update plan', errorData.detail || 'Unknown error');
      }
    } catch (error) {
      console.error('Error updating plan:', error);
      showError('Error updating plan', 'Network or server error');
    }
  };

  const handleUpgradeUser = (userId: number, planName: string) => {
    setPendingUpgrade({ userId, planName });
    setUpgradeModalOpen(true);
  };

  const confirmUpgrade = async () => {
    if (!pendingUpgrade) return;
    
    const { userId, planName } = pendingUpgrade;

    try {
      const response = await fetch(`${apiUrl}/api/v1/admin/users/${userId}/upgrade?plan_name=${planName}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${password}`,
        },
      });

      if (response.ok) {
        setUsers(users.map(u => u.id === userId ? { ...u, subscription_tier: planName, is_co_creator: planName === 'co_creator' } : u));
        showSuccess('User plan upgraded successfully');
        setUpgradeModalOpen(false);
        setPendingUpgrade(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Upgrade failed:', response.status, errorData);
        showError('Failed to upgrade user', errorData.detail || `Status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error upgrading user:', error);
      showError('Error upgrading user', 'Network or server error');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter admin password"
              />
            </div>
            <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Login
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-2">Manage your platform</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-lg ${activeTab === 'overview' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('plans')}
              className={`px-4 py-2 rounded-lg ${activeTab === 'plans' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
            >
              Plan Manager
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-2 rounded-lg ${activeTab === 'users' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
            >
              User Management
            </button>
          </div>
        </div>

        {loading ? (
           <div className="p-8 text-center">
             <Clock className="w-8 h-8 text-gray-400 mx-auto mb-2 animate-spin" />
             <p className="text-gray-600">Loading data...</p>
           </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <StatCard icon={<Users className="w-8 h-8 text-blue-600" />} title="Total Leads" value={stats.totalLeads} bgColor="bg-blue-50" />
                  <StatCard icon={<CheckCircle className="w-8 h-8 text-green-600" />} title="Assessments" value={stats.assessmentsCompleted} bgColor="bg-green-50" />
                  <StatCard icon={<Calendar className="w-8 h-8 text-purple-600" />} title="Consultations" value={stats.consultationsBooked} bgColor="bg-purple-50" />
                  <StatCard icon={<DollarSign className="w-8 h-8 text-yellow-600" />} title="Payments" value={stats.paymentsCompleted} bgColor="bg-yellow-50" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                   <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Revenue (USD)</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">${stats.totalRevenueUSD.toLocaleString()}</p>
                      </div>
                      <TrendingUp className="w-12 h-12 text-green-600" />
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Revenue (INR)</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">₹{stats.totalRevenueINR.toLocaleString()}</p>
                      </div>
                      <TrendingUp className="w-12 h-12 text-green-600" />
                    </div>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Conversion Rate</p>
                        <p className="text-3xl font-bold text-gray-900 mt-2">{stats.conversionRate.toFixed(1)}%</p>
                      </div>
                      <TrendingUp className="w-12 h-12 text-blue-600" />
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-xl font-bold text-gray-900">Recent Leads</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead Info</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CRM</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {leads.map((lead) => (
                          <tr key={lead.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                                <div className="text-sm text-gray-500">{lead.email}</div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{lead.crm_system || 'N/A'}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{lead.assessment_score}%</td>
                            <td className="px-6 py-4 whitespace-nowrap">
                               <span className={`px-2 py-1 text-xs font-medium rounded ${lead.payment_completed ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                 {lead.payment_completed ? 'Paid' : 'New'}
                               </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(lead.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                
                <div className="mt-8">
                  <PaymentTest />
                </div>
              </>
            )}

            {activeTab === 'plans' && (
              <div className="grid grid-cols-1 gap-6">
                {plans.map((plan) => (
                  <div key={plan.id} className="bg-white rounded-lg shadow p-6">
                    {editingPlan?.id === plan.id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                           <div>
                             <label className="block text-sm font-medium text-gray-700">Display Name</label>
                             <input 
                               type="text" 
                               value={editingPlan.display_name} 
                               onChange={e => setEditingPlan({...editingPlan, display_name: e.target.value})}
                               className="mt-1 w-full border rounded px-3 py-2"
                             />
                           </div>
                           <div>
                             <label className="block text-sm font-medium text-gray-700">Description</label>
                             <input 
                               type="text" 
                               value={editingPlan.description} 
                               onChange={e => setEditingPlan({...editingPlan, description: e.target.value})}
                               className="mt-1 w-full border rounded px-3 py-2"
                             />
                           </div>
                           <div>
                             <label className="block text-sm font-medium text-gray-700">Price (USD)</label>
                             <input 
                               type="number" 
                               value={editingPlan.price_usd} 
                               onChange={e => setEditingPlan({...editingPlan, price_usd: parseFloat(e.target.value)})}
                               className="mt-1 w-full border rounded px-3 py-2"
                             />
                           </div>
                           <div>
                             <label className="block text-sm font-medium text-gray-700">Price (INR)</label>
                             <input 
                               type="number" 
                               value={editingPlan.price_inr} 
                               onChange={e => setEditingPlan({...editingPlan, price_inr: parseFloat(e.target.value)})}
                               className="mt-1 w-full border rounded px-3 py-2"
                             />
                           </div>
                        </div>
                        <div className="flex justify-end gap-2">
                          <button onClick={() => setEditingPlan(null)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
                          <button onClick={() => handleUpdatePlan(editingPlan)} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Changes</button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center gap-2">
                             <h3 className="text-xl font-bold text-gray-900">{plan.display_name}</h3>
                             <span className="text-sm text-gray-500">({plan.name})</span>
                             {plan.is_active ? <span className="text-green-600 text-xs bg-green-100 px-2 py-1 rounded">Active</span> : <span className="text-red-600 text-xs bg-red-100 px-2 py-1 rounded">Inactive</span>}
                          </div>
                          <p className="text-gray-600 mt-1">{plan.description}</p>
                          <div className="flex gap-4 mt-2">
                            <span className="font-semibold text-green-700">₹{plan.price_inr.toLocaleString()}</span>
                            <span className="font-semibold text-blue-700">${plan.price_usd.toLocaleString()}</span>
                          </div>
                        </div>
                        <button onClick={() => setEditingPlan(plan)} className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded">
                          <Edit className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'users' && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                 <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Plan</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {users.map((user) => (
                          <tr key={user.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                                <div className="text-sm text-gray-500">{user.email}</div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                               <span className={`px-2 py-1 text-xs font-medium rounded ${user.subscription_tier === 'co_creator' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                                 {user.subscription_tier || 'free'}
                               </span>
                               {user.is_co_creator && <span className="ml-2 text-xs text-purple-600">✨ Co-Creator</span>}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                               <select 
                                 className="text-sm border rounded px-2 py-1 mr-2"
                                 value=""
                                 onChange={(e) => {
                                   if (e.target.value) handleUpgradeUser(user.id, e.target.value);
                                 }}
                               >
                                 <option value="">Change Plan...</option>
                                 {plans.map(p => (
                                   <option key={p.id} value={p.name}>{p.display_name}</option>
                                 ))}
                               </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
              </div>
            )}
          </>
        )}
      </div>
      <Modal
        isOpen={upgradeModalOpen}
        onClose={() => {
          setUpgradeModalOpen(false);
          setPendingUpgrade(null);
        }}
        title="Confirm Plan Upgrade"
        footer={
          <>
            <button
              onClick={() => {
                setUpgradeModalOpen(false);
                setPendingUpgrade(null);
              }}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={confirmUpgrade}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Confirm Upgrade
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Are you sure you want to upgrade this user?
          </p>
          {pendingUpgrade && (
            <div className="bg-blue-50 p-4 rounded-md">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Target Plan:</span> {plans.find(p => p.name === pendingUpgrade.planName)?.display_name || pendingUpgrade.planName}
              </p>
            </div>
          )}
          <p className="text-sm text-gray-500">
            This action will immediately update the user's subscription tier and access rights.
          </p>
        </div>
      </Modal>
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: number;
  bgColor: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value, bgColor }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`${bgColor} p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
      
    </div>
  );
};

const AdminDashboard: React.FC = () => {
  return (
    <ToastProvider>
      <AdminDashboardContent />
    </ToastProvider>
  );
};

export default AdminDashboard;
