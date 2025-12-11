import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { Button } from '../ui';
import PWAInstallButton from '../ui/PWAInstallButton';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <img
              src="/logo.svg"
              alt="Unitasa Logo"
              className="h-10 w-auto"
            />
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-unitasa-gray hover:text-unitasa-electric transition-colors font-medium">
              Features
            </a>
            <a href="#integrations" className="text-unitasa-gray hover:text-unitasa-electric transition-colors font-medium">
              Integrations
            </a>
            <a
              href="#assessment"
              className="text-unitasa-gray hover:text-unitasa-electric transition-colors font-medium cursor-pointer"
              onClick={(e) => {
                e.preventDefault();
                // Dispatch event to trigger lead capture flow
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }}
            >
              Assessment
            </a>
            <a href="#story" className="text-unitasa-gray hover:text-unitasa-electric transition-colors font-medium">
              Our Story
            </a>
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <PWAInstallButton className="text-xs" />
            <Button
              variant="outline"
              size="sm"
              className="border-unitasa-electric text-unitasa-electric hover:bg-unitasa-electric hover:text-white"
              onClick={() => {
                window.dispatchEvent(new CustomEvent('openLeadCapture'));
              }}
            >
              Take Assessment
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-unitasa-gray hover:text-unitasa-blue"
              onClick={() => {
                window.history.pushState({}, '', '/login');
                window.dispatchEvent(new Event('navigate'));
              }}
            >
              Sign In
            </Button>
            <Button
              size="sm"
              className="bg-gradient-primary text-white hover:shadow-brand"
              onClick={() => {
                window.history.pushState({}, '', '/signup');
                window.dispatchEvent(new Event('navigate'));
              }}
            >
              Start Free Trial
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-700 hover:text-primary-600 transition-colors"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              <a
                href="#features"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Features
              </a>
              <a
                href="#integrations"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Integrations
              </a>
              <a
                href="#assessment"
                className="text-gray-700 hover:text-primary-600 transition-colors cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  toggleMenu();
                  window.dispatchEvent(new CustomEvent('openAssessment'));
                }}
              >
                Assessment
              </a>
              <a
                href="#story"
                className="text-gray-700 hover:text-primary-600 transition-colors"
                onClick={toggleMenu}
              >
                Our Story
              </a>
              <div className="pt-4 border-t border-gray-200 space-y-2">
                <PWAInstallButton className="w-full text-sm" />
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    toggleMenu();
                    window.dispatchEvent(new CustomEvent('openLeadCapture'));
                  }}
                >
                  Take Assessment
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-gray-700 hover:text-primary-600"
                  onClick={() => {
                    toggleMenu();
                    window.history.pushState({}, '', '/login');
                    window.dispatchEvent(new Event('navigate'));
                  }}
                >
                  Sign In
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    toggleMenu();
                    window.history.pushState({}, '', '/signup');
                    window.dispatchEvent(new Event('navigate'));
                  }}
                >
                  Start Free Trial
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
