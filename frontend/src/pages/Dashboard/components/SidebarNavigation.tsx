import React, { useState } from 'react';
import {
  BarChart3,
  Users,
  Share2,
  Settings,
  Home,
  TrendingUp,
  MessageSquare,
  Calendar,
  Menu,
  X
} from 'lucide-react';

interface SidebarNavigationProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
}

const SidebarNavigation: React.FC<SidebarNavigationProps> = ({
  activeModule,
  onModuleChange
}) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const modules = [
    {
      id: 'business',
      label: 'Business',
      icon: Home,
      description: 'Main dashboard & analytics'
    },
    {
      id: 'social',
      label: 'Social Media',
      icon: Share2,
      description: 'Social media management'
    }
  ];

  const handleModuleChange = (moduleId: string) => {
    onModuleChange(moduleId);
    setIsMobileOpen(false); // Close mobile menu after selection
  };

  const sidebarContent = (
    <>
      {/* Navigation Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Dashboard</h2>
            <p className="text-sm text-gray-600 mt-1">Manage your business</p>
          </div>
          {/* Mobile close button */}
          <button
            onClick={() => setIsMobileOpen(false)}
            className="md:hidden p-1 rounded-md text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {modules.map((module) => {
            const Icon = module.icon;
            const isActive = activeModule === module.id;

            return (
              <button
                key={module.id}
                onClick={() => handleModuleChange(module.id)}
                className={`w-full flex items-center px-3 py-3 rounded-lg text-left transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
                <div>
                  <div className="font-medium text-sm">{module.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{module.description}</div>
                </div>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Unitasa v1.0
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="p-2 bg-white rounded-md shadow-md text-gray-600 hover:text-gray-900"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-white border-r border-gray-200 flex flex-col
        transform transition-transform duration-300 ease-in-out
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {sidebarContent}
      </div>
    </>
  );
};

export default SidebarNavigation;