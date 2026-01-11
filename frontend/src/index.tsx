import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import * as serviceWorker from './utils/serviceWorker';
import { AuthProvider } from './context/AuthContext';
import { ConfirmProvider } from './context/ConfirmContext';

// Global error handler for Chrome extension and other async errors (disabled to prevent reload loop)
// window.addEventListener('error', (event) => {
//   // Suppress Chrome extension errors that don't affect our app
//   if (event.message && event.message.includes('Extension context invalidated')) {
//     event.preventDefault();
//     return false;
//   }
// });

// Handle unhandled promise rejections (disabled to prevent reload loop)
// window.addEventListener('unhandledrejection', (event) => {
//   // Suppress Chrome extension promise rejections
//   if (event.reason && event.reason.message && 
//       (event.reason.message.includes('Extension context invalidated') ||
//        event.reason.message.includes('message channel closed'))) {
//     event.preventDefault();
//     return false;
//   }
// });

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <AuthProvider>
    <ConfirmProvider>
      <App />
    </ConfirmProvider>
  </AuthProvider>
);

// Register service worker for PWA features
serviceWorker.register({
  onSuccess: () => {
    console.log('Unitasa is now available offline!');
  },
  onUpdate: () => {
    console.log('New version available! Please refresh to update.');
  }
});

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
