import React, { useState } from 'react';
import { X, Users, Mail, Shield } from 'lucide-react';
import apiClient from '../../../services/api';

interface InviteTeamModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInvitationSent: () => void;
}

export const InviteTeamModal: React.FC<InviteTeamModalProps> = ({
  isOpen,
  onClose,
  onInvitationSent,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emails, setEmails] = useState<string>('');
  const [role, setRole] = useState<string>('member');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const emailList = emails.split(',').map(e => e.trim()).filter(e => e);

    if (emailList.length === 0) {
      setError("Please enter at least one email address");
      setLoading(false);
      return;
    }

    try {
      await apiClient.post('/api/v1/team/invite', {
        emails: emailList,
        role: role
      });
      onInvitationSent();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send invitations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-600" />
            Invite Team Members
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Addresses
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <textarea
                required
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="colleague@company.com, manager@company.com"
                rows={3}
                value={emails}
                onChange={e => setEmails(e.target.value)}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Separate multiple emails with commas
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setRole('member')}
                className={`p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors ${
                  role === 'member'
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Users className="w-5 h-5" />
                <span className="text-sm font-medium">Member</span>
              </button>
              <button
                type="button"
                onClick={() => setRole('admin')}
                className={`p-3 border rounded-lg flex flex-col items-center gap-2 transition-colors ${
                  role === 'admin'
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Shield className="w-5 h-5" />
                <span className="text-sm font-medium">Admin</span>
              </button>
            </div>
          </div>

          <div className="pt-4 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Invitations'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
