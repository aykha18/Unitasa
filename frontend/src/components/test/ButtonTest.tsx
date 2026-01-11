import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import Button from '../ui/Button';
import RazorpayCheckout from '../payment/RazorpayCheckout';

const ButtonTest: React.FC = () => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [clickCount, setClickCount] = useState(0);

  const handleButtonClick = () => {
    console.log('🎯 Button clicked! Count:', clickCount + 1);
    setClickCount(prev => prev + 1);
    setShowPaymentModal(true);
    toast('Button clicked! Opening payment modal...', { icon: '👆' });
  };

  return (
    <div style={{ padding: '20px', background: '#f0f0f0', margin: '20px', borderRadius: '8px' }}>
      <h2>🧪 Button Test Component</h2>
      <p>Click count: {clickCount}</p>
      <p>Payment modal open: {showPaymentModal ? 'Yes' : 'No'}</p>
      
      <Button 
        onClick={handleButtonClick}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg"
      >
        🎯 Test Secure Founding Spot Button
      </Button>
      
      <Button 
        onClick={() => {
          console.log('Simple button clicked');
          toast('Simple button works!', { icon: '✅' });
        }}
        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg ml-4"
      >
        ✅ Simple Test Button
      </Button>

      {/* Payment Modal */}
      {showPaymentModal && !paymentSuccess && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
        >
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', maxWidth: '400px' }}>
            <h3>🎉 Payment Modal Opened!</h3>
            <p>This confirms the button click is working.</p>
            <RazorpayCheckout
              onSuccess={(paymentData) => {
                console.log('Payment successful:', paymentData);
                setPaymentSuccess(true);
                setShowPaymentModal(false);
                toast.success(`🎉 Payment successful! Transaction ID: ${paymentData.transactionId}`);
              }}
              onError={(error) => {
                console.error('Payment error:', error);
                toast.error(`❌ Payment failed: ${error}`);
                setShowPaymentModal(false);
              }}
              onCancel={() => {
                setShowPaymentModal(false);
                console.log('Payment cancelled');
              }}
              customerEmail="test@example.com"
              customerName="Test User"
            />
            <Button 
              onClick={() => setShowPaymentModal(false)}
              className="mt-4 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            >
              Close Test Modal
            </Button>
          </div>
        </div>
      )}

      {/* Success State */}
      {paymentSuccess && (
        <div style={{ background: '#d4edda', padding: '15px', margin: '10px 0', borderRadius: '5px', color: '#155724' }}>
          ✅ Payment completed successfully!
        </div>
      )}
    </div>
  );
};

export default ButtonTest;