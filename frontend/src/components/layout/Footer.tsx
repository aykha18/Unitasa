import React from 'react';
import { Zap, Mail, Linkedin, Twitter } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Unitasa</h3>
                <p className="text-sm text-gray-400">Unified Marketing Intelligence Platform</p>
              </div>
            </div>
            <p className="text-gray-400 mb-4 max-w-md">
              One platform. Unified marketing. The only AI marketing intelligence you'll ever need - 
              replacing fragmented tools with complete marketing unity.
            </p>
            <div className="flex space-x-4">
              <a href="mailto:support@unitasa.in" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
              <a href="https://linkedin.com/company/unitasa" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="https://twitter.com/unitasa" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li>
                <a 
                  href="/" 
                  className="hover:text-white transition-colors"
                  onClick={(e) => {
                    if (window.location.pathname === '/') {
                      e.preventDefault();
                      document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                >
                  Features
                </a>
              </li>
              <li>
                <a 
                  href="/" 
                  className="hover:text-white transition-colors"
                  onClick={(e) => {
                    if (window.location.pathname === '/') {
                      e.preventDefault();
                      document.getElementById('integrations')?.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                >
                  Integrations
                </a>
              </li>
              <li>
                <a
                  href="/"
                  className="hover:text-white transition-colors cursor-pointer"
                  onClick={(e) => {
                    e.preventDefault();
                    if (window.location.pathname !== '/') {
                      window.location.href = '/';
                    }
                    setTimeout(() => {
                      window.dispatchEvent(new CustomEvent('openLeadCapture'));
                    }, 100);
                  }}
                >
                  AI Assessment
                </a>
              </li>
              <li>
                <a 
                  href="/" 
                  className="hover:text-white transition-colors"
                  onClick={(e) => {
                    if (window.location.pathname === '/') {
                      e.preventDefault();
                      document.getElementById('co-creator')?.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                >
                  Co-Creator Program
                </a>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li>
                <a 
                  href="/contact" 
                  className="hover:text-white transition-colors"
                  onClick={(e) => {
                    e.preventDefault();
                    window.history.pushState({}, '', '/contact');
                    window.dispatchEvent(new PopStateEvent('popstate'));
                  }}
                >
                  Contact Us
                </a>
              </li>
              <li><a href="mailto:support@unitasa.com" className="hover:text-white transition-colors">Email Support</a></li>
              <li><a href="tel:+919768584622" className="hover:text-white transition-colors">Phone Support</a></li>
              <li>
                <a 
                  href="/refund-policy" 
                  className="hover:text-white transition-colors"
                  onClick={(e) => {
                    e.preventDefault();
                    window.history.pushState({}, '', '/refund-policy');
                    window.dispatchEvent(new PopStateEvent('popstate'));
                  }}
                >
                  Refund Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center gap-4">
            <p className="text-gray-400 text-sm">
              © 2025 Unitasa. All rights reserved.
            </p>
            <button
              onClick={() => {
                window.history.pushState({}, '', '/admin');
                window.dispatchEvent(new PopStateEvent('popstate'));
              }}
              className="text-gray-600 hover:text-gray-400 text-xs transition-colors"
              title="Admin Dashboard"
            >
              •
            </button>
          </div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a 
              href="/privacy-policy" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
              onClick={(e) => {
                e.preventDefault();
                window.history.pushState({}, '', '/privacy-policy');
                window.dispatchEvent(new PopStateEvent('popstate'));
              }}
            >
              Privacy Policy
            </a>
            <a 
              href="/terms-of-service" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
              onClick={(e) => {
                e.preventDefault();
                window.history.pushState({}, '', '/terms-of-service');
                window.dispatchEvent(new PopStateEvent('popstate'));
              }}
            >
              Terms of Service
            </a>
            <a 
              href="/refund-policy" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
              onClick={(e) => {
                e.preventDefault();
                window.history.pushState({}, '', '/refund-policy');
                window.dispatchEvent(new PopStateEvent('popstate'));
              }}
            >
              Refund Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
