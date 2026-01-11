import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import Button from '../ui/Button';

const SimplePaymentTest: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [clickCount, setClickCount] = useState(0);

  const handleClick = () => {
    console.log('🎯 BUTTON CLICKED!', new Date().toISOString());
    setClickCount(prev => prev + 1);
    setShowModal(true);
    
    // Show toast to confirm click is working
    toast.success(`Button clicked ${clickCount + 1} times! Modal should open.`);
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      padding: '20px', 
      border: '2px solid #3b82f6',
      borderRadius: '8px',
      zIndex: 9999,
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
    }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#3b82f6' }}>🧪 Button Test</h3>
      <p style={{ margin: '0 0 10px 0', fontSize: '14px' }}>
        Clicks: {clickCount} | Modal: {showModal ? 'Open' : 'Closed'}
      </p>
      
      <Button 
        onClick={handleClick}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-2"
      >
        🎯 Test Secure Founding Spot
      </Button>
      
      <br />
      
      <button 
        onClick={() => {
          console.log('Native button clicked');
          toast('Native HTML button works!', { icon: '✅' });
        }}
        style={{
          background: '#22c55e',
          color: 'white',
          padding: '8px 16px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        ✅ Native Button Test
      </button>

      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            maxWidth: '400px'
          }}>
            <h2 style={{ color: '#22c55e', marginBottom: '15px' }}>🎉 Success!</h2>
            <p>Button click is working! This confirms the onClick handler is functioning.</p>
            <p><strong>Click count:</strong> {clickCount}</p>
            
            <button 
              onClick={() => setShowModal(false)}
              style={{
                background: '#3b82f6',
                color: 'white',
                padding: '10px 20px',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginTop: '15px'
              }}
            >
              Close Modal
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimplePaymentTest;